"""
Configuration Management for Digital Twin Platform
"""
import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    app_name: str = "Digital Twin Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Security
    secret_key: str
    allowed_hosts: List[str] = ["*"]
    cors_origins: List[str] = ["*"]
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    
    # Redis
    redis_url: str
    redis_max_connections: int = 10
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    
    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_username: Optional[str] = None
    mqtt_password: Optional[str] = None
    mqtt_keepalive: int = 60
    mqtt_qos: int = 1
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    json_logging: bool = False
    structured_logging: bool = True
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    
    # ML Models
    ml_model_path: str = "/app/models"
    ml_inference_timeout: int = 30
    ml_batch_size: int = 100
    
    # File Storage
    upload_path: str = "/app/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".csv", ".json", ".txt"]
    
    # Email (Optional)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    email_from: str = "noreply@digitaltwin.com"
    
    # External APIs
    weather_api_key: Optional[str] = None
    maps_api_key: Optional[str] = None
    
    # Feature Flags
    enable_3d_visualization: bool = True
    enable_ml_predictions: bool = True
    enable_real_time_alerts: bool = True
    enable_data_export: bool = True
    
    # Performance
    request_timeout: int = 30
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Cache
    cache_ttl: int = 300  # 5 minutes
    cache_max_size: int = 1000
    
    # Background Tasks
    task_queue_max_size: int = 1000
    task_worker_count: int = 4
    task_retry_attempts: int = 3
    
    @validator("environment")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production", "testing"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("allowed_hosts", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    environment: str = "development"
    log_level: str = "DEBUG"
    workers: int = 1
    
    # Development database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/digital_twin_dev"
    redis_url: str = "redis://localhost:6379/0"
    
    # Relaxed security for development
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

class TestingSettings(Settings):
    """Testing environment settings"""
    environment: str = "testing"
    debug: bool = True
    log_level: str = "WARNING"
    
    # Test database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/digital_twin_test"
    redis_url: str = "redis://localhost:6379/1"
    
    # Disable external services in tests
    enable_metrics: bool = False
    smtp_host: Optional[str] = None

class ProductionSettings(Settings):
    """Production environment settings"""
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    json_logging: bool = True
    
    # Production security
    cors_origins: List[str] = []  # Must be explicitly set
    allowed_hosts: List[str] = []  # Must be explicitly set
    
    # Performance optimizations
    workers: int = 4
    database_pool_size: int = 20
    redis_max_connections: int = 20

@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)"""
    environment = os.getenv("ENVIRONMENT", "production").lower()
    
    if environment == "development":
        return DevelopmentSettings()
    elif environment == "testing":
        return TestingSettings()
    elif environment == "production":
        return ProductionSettings()
    else:
        return Settings()

# Global settings instance
settings = get_settings()

# Configuration validation
def validate_configuration():
    """Validate critical configuration settings"""
    errors = []
    
    # Check required settings
    if not settings.secret_key or settings.secret_key == "dev-secret-key-change-in-production":
        if settings.environment == "production":
            errors.append("SECRET_KEY must be set for production")
    
    if not settings.database_url:
        errors.append("DATABASE_URL is required")
    
    if not settings.redis_url:
        errors.append("REDIS_URL is required")
    
    # Check security settings for production
    if settings.environment == "production":
        if "*" in settings.cors_origins:
            errors.append("CORS_ORIGINS should not include '*' in production")
        
        if "*" in settings.allowed_hosts:
            errors.append("ALLOWED_HOSTS should not include '*' in production")
        
        if settings.debug:
            errors.append("DEBUG should be False in production")
    
    # Check file paths
    if not os.path.exists(os.path.dirname(settings.upload_path)):
        try:
            os.makedirs(os.path.dirname(settings.upload_path), exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create upload directory: {e}")
    
    if not os.path.exists(os.path.dirname(settings.ml_model_path)):
        try:
            os.makedirs(os.path.dirname(settings.ml_model_path), exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create ML model directory: {e}")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")

# Environment-specific configurations
DATABASE_CONFIG = {
    "pool_size": settings.database_pool_size,
    "max_overflow": settings.database_max_overflow,
    "pool_timeout": settings.database_pool_timeout,
    "pool_recycle": settings.database_pool_recycle,
    "echo": settings.debug,
}

REDIS_CONFIG = {
    "max_connections": settings.redis_max_connections,
    "socket_timeout": settings.redis_socket_timeout,
    "socket_connect_timeout": settings.redis_socket_connect_timeout,
    "decode_responses": True,
}

MQTT_CONFIG = {
    "host": settings.mqtt_broker_host,
    "port": settings.mqtt_broker_port,
    "username": settings.mqtt_username,
    "password": settings.mqtt_password,
    "keepalive": settings.mqtt_keepalive,
    "qos": settings.mqtt_qos,
}

LOGGING_CONFIG = {
    "level": settings.log_level,
    "file": settings.log_file,
    "json_logging": settings.json_logging,
    "structured_logging": settings.structured_logging,
}

# Validate configuration on import
if __name__ != "__main__":
    try:
        validate_configuration()
    except ValueError as e:
        print(f"Configuration validation failed: {e}")
        if settings.environment == "production":
            raise

