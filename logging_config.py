"""
Logging Configuration for Digital Twin Platform
"""
import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    enable_json_logging: bool = False,
    enable_structured_logging: bool = True
):
    """
    Setup logging configuration for the Digital Twin Platform
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_json_logging: Enable JSON formatted logging
        enable_structured_logging: Enable structured logging with additional context
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Default log file if not specified
    if log_file is None:
        log_file = log_dir / f"digital_twin_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Base logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "standard",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "detailed" if not enable_json_logging else "json",
                "filename": str(log_file),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed" if not enable_json_logging else "json",
                "filename": str(log_dir / "errors.log"),
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "file", "error_file"],
                "level": log_level,
                "propagate": False
            },
            "uvicorn": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "uvicorn.access": {
                "handlers": ["file"],
                "level": "INFO",
                "propagate": False
            },
            "fastapi": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False
            },
            "paho.mqtt": {
                "handlers": ["console", "file"],
                "level": "WARNING",
                "propagate": False
            },
            "sqlalchemy": {
                "handlers": ["file"],
                "level": "WARNING",
                "propagate": False
            }
        }
    }
    
    # Apply logging configuration
    logging.config.dictConfig(config)
    
    # Add custom logging context if structured logging is enabled
    if enable_structured_logging:
        setup_structured_logging()
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, File: {log_file}")
    
    return logger

def setup_structured_logging():
    """Setup structured logging with additional context"""
    
    class ContextFilter(logging.Filter):
        """Add context information to log records"""
        
        def filter(self, record):
            # Add application context
            record.app_name = "digital-twin-platform"
            record.app_version = "1.0.0"
            record.environment = os.getenv("ENVIRONMENT", "development")
            
            # Add request context if available (for web requests)
            try:
                from contextvars import ContextVar
                request_id = getattr(record, 'request_id', None)
                if request_id:
                    record.request_id = request_id
            except ImportError:
                pass
            
            return True
    
    # Add context filter to all handlers
    context_filter = ContextFilter()
    root_logger = logging.getLogger()
    
    for handler in root_logger.handlers:
        handler.addFilter(context_filter)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)

def log_performance(func):
    """Decorator to log function performance"""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    
    return wrapper

def log_api_request(func):
    """Decorator to log API requests"""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = get_logger("api")
        
        # Extract request information
        request = None
        for arg in args:
            if hasattr(arg, 'method') and hasattr(arg, 'url'):
                request = arg
                break
        
        if request:
            logger.info(f"API Request: {request.method} {request.url}")
        
        try:
            result = await func(*args, **kwargs)
            if request:
                logger.info(f"API Response: {request.method} {request.url} - Success")
            return result
        except Exception as e:
            if request:
                logger.error(f"API Response: {request.method} {request.url} - Error: {str(e)}")
            raise
    
    return wrapper

# Security logging functions
def log_security_event(event_type: str, details: dict, severity: str = "WARNING"):
    """Log security-related events"""
    logger = get_logger("security")
    
    log_message = f"Security Event: {event_type}"
    extra = {
        "event_type": event_type,
        "severity": severity,
        **details
    }
    
    if severity == "CRITICAL":
        logger.critical(log_message, extra=extra)
    elif severity == "ERROR":
        logger.error(log_message, extra=extra)
    elif severity == "WARNING":
        logger.warning(log_message, extra=extra)
    else:
        logger.info(log_message, extra=extra)

def log_authentication_attempt(username: str, success: bool, ip_address: str = None):
    """Log authentication attempts"""
    details = {
        "username": username,
        "success": success,
        "ip_address": ip_address or "unknown"
    }
    
    severity = "INFO" if success else "WARNING"
    event_type = "authentication_success" if success else "authentication_failure"
    
    log_security_event(event_type, details, severity)

def log_data_access(user: str, resource: str, action: str, success: bool):
    """Log data access events"""
    details = {
        "user": user,
        "resource": resource,
        "action": action,
        "success": success
    }
    
    severity = "INFO" if success else "WARNING"
    event_type = f"data_access_{action}"
    
    log_security_event(event_type, details, severity)

# Application-specific logging functions
def log_mqtt_event(event_type: str, topic: str, message: str = None, error: str = None):
    """Log MQTT-related events"""
    logger = get_logger("mqtt")
    
    log_data = {
        "event_type": event_type,
        "topic": topic
    }
    
    if message:
        log_data["message"] = message
    
    if error:
        logger.error(f"MQTT {event_type}: {topic} - Error: {error}", extra=log_data)
    else:
        logger.info(f"MQTT {event_type}: {topic}", extra=log_data)

def log_telemetry_data(asset_id: str, data_points: int, processing_time: float = None):
    """Log telemetry data processing"""
    logger = get_logger("telemetry")
    
    log_data = {
        "asset_id": asset_id,
        "data_points": data_points,
        "processing_time": processing_time
    }
    
    message = f"Processed {data_points} telemetry points for asset {asset_id}"
    if processing_time:
        message += f" in {processing_time:.4f} seconds"
    
    logger.info(message, extra=log_data)

def log_ml_prediction(asset_id: str, model_name: str, prediction: dict, confidence: float = None):
    """Log ML predictions"""
    logger = get_logger("ml")
    
    log_data = {
        "asset_id": asset_id,
        "model_name": model_name,
        "prediction": prediction,
        "confidence": confidence
    }
    
    message = f"ML Prediction for asset {asset_id} using {model_name}"
    if confidence:
        message += f" (confidence: {confidence:.2f})"
    
    logger.info(message, extra=log_data)

def log_alert_generated(asset_id: str, alert_type: str, severity: str, message: str):
    """Log alert generation"""
    logger = get_logger("alerts")
    
    log_data = {
        "asset_id": asset_id,
        "alert_type": alert_type,
        "severity": severity,
        "alert_message": message
    }
    
    log_message = f"Alert generated for asset {asset_id}: {alert_type} ({severity})"
    
    if severity.lower() == "critical":
        logger.critical(log_message, extra=log_data)
    elif severity.lower() == "warning":
        logger.warning(log_message, extra=log_data)
    else:
        logger.info(log_message, extra=log_data)

# Initialize logging on module import
if __name__ != "__main__":
    # Get configuration from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    enable_json_logging = os.getenv("JSON_LOGGING", "false").lower() == "true"
    
    setup_logging(
        log_level=log_level,
        enable_json_logging=enable_json_logging
    )

