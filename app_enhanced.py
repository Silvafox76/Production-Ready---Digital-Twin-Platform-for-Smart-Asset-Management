"""
Digital Twin Platform - Enhanced FastAPI Application
With WebSocket support and real-time MQTT integration
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import models
from models.asset import Asset, AssetCreate, AssetUpdate
from models.telemetry import TelemetryData, TelemetryCreate

# Import database and MQTT clients
from db.database import DatabaseManager
from mqtt_client_enhanced import get_enhanced_mqtt_client
from websocket_manager import websocket_endpoint, manager, broadcaster

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
db_manager = None
mqtt_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Digital Twin Platform...")
    
    global db_manager, mqtt_client
    
    # Initialize database
    try:
        db_manager = DatabaseManager()
        await db_manager.initialize()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        
    # Initialize enhanced MQTT client
    try:
        mqtt_client = get_enhanced_mqtt_client()
        mqtt_client.connect()
        logger.info("Enhanced MQTT client connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect MQTT client: {e}")
        
    # Start background tasks
    asyncio.create_task(telemetry_simulator())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Digital Twin Platform...")
    
    if mqtt_client:
        mqtt_client.disconnect()
        
    if db_manager:
        await db_manager.close()

# Create FastAPI application
app = FastAPI(
    title="Digital Twin Platform API",
    description="Production-ready Digital Twin Platform for Smart Asset Management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "connected" if db_manager else "disconnected",
            "mqtt": "connected" if mqtt_client and mqtt_client.is_connected else "disconnected"
        }
    }

# WebSocket endpoint for real-time data
@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry data"""
    await websocket_endpoint(websocket)

# Asset Management Endpoints
@app.get("/api/v1/assets", response_model=dict)
async def get_assets(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    """Get all assets with pagination"""
    try:
        # Mock data for now - in production, this would query the database
        mock_assets = [
            {
                "id": f"asset_{i}",
                "name": f"HVAC Unit {i}",
                "description": f"Main HVAC system for building {i}",
                "asset_type": "hvac" if i % 3 == 0 else "pump" if i % 3 == 1 else "motor",
                "location": f"Building A, Floor {(i % 5) + 1}",
                "building": "Building A",
                "floor": f"Floor {(i % 5) + 1}",
                "room": f"Room {i * 10}",
                "manufacturer": "Siemens" if i % 2 == 0 else "Honeywell",
                "model": f"Model-{i}00X",
                "serial_number": f"SN{i:06d}",
                "status": "online" if i % 4 != 3 else "warning" if i % 4 == 3 else "error",
                "installation_date": "2023-01-15T00:00:00Z",
                "warranty_expiry": "2026-01-15T00:00:00Z",
                "last_seen": datetime.utcnow().isoformat(),
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": datetime.utcnow().isoformat()
            }
            for i in range(1, 21)  # Create 20 mock assets
        ]
        
        # Apply pagination
        paginated_assets = mock_assets[skip:skip + limit]
        
        return {
            "assets": paginated_assets,
            "total": len(mock_assets),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching assets: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/assets/{asset_id}", response_model=dict)
async def get_asset(asset_id: str):
    """Get a specific asset by ID"""
    try:
        # Mock data - in production, query database
        asset = {
            "id": asset_id,
            "name": f"Asset {asset_id}",
            "description": "Mock asset for demonstration",
            "asset_type": "hvac",
            "location": "Building A, Floor 1",
            "building": "Building A",
            "floor": "Floor 1",
            "room": "Room 101",
            "manufacturer": "Siemens",
            "model": "Model-100X",
            "serial_number": "SN000001",
            "status": "online",
            "installation_date": "2023-01-15T00:00:00Z",
            "warranty_expiry": "2026-01-15T00:00:00Z",
            "last_seen": datetime.utcnow().isoformat(),
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return asset
        
    except Exception as e:
        logger.error(f"Error fetching asset {asset_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/assets", response_model=dict)
async def create_asset(asset: AssetCreate):
    """Create a new asset"""
    try:
        # Mock creation - in production, save to database
        new_asset = {
            "id": f"asset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            **asset.dict(),
            "status": "offline",
            "last_seen": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Created new asset: {new_asset['id']}")
        return new_asset
        
    except Exception as e:
        logger.error(f"Error creating asset: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Telemetry Endpoints
@app.get("/api/v1/assets/{asset_id}/telemetry")
async def get_asset_telemetry(
    asset_id: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get telemetry data for a specific asset"""
    try:
        # Mock telemetry data
        from datetime import timedelta
        import random
        
        telemetry_data = []
        now = datetime.utcnow()
        
        for i in range(limit):
            timestamp = now - timedelta(hours=i)
            telemetry_data.append({
                "timestamp": timestamp.isoformat(),
                "asset_id": asset_id,
                "temperature": 22 + random.uniform(-3, 3),
                "humidity": 45 + random.uniform(-10, 10),
                "pressure": 102 + random.uniform(-2, 2),
                "vibration": 0.3 + random.uniform(-0.1, 0.1),
                "power_consumption": 12 + random.uniform(-2, 2),
                "status": "online"
            })
            
        return {
            "asset_id": asset_id,
            "telemetry": telemetry_data,
            "count": len(telemetry_data)
        }
        
    except Exception as e:
        logger.error(f"Error fetching telemetry for asset {asset_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/telemetry")
async def create_telemetry(telemetry: TelemetryCreate):
    """Create new telemetry data"""
    try:
        # Mock creation - in production, save to database and publish to MQTT
        telemetry_data = {
            "id": f"telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            **telemetry.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to WebSocket clients
        await broadcaster.broadcast_telemetry(telemetry.asset_id, telemetry_data)
        
        logger.info(f"Created telemetry data for asset: {telemetry.asset_id}")
        return telemetry_data
        
    except Exception as e:
        logger.error(f"Error creating telemetry: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# System Status Endpoints
@app.get("/api/v1/system/status")
async def get_system_status():
    """Get overall system status"""
    try:
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "operational",
            "services": {
                "api": "healthy",
                "database": "healthy" if db_manager else "unhealthy",
                "mqtt": "healthy" if mqtt_client and mqtt_client.is_connected else "unhealthy",
                "websocket": "healthy"
            },
            "metrics": {
                "active_connections": len(manager.active_connections),
                "mqtt_messages_received": mqtt_client.get_stats()["messages_received"] if mqtt_client else 0,
                "mqtt_messages_processed": mqtt_client.get_stats()["messages_processed"] if mqtt_client else 0
            }
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Background Tasks
async def telemetry_simulator():
    """Simulate telemetry data for demonstration"""
    import random
    
    while True:
        try:
            # Simulate telemetry for a few assets
            for asset_id in ["asset_1", "asset_2", "asset_3"]:
                telemetry_data = {
                    "asset_id": asset_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "temperature": 22 + random.uniform(-2, 2),
                    "humidity": 45 + random.uniform(-5, 5),
                    "pressure": 102 + random.uniform(-1, 1),
                    "vibration": 0.3 + random.uniform(-0.05, 0.05),
                    "power_consumption": 12 + random.uniform(-1, 1),
                    "status": "online"
                }
                
                # Broadcast to WebSocket clients
                await broadcaster.broadcast_telemetry(asset_id, telemetry_data)
                
            # Wait 30 seconds before next simulation
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in telemetry simulator: {e}")
            await asyncio.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Run the application
    uvicorn.run(
        "app_enhanced:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

