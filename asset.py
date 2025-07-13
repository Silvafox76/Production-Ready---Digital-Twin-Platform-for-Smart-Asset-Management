"""
Asset models for Digital Twin Platform
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field

class AssetType(str, Enum):
    """Asset type enumeration"""
    HVAC = "hvac"
    PUMP = "pump"
    MOTOR = "motor"
    SENSOR = "sensor"
    VALVE = "valve"
    COMPRESSOR = "compressor"
    CHILLER = "chiller"
    BOILER = "boiler"
    FAN = "fan"
    OTHER = "other"

class AssetStatus(str, Enum):
    """Asset status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    WARNING = "warning"

class AssetBase(BaseModel):
    """Base asset model"""
    name: str = Field(..., description="Asset name")
    description: Optional[str] = Field(None, description="Asset description")
    asset_type: AssetType = Field(..., description="Type of asset")
    location: Optional[str] = Field(None, description="Physical location")
    building: Optional[str] = Field(None, description="Building identifier")
    floor: Optional[str] = Field(None, description="Floor identifier")
    room: Optional[str] = Field(None, description="Room identifier")
    manufacturer: Optional[str] = Field(None, description="Manufacturer")
    model: Optional[str] = Field(None, description="Model number")
    serial_number: Optional[str] = Field(None, description="Serial number")
    installation_date: Optional[datetime] = Field(None, description="Installation date")
    warranty_expiry: Optional[datetime] = Field(None, description="Warranty expiry date")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

class AssetCreate(AssetBase):
    """Asset creation model"""
    pass

class AssetUpdate(BaseModel):
    """Asset update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    asset_type: Optional[AssetType] = None
    location: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    status: Optional[AssetStatus] = None
    metadata: Optional[Dict[str, Any]] = None

class Asset(AssetBase):
    """Complete asset model"""
    id: str = Field(..., description="Unique asset identifier")
    status: AssetStatus = Field(default=AssetStatus.OFFLINE, description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_seen: Optional[datetime] = Field(None, description="Last telemetry timestamp")
    
    class Config:
        from_attributes = True

class AssetSummary(BaseModel):
    """Asset summary for dashboard"""
    id: str
    name: str
    asset_type: AssetType
    status: AssetStatus
    location: Optional[str]
    last_seen: Optional[datetime]
    health_score: Optional[float] = Field(None, ge=0, le=100, description="Health score 0-100")
    
class AssetHealth(BaseModel):
    """Asset health metrics"""
    asset_id: str
    health_score: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., description="low, medium, high, critical")
    predicted_failure_date: Optional[datetime] = None
    maintenance_recommendations: list[str] = Field(default_factory=list)
    last_calculated: datetime = Field(default_factory=datetime.utcnow)

