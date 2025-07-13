"""
Basic Tests for Digital Twin Platform
"""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

def test_basic_imports():
    """Test that basic modules can be imported"""
    try:
        from models.asset import Asset, AssetCreate, AssetUpdate
        from models.telemetry import TelemetryData, TelemetryCreate
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")

def test_ml_model_basic():
    """Test ML model basic functionality"""
    try:
        from ml.models.predictive_maintenance import PredictiveMaintenanceModel
        model = PredictiveMaintenanceModel()
        assert model is not None
        assert hasattr(model, 'predict')
        assert hasattr(model, 'train')
    except Exception as e:
        pytest.fail(f"ML model test failed: {e}")

def test_logging_basic():
    """Test basic logging functionality"""
    try:
        from logging_config import get_logger
        logger = get_logger("test")
        assert logger is not None
        logger.info("Test log message")
    except Exception as e:
        pytest.fail(f"Logging test failed: {e}")

def test_metrics_basic():
    """Test basic metrics functionality"""
    try:
        from metrics import http_requests_total, update_websocket_connections
        assert http_requests_total is not None
        # Test metric update
        update_websocket_connections('connect')
        update_websocket_connections('disconnect')
    except Exception as e:
        pytest.fail(f"Metrics test failed: {e}")

def test_data_generation():
    """Test synthetic data generation"""
    try:
        from ml.training.data_generator import HVACDataGenerator
        generator = HVACDataGenerator()
        data = generator.generate_telemetry_data(num_samples=10)
        assert len(data) == 10
        assert 'timestamp' in data.columns
        assert 'temperature' in data.columns
    except Exception as e:
        pytest.fail(f"Data generation test failed: {e}")

def test_model_training():
    """Test model training functionality"""
    try:
        from ml.models.predictive_maintenance import PredictiveMaintenanceModel
        from ml.training.data_generator import HVACDataGenerator
        
        # Generate test data
        generator = HVACDataGenerator()
        data = generator.generate_telemetry_data(num_samples=100)
        
        # Create and train model
        model = PredictiveMaintenanceModel()
        model.train(data)
        
        # Test prediction
        test_data = data.iloc[:5]
        predictions = model.predict(test_data)
        assert len(predictions) == 5
        
    except Exception as e:
        pytest.fail(f"Model training test failed: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

