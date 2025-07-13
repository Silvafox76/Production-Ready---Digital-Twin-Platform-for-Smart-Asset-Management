"""
Backend API Tests for Digital Twin Platform
"""
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from app_enhanced import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Async test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"

class TestAssetEndpoints:
    """Test asset management endpoints"""
    
    def test_get_assets(self, client):
        """Test getting all assets"""
        response = client.get("/api/v1/assets")
        assert response.status_code == 200
        
        data = response.json()
        assert "assets" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert isinstance(data["assets"], list)
    
    def test_get_assets_with_pagination(self, client):
        """Test asset pagination"""
        response = client.get("/api/v1/assets?skip=5&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["skip"] == 5
        assert data["limit"] == 5
        assert len(data["assets"]) <= 5
    
    def test_get_single_asset(self, client):
        """Test getting a single asset"""
        asset_id = "asset_1"
        response = client.get(f"/api/v1/assets/{asset_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == asset_id
        assert "name" in data
        assert "asset_type" in data
        assert "status" in data
    
    def test_create_asset(self, client):
        """Test creating a new asset"""
        asset_data = {
            "name": "Test HVAC Unit",
            "description": "Test HVAC system",
            "asset_type": "hvac",
            "location": "Test Building",
            "manufacturer": "Test Manufacturer",
            "model": "Test Model",
            "serial_number": "TEST001"
        }
        
        response = client.post("/api/v1/assets", json=asset_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["name"] == asset_data["name"]
        assert data["asset_type"] == asset_data["asset_type"]
    
    def test_update_asset(self, client):
        """Test updating an asset"""
        asset_id = "asset_1"
        update_data = {
            "name": "Updated HVAC Unit",
            "status": "maintenance"
        }
        
        response = client.put(f"/api/v1/assets/{asset_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == asset_id
        assert "updated_at" in data
    
    def test_delete_asset(self, client):
        """Test deleting an asset"""
        asset_id = "test_asset"
        response = client.delete(f"/api/v1/assets/{asset_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data

class TestTelemetryEndpoints:
    """Test telemetry data endpoints"""
    
    def test_get_asset_telemetry(self, client):
        """Test getting telemetry data for an asset"""
        asset_id = "asset_1"
        response = client.get(f"/api/v1/assets/{asset_id}/telemetry")
        assert response.status_code == 200
        
        data = response.json()
        assert data["asset_id"] == asset_id
        assert "telemetry" in data
        assert "count" in data
        assert isinstance(data["telemetry"], list)
    
    def test_get_telemetry_with_limit(self, client):
        """Test telemetry data with limit"""
        asset_id = "asset_1"
        limit = 10
        response = client.get(f"/api/v1/assets/{asset_id}/telemetry?limit={limit}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["telemetry"]) <= limit
    
    def test_create_telemetry(self, client):
        """Test creating telemetry data"""
        telemetry_data = {
            "asset_id": "asset_1",
            "temperature": 22.5,
            "humidity": 45.0,
            "pressure": 101.3,
            "vibration": 0.2,
            "power_consumption": 12.5
        }
        
        response = client.post("/api/v1/telemetry", json=telemetry_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "id" in data
        assert data["asset_id"] == telemetry_data["asset_id"]
        assert data["temperature"] == telemetry_data["temperature"]

class TestSystemEndpoints:
    """Test system status endpoints"""
    
    def test_system_status(self, client):
        """Test system status endpoint"""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "status" in data
        assert "services" in data
        assert "metrics" in data

@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test async endpoints"""
    
    async def test_async_health_check(self, async_client):
        """Test async health check"""
        response = await async_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_async_assets(self, async_client):
        """Test async asset retrieval"""
        response = await async_client.get("/api/v1/assets")
        assert response.status_code == 200
        
        data = response.json()
        assert "assets" in data

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_asset_id(self, client):
        """Test handling of invalid asset ID"""
        response = client.get("/api/v1/assets/nonexistent")
        # Should return 200 with mock data for now
        assert response.status_code == 200
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/assets",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity

class TestValidation:
    """Test input validation"""
    
    def test_asset_creation_validation(self, client):
        """Test asset creation with missing required fields"""
        incomplete_data = {
            "name": "Test Asset"
            # Missing required fields
        }
        
        response = client.post("/api/v1/assets", json=incomplete_data)
        assert response.status_code == 422
    
    def test_telemetry_validation(self, client):
        """Test telemetry data validation"""
        invalid_data = {
            "asset_id": "",  # Empty asset ID
            "temperature": "not_a_number"  # Invalid type
        }
        
        response = client.post("/api/v1/telemetry", json=invalid_data)
        assert response.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

