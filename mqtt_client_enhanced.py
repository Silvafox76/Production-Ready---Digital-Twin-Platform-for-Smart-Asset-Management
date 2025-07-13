"""
Enhanced MQTT Client for Digital Twin Platform
With real-time data processing and WebSocket broadcasting
"""
import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import paho.mqtt.client as mqtt
from websocket_manager import broadcaster
from db.database import DatabaseManager

logger = logging.getLogger(__name__)

class EnhancedMQTTClient:
    """Enhanced MQTT Client for real-time telemetry data ingestion"""
    
    def __init__(self, 
                 broker_host: str = "localhost",
                 broker_port: int = 1883,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 client_id: Optional[str] = None):
        
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client_id = client_id or f"digital_twin_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # MQTT client setup
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        
        # Connection state
        self.is_connected = False
        self.subscribed_topics = set()
        
        # Statistics
        self.stats = {
            "messages_received": 0,
            "messages_processed": 0,
            "errors": 0,
            "last_message_time": None
        }
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server"""
        if rc == 0:
            self.is_connected = True
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.subscribe_to_default_topics()
        else:
            self.is_connected = False
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the server"""
        self.is_connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker. Return code: {rc}")
        else:
            logger.info("Disconnected from MQTT broker")
            
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback for when the client receives a SUBACK response from the server"""
        logger.info(f"Subscribed to topic with message ID: {mid}, QoS: {granted_qos}")
        
    def _on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server"""
        try:
            self.stats["messages_received"] += 1
            self.stats["last_message_time"] = datetime.utcnow()
            
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug(f"Received message on topic '{topic}': {payload}")
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON payload: {e}")
                self.stats["errors"] += 1
                return
                
            # Route message to appropriate handler
            asyncio.create_task(self._route_message(topic, data))
            
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
            self.stats["errors"] += 1
            
    async def _route_message(self, topic: str, data: dict):
        """Route incoming messages to appropriate handlers"""
        try:
            # Determine message type from topic
            topic_parts = topic.split('/')
            
            if "telemetry" in topic:
                await self._handle_telemetry_message(topic, data)
            elif "alerts" in topic:
                await self._handle_alert_message(topic, data)
            elif "status" in topic:
                await self._handle_status_message(topic, data)
            elif "commands" in topic:
                await self._handle_command_message(topic, data)
            else:
                logger.warning(f"Unknown topic pattern: {topic}")
                
            self.stats["messages_processed"] += 1
            
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            self.stats["errors"] += 1
            
    async def _handle_telemetry_message(self, topic: str, data: dict):
        """Handle telemetry data messages"""
        try:
            # Extract asset ID from topic (e.g., "assets/telemetry/asset_123")
            topic_parts = topic.split('/')
            if len(topic_parts) >= 3:
                asset_id = topic_parts[2]
            else:
                asset_id = data.get('asset_id', 'unknown')
                
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()
                
            # Broadcast to WebSocket clients
            await broadcaster.broadcast_telemetry(asset_id, data)
            
            # Check for alerts based on thresholds
            await self._check_telemetry_alerts(asset_id, data)
            
            logger.debug(f"Processed telemetry data for asset {asset_id}")
            
        except Exception as e:
            logger.error(f"Error handling telemetry message: {e}")
            
    async def _handle_alert_message(self, topic: str, data: dict):
        """Handle alert messages"""
        try:
            topic_parts = topic.split('/')
            if len(topic_parts) >= 3:
                asset_id = topic_parts[2]
            else:
                asset_id = data.get('asset_id', 'unknown')
                
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()
                
            # Broadcast alert to WebSocket clients
            await broadcaster.broadcast_alert(asset_id, data)
            
            logger.info(f"Processed alert for asset {asset_id}: {data.get('message', 'Unknown alert')}")
            
        except Exception as e:
            logger.error(f"Error handling alert message: {e}")
            
    async def _handle_status_message(self, topic: str, data: dict):
        """Handle asset status messages"""
        try:
            topic_parts = topic.split('/')
            if len(topic_parts) >= 3:
                asset_id = topic_parts[2]
            else:
                asset_id = data.get('asset_id', 'unknown')
                
            status = data.get('status', 'unknown')
            
            # Broadcast status change to WebSocket clients
            await broadcaster.broadcast_asset_status(asset_id, status, data)
            
            logger.info(f"Updated status for asset {asset_id}: {status}")
            
        except Exception as e:
            logger.error(f"Error handling status message: {e}")
            
    async def _handle_command_message(self, topic: str, data: dict):
        """Handle command messages"""
        try:
            command_type = data.get('command_type', 'unknown')
            asset_id = data.get('asset_id', 'unknown')
            
            logger.info(f"Received command confirmation for asset {asset_id}: {command_type}")
            
        except Exception as e:
            logger.error(f"Error handling command message: {e}")
            
    async def _check_telemetry_alerts(self, asset_id: str, data: dict):
        """Check telemetry data against alert thresholds"""
        try:
            # Define default thresholds
            thresholds = {
                'temperature': {'min': 15, 'max': 30},
                'humidity': {'min': 30, 'max': 70},
                'pressure': {'min': 95, 'max': 110},
                'vibration': {'max': 1.0},
                'power_consumption': {'max': 25}
            }
            
            alerts = []
            
            for metric, value in data.items():
                if metric in thresholds and isinstance(value, (int, float)):
                    threshold = thresholds[metric]
                    
                    if 'min' in threshold and value < threshold['min']:
                        alerts.append({
                            'type': 'threshold_violation',
                            'metric': metric,
                            'value': value,
                            'threshold': threshold['min'],
                            'condition': 'below_minimum',
                            'severity': 'warning'
                        })
                        
                    if 'max' in threshold and value > threshold['max']:
                        alerts.append({
                            'type': 'threshold_violation',
                            'metric': metric,
                            'value': value,
                            'threshold': threshold['max'],
                            'condition': 'above_maximum',
                            'severity': 'warning' if value < threshold['max'] * 1.2 else 'critical'
                        })
            
            # Send alerts if any violations found
            for alert in alerts:
                alert_data = {
                    'asset_id': asset_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    **alert
                }
                await broadcaster.broadcast_alert(asset_id, alert_data)
                
        except Exception as e:
            logger.error(f"Error checking telemetry alerts: {e}")
            
    def connect(self):
        """Connect to the MQTT broker"""
        try:
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
                
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # Start the network loop in a separate thread
            self.client.loop_start()
            
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
            raise
            
    def disconnect(self):
        """Disconnect from the MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
            
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
            
    def subscribe_to_default_topics(self):
        """Subscribe to default topics for the digital twin platform"""
        default_topics = [
            "assets/telemetry/+",      # All asset telemetry
            "assets/alerts/+",         # All asset alerts
            "assets/status/+",         # All asset status updates
            "assets/commands/+",       # All asset command confirmations
            "system/status",           # System-wide status
            "system/alerts"            # System-wide alerts
        ]
        
        for topic in default_topics:
            self.subscribe(topic)
            
    def subscribe(self, topic: str, qos: int = 0):
        """Subscribe to a specific topic"""
        try:
            result, mid = self.client.subscribe(topic, qos)
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.subscribed_topics.add(topic)
                logger.info(f"Subscribed to topic: {topic}")
            else:
                logger.error(f"Failed to subscribe to topic {topic}. Result: {result}")
                
        except Exception as e:
            logger.error(f"Error subscribing to topic {topic}: {e}")
            
    def publish(self, topic: str, payload: dict, qos: int = 0, retain: bool = False):
        """Publish a message to a topic"""
        try:
            payload_str = json.dumps(payload)
            result = self.client.publish(topic, payload_str, qos, retain)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published message to topic {topic}")
            else:
                logger.error(f"Failed to publish message to topic {topic}. Result: {result.rc}")
                
        except Exception as e:
            logger.error(f"Error publishing message to topic {topic}: {e}")
            
    def get_stats(self) -> dict:
        """Get MQTT client statistics"""
        return {
            **self.stats,
            "is_connected": self.is_connected,
            "subscribed_topics": list(self.subscribed_topics),
            "broker_host": self.broker_host,
            "broker_port": self.broker_port
        }

# Global enhanced MQTT client instance
enhanced_mqtt_client = None

def get_enhanced_mqtt_client() -> EnhancedMQTTClient:
    """Get the global enhanced MQTT client instance"""
    global enhanced_mqtt_client
    if enhanced_mqtt_client is None:
        # Get configuration from environment variables
        broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        username = os.getenv("MQTT_USERNAME")
        password = os.getenv("MQTT_PASSWORD")
        
        enhanced_mqtt_client = EnhancedMQTTClient(
            broker_host=broker_host,
            broker_port=broker_port,
            username=username,
            password=password
        )
        
    return enhanced_mqtt_client

