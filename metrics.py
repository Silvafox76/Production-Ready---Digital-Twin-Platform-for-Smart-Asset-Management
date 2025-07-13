"""
Metrics Collection for Digital Twin Platform
Prometheus metrics for monitoring and observability
"""
import time
from functools import wraps
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse

# Application Info
app_info = Info('digital_twin_app', 'Digital Twin Platform Application Info')
app_info.info({
    'version': '1.0.0',
    'name': 'digital-twin-platform',
    'description': 'Smart Asset Management Platform'
})

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed'
)

# WebSocket Metrics
websocket_connections_total = Counter(
    'websocket_connections_total',
    'Total number of WebSocket connections',
    ['status']  # connected, disconnected
)

websocket_connections_active = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

websocket_messages_total = Counter(
    'websocket_messages_total',
    'Total number of WebSocket messages',
    ['direction', 'message_type']  # sent/received, telemetry/alert/etc
)

# MQTT Metrics
mqtt_messages_total = Counter(
    'mqtt_messages_total',
    'Total number of MQTT messages',
    ['topic_type', 'status']  # telemetry/alerts/status, success/error
)

mqtt_messages_processing_duration_seconds = Histogram(
    'mqtt_messages_processing_duration_seconds',
    'MQTT message processing duration in seconds',
    ['topic_type']
)

mqtt_connection_status = Gauge(
    'mqtt_connection_status',
    'MQTT connection status (1=connected, 0=disconnected)'
)

# Database Metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

database_query_duration_seconds = Histogram(
    'database_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table']
)

database_queries_total = Counter(
    'database_queries_total',
    'Total number of database queries',
    ['operation', 'table', 'status']
)

# Asset Metrics
assets_total = Gauge(
    'assets_total',
    'Total number of assets',
    ['asset_type', 'status']
)

telemetry_data_points_total = Counter(
    'telemetry_data_points_total',
    'Total number of telemetry data points received',
    ['asset_id', 'metric_type']
)

telemetry_processing_duration_seconds = Histogram(
    'telemetry_processing_duration_seconds',
    'Telemetry data processing duration in seconds',
    ['asset_id']
)

# Alert Metrics
alerts_total = Counter(
    'alerts_total',
    'Total number of alerts generated',
    ['asset_id', 'alert_type', 'severity']
)

alerts_active = Gauge(
    'alerts_active',
    'Number of active alerts',
    ['severity']
)

# ML Metrics
ml_predictions_total = Counter(
    'ml_predictions_total',
    'Total number of ML predictions made',
    ['model_name', 'asset_type']
)

ml_prediction_duration_seconds = Histogram(
    'ml_prediction_duration_seconds',
    'ML prediction duration in seconds',
    ['model_name']
)

ml_model_accuracy = Gauge(
    'ml_model_accuracy',
    'ML model accuracy score',
    ['model_name']
)

# System Metrics
system_uptime_seconds = Gauge(
    'system_uptime_seconds',
    'System uptime in seconds'
)

memory_usage_bytes = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['type']  # rss, vms, shared
)

cpu_usage_percent = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage'
)

# Business Metrics
energy_consumption_total = Counter(
    'energy_consumption_total',
    'Total energy consumption',
    ['asset_id', 'unit']
)

maintenance_events_total = Counter(
    'maintenance_events_total',
    'Total number of maintenance events',
    ['asset_id', 'event_type']
)

downtime_duration_seconds = Histogram(
    'downtime_duration_seconds',
    'Asset downtime duration in seconds',
    ['asset_id', 'reason']
)

# Decorators for automatic metrics collection
def track_http_requests(func):
    """Decorator to track HTTP request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            return await func(*args, **kwargs)
        
        method = request.method
        endpoint = request.url.path
        
        http_requests_in_progress.inc()
        start_time = time.time()
        
        try:
            response = await func(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()
            
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error metrics
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()
            
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
            raise
        finally:
            http_requests_in_progress.dec()
    
    return wrapper

def track_database_queries(operation: str, table: str):
    """Decorator to track database query metrics"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success metrics
                database_queries_total.labels(
                    operation=operation,
                    table=table,
                    status='success'
                ).inc()
                
                duration = time.time() - start_time
                database_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
                
                return result
                
            except Exception as e:
                # Record error metrics
                database_queries_total.labels(
                    operation=operation,
                    table=table,
                    status='error'
                ).inc()
                
                duration = time.time() - start_time
                database_query_duration_seconds.labels(
                    operation=operation,
                    table=table
                ).observe(duration)
                
                raise
        
        return wrapper
    return decorator

