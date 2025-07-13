"""
Database Migration Script for Digital Twin Platform
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from db.database import DatabaseManager
import structlog

logger = structlog.get_logger()

async def create_sample_data():
    """Create sample assets and telemetry data"""
    db_manager = DatabaseManager()
    await db_manager.initialize()
    
    try:
        from models.asset import AssetCreate, AssetType
        from models.telemetry import TelemetryCreate
        from datetime import datetime, timedelta
        import random
        
        # Create sample assets
        sample_assets = [
            AssetCreate(
                name="HVAC Unit 001",
                description="Main HVAC unit for Building A",
                asset_type=AssetType.HVAC,
                location="Building A - Roof",
                building="Building A",
                floor="Roof",
                manufacturer="Carrier",
                model="30XA-1002",
                serial_number="HV001-2023",
                installation_date=datetime(2023, 1, 15)
            ),
            AssetCreate(
                name="Chiller Unit 001",
                description="Primary chiller for cooling system",
                asset_type=AssetType.CHILLER,
                location="Building A - Basement",
                building="Building A",
                floor="Basement",
                manufacturer="Trane",
                model="RTAC-350",
                serial_number="CH001-2023",
                installation_date=datetime(2023, 2, 20)
            ),
            AssetCreate(
                name="Pump Motor 001",
                description="Water circulation pump motor",
                asset_type=AssetType.PUMP,
                location="Building A - Mechanical Room",
                building="Building A",
                floor="1",
                room="Mechanical Room",
                manufacturer="Grundfos",
                model="CR32-4",
                serial_number="PM001-2023",
                installation_date=datetime(2023, 3, 10)
            ),
            AssetCreate(
                name="Compressor Unit 001",
                description="Air compressor for pneumatic systems",
                asset_type=AssetType.COMPRESSOR,
                location="Building B - Utility Room",
                building="Building B",
                floor="1",
                room="Utility Room",
                manufacturer="Atlas Copco",
                model="GA22-8.5",
                serial_number="AC001-2023",
                installation_date=datetime(2023, 4, 5)
            ),
            AssetCreate(
                name="Exhaust Fan 001",
                description="Exhaust fan for ventilation system",
                asset_type=AssetType.FAN,
                location="Building B - Roof",
                building="Building B",
                floor="Roof",
                manufacturer="Greenheck",
                model="SWB-180",
                serial_number="EF001-2023",
                installation_date=datetime(2023, 5, 12)
            )
        ]
        
        created_assets = []
        for asset_data in sample_assets:
            asset = await db_manager.create_asset(asset_data)
            created_assets.append(asset)
            logger.info("Created sample asset", asset_id=asset.id, name=asset.name)
        
        # Create sample telemetry data for the last 7 days
        logger.info("Creating sample telemetry data...")
        
        for asset in created_assets:
            # Generate telemetry for the last 7 days
            start_time = datetime.now() - timedelta(days=7)
            
            for day in range(7):
                day_start = start_time + timedelta(days=day)
                
                # Generate 24 hours of data (every hour)
                for hour in range(24):
                    timestamp = day_start + timedelta(hours=hour)
                    
                    # Generate realistic values based on asset type
                    if asset.asset_type == AssetType.HVAC:
                        temperature = random.uniform(18, 25) + random.uniform(-2, 2)
                        humidity = random.uniform(40, 60) + random.uniform(-5, 5)
                        power_consumption = random.uniform(8, 15) + random.uniform(-2, 2)
                    elif asset.asset_type == AssetType.CHILLER:
                        temperature = random.uniform(5, 12) + random.uniform(-1, 1)
                        humidity = random.uniform(80, 95) + random.uniform(-3, 3)
                        power_consumption = random.uniform(25, 40) + random.uniform(-5, 5)
                    elif asset.asset_type == AssetType.PUMP:
                        temperature = random.uniform(35, 45) + random.uniform(-3, 3)
                        humidity = random.uniform(30, 50) + random.uniform(-5, 5)
                        power_consumption = random.uniform(3, 8) + random.uniform(-1, 1)
                    elif asset.asset_type == AssetType.COMPRESSOR:
                        temperature = random.uniform(40, 55) + random.uniform(-5, 5)
                        humidity = random.uniform(20, 40) + random.uniform(-5, 5)
                        power_consumption = random.uniform(15, 25) + random.uniform(-3, 3)
                    else:  # FAN
                        temperature = random.uniform(25, 35) + random.uniform(-2, 2)
                        humidity = random.uniform(35, 55) + random.uniform(-5, 5)
                        power_consumption = random.uniform(2, 6) + random.uniform(-1, 1)
                    
                    # Common values
                    pressure = random.uniform(100, 105) + random.uniform(-2, 2)
                    vibration = random.uniform(0.1, 0.5) + random.uniform(-0.1, 0.1)
                    
                    # Occasionally add some anomalies
                    if random.random() < 0.05:  # 5% chance of anomaly
                        temperature += random.uniform(10, 20)
                        vibration += random.uniform(1, 3)
                        power_consumption += random.uniform(5, 15)
                    
                    telemetry_data = TelemetryCreate(
                        asset_id=asset.id,
                        timestamp=timestamp,
                        temperature=round(temperature, 2),
                        humidity=round(max(0, min(100, humidity)), 2),
                        pressure=round(pressure, 2),
                        vibration=round(max(0, vibration), 3),
                        power_consumption=round(max(0, power_consumption), 2),
                        status='online' if random.random() > 0.02 else 'warning'
                    )
                    
                    await db_manager.create_telemetry(telemetry_data)
        
        logger.info("Sample data creation completed")
        
    except Exception as e:
        logger.error("Failed to create sample data", error=str(e))
        raise
    finally:
        await db_manager.close()

async def main():
    """Main migration function"""
    logger.info("Starting database migration")
    
    # Initialize database
    db_manager = DatabaseManager()
    await db_manager.initialize()
    await db_manager.close()
    
    # Create sample data
    await create_sample_data()
    
    logger.info("Database migration completed")

if __name__ == "__main__":
    asyncio.run(main())

