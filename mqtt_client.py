"""
MQTT Client for Digital Twin Platform
Handles connection to MQTT broker and message processing
"""
import asyncio
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

import structlog
from asyncio_mqtt import Client, MqttError
from pydantic import ValidationError

from models.telemetry import TelemetryCreate

logger = structlog.get_logger()

class MQTTClient:
    """MQTT Client for handling IoT device communications"""
    
    def __init__(self):
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
        self.username = os.getenv("MQTT_USERNAME")
        self.password = os.getenv("MQTT_PASSWORD")
        self.client_id = os.getenv("MQTT_CLIENT_ID", "digital-twin-platform")
        
        self.client: Optional[Client] = None
        self.telemetry_queue = asyncio.Queue()
        self.is_connected = False
        
        # Topic configuration
        self.telemetry_topic = "dt/telemetry/+"  # Wildcard for all assets
        self.command_topic = "dt/commands/"
        self.status_topic = "dt/status/"
        
        logger.info("MQTT Client initialized", 
                   broker=f"{self.broker_host}:{self.broker_port}")
    
    async def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client = Client(
                hostname=self.broker_host,
                port=self.broker_port,
                username=self.username,
                password=self.password,
                client_id=self.client_id,
                keepalive=60
            )
            
            await self.client.__aenter__()
            self.is_connected = True
            
            # Start message processing task
            asyncio.create_task(self._message_handler())
            
            # Subscribe to telemetry topics
            await self.client.subscribe(self.telemetry_topic)
            
            logger.info("MQTT Client connected successfully")
            
        except MqttError as e:
            logger.error("Failed to connect to MQTT broker", error=str(e))
            self.is_connected = False
            raise
        except Exception as e:
            logger.error("Unexpected error connecting to MQTT", error=str(e))
            self.is_connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.is_connected:
            try:
                await self.client.__aexit__(None, None, None)
                self.is_connected = False
                logger.info("MQTT Client disconnected")
            except Exception as e:
                logger.error("Error disconnecting MQTT client", error=str(e))
    
    async def _message_handler(self):
        """Handle incoming MQTT messages"""
        if not self.client:
            return
        
        logger.info("Starting MQTT message handler")
        
        try:
            async with self.client.messages() as messages:
                async for message in messages:
                    await self._process_message(message)
        except Exception as e:
            logger.error("Error in MQTT message handler", error=str(e))
    
    async def _process_message(self, message):
        """Process individual MQTT message"""
        try:
            topic = message.topic.value
            payload = message.payload.decode()
            
            logger.debug("Received MQTT message", topic=topic, payload=payload)
            
            # Parse telemetry messages
            if topic.startswith("dt/telemetry/"):
                await self._process_telemetry_message(topic, payload)
            elif topic.startswith("dt/status/"):
                await self._process_status_message(topic, payload)
            else:
                logger.warning("Unknown topic", topic=topic)
                
        except Exception as e:
            logger.error("Error processing MQTT message", error=str(e))
    
    async def _process_telemetry_message(self, topic: str, payload: str):
        """Process telemetry message"""
        try:
            # Extract asset ID from topic (dt/telemetry/asset_id)
            asset_id = topic.split("/")[-1]
            
            # Parse JSON payload
            data = json.loads(payload)
            
            # Create telemetry object
            telemetry = TelemetryCreate(
                asset_id=asset_id,
                timestamp=datetime.fromisoformat(data.get("timestamp", datetime.utcnow().isoformat())),
                temperature=data.get("temperature"),
                humidity=data.get("humidity"),
                pressure=data.get("pressure"),
                vibration=data.get("vibration"),
                power_consumption=data.get("power_consumption"),
                status=data.get("status", "online"),
                metadata=data.get("metadata", {})
            )
            
            # Add to processing queue
            await self.telemetry_queue.put(telemetry)
            
            logger.debug("Telemetry queued for processing", asset_id=asset_id)
            
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in telemetry message", error=str(e), payload=payload)
        except ValidationError as e:
            logger.error("Invalid telemetry data", error=str(e), payload=payload)
        except Exception as e:
            logger.error("Error processing telemetry message", error=str(e))
    
    async def _process_status_message(self, topic: str, payload: str):
        """Process status message"""
        try:
            asset_id = topic.split("/")[-1]
            data = json.loads(payload)
            
            logger.info("Asset status update", 
                       asset_id=asset_id, 
                       status=data.get("status"),
                       timestamp=data.get("timestamp"))
            
        except Exception as e:
            logger.error("Error processing status message", error=str(e))
    
    async def publish_command(self, asset_id: str, command: Dict[str, Any]):
        """Publish command to asset"""
        if not self.client or not self.is_connected:
            logger.error("MQTT client not connected")
            return False
        
        try:
            topic = f"{self.command_topic}{asset_id}"
            payload = json.dumps(command)
            
            await self.client.publish(topic, payload)
            
            logger.info("Command published", asset_id=asset_id, command=command)
            return True
            
        except Exception as e:
            logger.error("Failed to publish command", asset_id=asset_id, error=str(e))
            return False
    
    async def publish_status(self, asset_id: str, status: Dict[str, Any]):
        """Publish status update"""
        if not self.client or not self.is_connected:
            logger.error("MQTT client not connected")
            return False
        
        try:
            topic = f"{self.status_topic}{asset_id}"
            payload = json.dumps({
                **status,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            await self.client.publish(topic, payload)
            
            logger.debug("Status published", asset_id=asset_id)
            return True
            
        except Exception as e:
            logger.error("Failed to publish status", asset_id=asset_id, error=str(e))
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status"""
        return {
            "connected": self.is_connected,
            "broker": f"{self.broker_host}:{self.broker_port}",
            "client_id": self.client_id,
            "queue_size": self.telemetry_queue.qsize()
        }