def track_ml_predictions(model_name: str, asset_type: str = None):
    """Decorator to track ML prediction metrics"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record prediction metrics
                ml_predictions_total.labels(
                    model_name=model_name,
                    asset_type=asset_type or 'unknown'
                ).inc()
                
                duration = time.time() - start_time
                ml_prediction_duration_seconds.labels(
                    model_name=model_name
                ).observe(duration)
                
                return result
                
            except Exception as e:
                # Still record the attempt
                duration = time.time() - start_time
                ml_prediction_duration_seconds.labels(
                    model_name=model_name
                ).observe(duration)
                
                raise
        
        return wrapper
    return decorator

# Utility functions for metrics updates
def update_websocket_connections(action: str):
    """Update WebSocket connection metrics"""
    if action == 'connect':
        websocket_connections_total.labels(status='connected').inc()
        websocket_connections_active.inc()
    elif action == 'disconnect':
        websocket_connections_total.labels(status='disconnected').inc()
        websocket_connections_active.dec()

def record_websocket_message(direction: str, message_type: str):
    """Record WebSocket message metrics"""
    websocket_messages_total.labels(
        direction=direction,
        message_type=message_type
    ).inc()

def update_mqtt_connection_status(connected: bool):
    """Update MQTT connection status"""
    mqtt_connection_status.set(1 if connected else 0)

def record_mqtt_message(topic_type: str, status: str, processing_time: float = None):
    """Record MQTT message metrics"""
    mqtt_messages_total.labels(
        topic_type=topic_type,
        status=status
    ).inc()
    
    if processing_time is not None:
        mqtt_messages_processing_duration_seconds.labels(
            topic_type=topic_type
        ).observe(processing_time)

def update_asset_count(asset_type: str, status: str, count: int):
    """Update asset count metrics"""
    assets_total.labels(
        asset_type=asset_type,
        status=status
    ).set(count)

def record_telemetry_data(asset_id: str, metric_type: str, processing_time: float = None):
    """Record telemetry data metrics"""
    telemetry_data_points_total.labels(
        asset_id=asset_id,
        metric_type=metric_type
    ).inc()
    
    if processing_time is not None:
        telemetry_processing_duration_seconds.labels(
            asset_id=asset_id
        ).observe(processing_time)

def record_alert(asset_id: str, alert_type: str, severity: str):
    """Record alert metrics"""
    alerts_total.labels(
        asset_id=asset_id,
        alert_type=alert_type,
        severity=severity
    ).inc()

def update_active_alerts(severity: str, count: int):
    """Update active alert count"""
    alerts_active.labels(severity=severity).set(count)

def update_system_metrics(uptime: float, memory_usage: Dict[str, int], cpu_percent: float):
    """Update system metrics"""
    system_uptime_seconds.set(uptime)
    cpu_usage_percent.set(cpu_percent)
    
    for mem_type, usage in memory_usage.items():
        memory_usage_bytes.labels(type=mem_type).set(usage)

def record_energy_consumption(asset_id: str, amount: float, unit: str = 'kwh'):
    """Record energy consumption"""
    energy_consumption_total.labels(
        asset_id=asset_id,
        unit=unit
    ).inc(amount)

def record_maintenance_event(asset_id: str, event_type: str):
    """Record maintenance event"""
    maintenance_events_total.labels(
        asset_id=asset_id,
        event_type=event_type
    ).inc()

def record_downtime(asset_id: str, duration: float, reason: str):
    """Record asset downtime"""
    downtime_duration_seconds.labels(
        asset_id=asset_id,
        reason=reason
    ).observe(duration)

# FastAPI endpoint for metrics
async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Middleware for automatic HTTP metrics collection
class MetricsMiddleware:
    """Middleware to automatically collect HTTP metrics"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        method = request.method
        path = request.url.path
        
        # Skip metrics endpoint to avoid recursion
        if path == "/metrics":
            await self.app(scope, receive, send)
            return
        
        http_requests_in_progress.inc()
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                
                # Record metrics
                http_requests_total.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).inc()
                
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
                
                http_requests_in_progress.dec()
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            # Record error and re-raise
            http_requests_total.labels(
                method=method,
                endpoint=path,
                status_code=500
            ).inc()
            
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            http_requests_in_progress.dec()
            raise

