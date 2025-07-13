"""
Digital Twin Platform - Main FastAPI Application
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import structlog
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from mqtt_client import MQTTClient
from models.asset import Asset, AssetCreate, AssetUpdate
from models.telemetry import TelemetryData, TelemetryCreate
from db.database import DatabaseManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global instances
mqtt_client: Optional[MQTTClient] = None
db_manager: Optional[DatabaseManager] = None
websocket_connections: List[WebSocket] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global mqtt_client, db_manager
    
    logger.info("Starting Digital Twin Platform...")
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    # Initialize MQTT client
    mqtt_client = MQTTClient()
    await mqtt_client.connect()
    
    # Start background tasks
    asyncio.create_task(telemetry_processor())
    
    logger.info("Digital Twin Platform started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Digital Twin Platform...")
    if mqtt_client:
        await mqtt_client.disconnect()
    if db_manager:
        await db_manager.close()
    logger.info("Digital Twin Platform shut down complete")

# Create FastAPI app
app = FastAPI(
    title="Digital Twin Platform API",
    description="Production-ready Digital Twin Platform for Smart Asset Management",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

class AssetListResponse(BaseModel):
    assets: List[Asset]
    total: int

class TelemetryResponse(BaseModel):
    data: List[TelemetryData]
    asset_id: str
    count: int

# API Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/api/v1/assets", response_model=AssetListResponse)
async def get_assets(skip: int = 0, limit: int = 100):
    """Get all assets with pagination"""
    try:
        assets = await db_manager.get_assets(skip=skip, limit=limit)
        total = await db_manager.count_assets()
        return AssetListResponse(assets=assets, total=total)
    except Exception as e:
        logger.error("Failed to get assets", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve assets")

@app.post("/api/v1/assets", response_model=Asset)
async def create_asset(asset: AssetCreate):
    """Create a new asset"""
    try:
        new_asset = await db_manager.create_asset(asset)
        logger.info("Asset created", asset_id=new_asset.id, name=new_asset.name)
        return new_asset
    except Exception as e:
        logger.error("Failed to create asset", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create asset")

@app.get("/api/v1/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str):
    """Get asset by ID"""
    try:
        asset = await db_manager.get_asset(asset_id)
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        return asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get asset", asset_id=asset_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve asset")

@app.put("/api/v1/assets/{asset_id}", response_model=Asset)
async def update_asset(asset_id: str, asset_update: AssetUpdate):
    """Update asset by ID"""
    try:
        updated_asset = await db_manager.update_asset(asset_id, asset_update)
        if not updated_asset:
            raise HTTPException(status_code=404, detail="Asset not found")
        logger.info("Asset updated", asset_id=asset_id)
        return updated_asset
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update asset", asset_id=asset_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update asset")

@app.delete("/api/v1/assets/{asset_id}")
async def delete_asset(asset_id: str):
    """Delete asset by ID"""
    try:
        success = await db_manager.delete_asset(asset_id)
        if not success:
            raise HTTPException(status_code=404, detail="Asset not found")
        logger.info("Asset deleted", asset_id=asset_id)
        return {"message": "Asset deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete asset", asset_id=asset_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete asset")

@app.get("/api/v1/assets/{asset_id}/telemetry", response_model=TelemetryResponse)
async def get_asset_telemetry(
    asset_id: str, 
    limit: int = 100, 
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
):
    """Get telemetry data for an asset"""
    try:
        telemetry_data = await db_manager.get_telemetry(
            asset_id=asset_id,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        return TelemetryResponse(
            data=telemetry_data,
            asset_id=asset_id,
            count=len(telemetry_data)
        )
    except Exception as e:
        logger.error("Failed to get telemetry", asset_id=asset_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve telemetry data")

@app.post("/api/v1/telemetry")
async def create_telemetry(telemetry: TelemetryCreate):
    """Create new telemetry data point"""
    try:
        new_telemetry = await db_manager.create_telemetry(telemetry)
        
        # Broadcast to WebSocket connections
        await broadcast_telemetry(new_telemetry)
        
        logger.info("Telemetry created", asset_id=telemetry.asset_id)
        return new_telemetry
    except Exception as e:
        logger.error("Failed to create telemetry", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create telemetry data")

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry data"""
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        logger.info("WebSocket connection closed")

async def broadcast_telemetry(telemetry_data: TelemetryData):
    """Broadcast telemetry data to all WebSocket connections"""
    if not websocket_connections:
        return
    
    message = {
        "type": "telemetry",
        "data": telemetry_data.dict()
    }
    
    # Remove disconnected connections
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_json(message)
        except:
            disconnected.append(websocket)
    
    for ws in disconnected:
        websocket_connections.remove(ws)

async def telemetry_processor():
    """Background task to process incoming telemetry data"""
    logger.info("Starting telemetry processor")
    
    while True:
        try:
            # Process any queued telemetry data from MQTT
            if mqtt_client and mqtt_client.telemetry_queue:
                while not mqtt_client.telemetry_queue.empty():
                    telemetry_data = await mqtt_client.telemetry_queue.get()
                    
                    # Store in database
                    await db_manager.create_telemetry(telemetry_data)
                    
                    # Broadcast to WebSocket connections
                    await broadcast_telemetry(telemetry_data)
                    
                    logger.debug("Processed telemetry", asset_id=telemetry_data.asset_id)
            
            await asyncio.sleep(1)  # Process every second
            
        except Exception as e:
            logger.error("Error in telemetry processor", error=str(e))
            await asyncio.sleep(5)  # Wait longer on error

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "production") == "development",
        log_level="info"
    )

