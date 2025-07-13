"""
Simplified Backend Tests for Digital Twin Platform
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from models.asset import Asset, AssetCreate, AssetUpdate
        from models.telemetry import TelemetryData, TelemetryCreate
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_mqtt_client():
    """Test MQTT client initialization"""
    try:
        from mqtt_client import MQTTClient
        client = MQTTClient()
        assert client.broker_host == "localhost"
        assert client.broker_port == 1883
        assert not client.is_connected
    except Exception as e:
        pytest.fail(f"MQTT client test failed: {e}")

def test_database_manager():
    """Test database manager initialization"""
    try:
        from db.database import DatabaseManager
        db = DatabaseManager()
        assert db is not None
    except Exception as e:
        pytest.fail(f"Database manager test failed: {e}")

def test_ml_models():
    """Test ML models can be imported"""
    try:
        from ml.models.predictive_maintenance import PredictiveMaintenanceModel
        model = PredictiveMaintenanceModel()
        assert model is not None
    except Exception as e:
        pytest.fail(f"ML model test failed: {e}")

def test_config():
    """Test configuration module"""
    try:
        from config import Settings, get_settings
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'environment')
    except Exception as e:
        pytest.fail(f"Config test failed: {e}")

def test_logging_config():
    """Test logging configuration"""
    try:
        from logging_config import setup_logging, get_logger
        logger = get_logger("test")
        assert logger is not None
    except Exception as e:
        pytest.fail(f"Logging config test failed: {e}")

def test_metrics():
    """Test metrics module"""
    try:
        from metrics import http_requests_total, update_websocket_connections
        assert http_requests_total is not None
        # Test metric update
        update_websocket_connections('connect')
        update_websocket_connections('disconnect')
    except Exception as e:
        pytest.fail(f"Metrics test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

