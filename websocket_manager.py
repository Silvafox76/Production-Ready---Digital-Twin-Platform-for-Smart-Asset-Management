"""
WebSocket Manager for Real-time Data Broadcasting
"""
import asyncio
import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time data broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.asset_subscribers: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection established. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        # Remove from asset subscriptions
        for asset_id, subscribers in self.asset_subscribers.items():
            if websocket in subscribers:
                subscribers.remove(websocket)
                
        logger.info(f"WebSocket connection closed. Total: {len(self.active_connections)}")
        
    async def subscribe_to_asset(self, websocket: WebSocket, asset_id: str):
        """Subscribe a WebSocket to specific asset updates"""
        if asset_id not in self.asset_subscribers:
            self.asset_subscribers[asset_id] = set()
        self.asset_subscribers[asset_id].add(websocket)
        logger.info(f"WebSocket subscribed to asset {asset_id}")
        
    async def unsubscribe_from_asset(self, websocket: WebSocket, asset_id: str):
        """Unsubscribe a WebSocket from specific asset updates"""
        if asset_id in self.asset_subscribers and websocket in self.asset_subscribers[asset_id]:
            self.asset_subscribers[asset_id].remove(websocket)
            logger.info(f"WebSocket unsubscribed from asset {asset_id}")
            
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected WebSockets"""
        if not self.active_connections:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)
                
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
            
    async def broadcast_to_asset_subscribers(self, asset_id: str, message: dict):
        """Broadcast a message to subscribers of a specific asset"""
        if asset_id not in self.asset_subscribers:
            return
            
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.asset_subscribers[asset_id].copy():
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending asset message to WebSocket: {e}")
                disconnected.append(connection)
                
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
            
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

# Global connection manager instance
manager = ConnectionManager()

class TelemetryBroadcaster:
    """Handles broadcasting of telemetry data to WebSocket clients"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        
    async def broadcast_telemetry(self, asset_id: str, telemetry_data: dict):
        """Broadcast telemetry data for a specific asset"""
        message = {
            "type": "telemetry",
            "asset_id": asset_id,
            "data": telemetry_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all connections
        await self.manager.broadcast_to_all(message)
        
        # Also broadcast to asset-specific subscribers
        await self.manager.broadcast_to_asset_subscribers(asset_id, message)
        
    async def broadcast_alert(self, asset_id: str, alert_data: dict):
        """Broadcast alert for a specific asset"""
        message = {
            "type": "alert",
            "asset_id": asset_id,
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast_to_all(message)
        
    async def broadcast_asset_status(self, asset_id: str, status: str, details: dict = None):
        """Broadcast asset status change"""
        message = {
            "type": "asset_status",
            "asset_id": asset_id,
            "status": status,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast_to_all(message)
        
    async def broadcast_system_status(self, status_data: dict):
        """Broadcast system-wide status updates"""
        message = {
            "type": "system_status",
            "data": status_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.manager.broadcast_to_all(message)

# Global broadcaster instance
broadcaster = TelemetryBroadcaster(manager)

async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint handler"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, message: dict):
    """Handle incoming WebSocket messages from clients"""
    message_type = message.get("type")
    
    if message_type == "subscribe":
        asset_id = message.get("asset_id")
        if asset_id:
            await manager.subscribe_to_asset(websocket, asset_id)
            await manager.send_personal_message({
                "type": "subscription_confirmed",
                "asset_id": asset_id
            }, websocket)
            
    elif message_type == "unsubscribe":
        asset_id = message.get("asset_id")
        if asset_id:
            await manager.unsubscribe_from_asset(websocket, asset_id)
            await manager.send_personal_message({
                "type": "unsubscription_confirmed",
                "asset_id": asset_id
            }, websocket)
            
    elif message_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }, websocket)
        
    else:
        await manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, websocket)

