"""
Telemetry models for Digital Twin Platform
"""
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

class TelemetryBase(BaseModel):
    """Base telemetry model"""
    asset_id: str = Field(..., description="Asset identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Measurement timestamp")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Pressure in kPa")
    vibration: Optional[float] = Field(None, description="Vibration level")
    power_consumption: Optional[float] = Field(None, ge=0, description="Power consumption in kW")
    status: str = Field(default="online", description="Device status")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional sensor data")

class TelemetryCreate(TelemetryBase):
    """Telemetry creation model"""
    pass

class TelemetryData(TelemetryBase):
    """Complete telemetry model"""
    id: str = Field(..., description="Unique telemetry record identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    class Config:
        from_attributes = True

class TelemetryAggregation(BaseModel):
    """Aggregated telemetry data"""
    asset_id: str
    start_time: datetime
    end_time: datetime
    avg_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    avg_humidity: Optional[float] = None
    min_humidity: Optional[float] = None
    max_humidity: Optional[float] = None
    avg_pressure: Optional[float] = None
    min_pressure: Optional[float] = None
    max_pressure: Optional[float] = None
    avg_vibration: Optional[float] = None
    max_vibration: Optional[float] = None
    total_power_consumption: Optional[float] = None
    avg_power_consumption: Optional[float] = None
    data_points: int = Field(..., description="Number of data points in aggregation")

class TelemetryAlert(BaseModel):
    """Telemetry alert model"""
    id: str
    asset_id: str
    alert_type: str = Field(..., description="temperature, humidity, pressure, vibration, power")
    severity: str = Field(..., description="low, medium, high, critical")
    message: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = Field(default=False)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

