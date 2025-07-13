"""
Database Manager for Digital Twin Platform
Handles PostgreSQL and TimescaleDB connections and operations
"""
import asyncio
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

import asyncpg
import structlog
from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Float, Integer, JSON, Boolean, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import redis.asyncio as redis

from models.asset import Asset, AssetCreate, AssetUpdate, AssetStatus, AssetType
from models.telemetry import TelemetryData, TelemetryCreate

logger = structlog.get_logger()

Base = declarative_base()

class AssetTable(Base):
    """SQLAlchemy Asset table model"""
    __tablename__ = 'assets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    asset_type = Column(String(50), nullable=False)
    location = Column(String(255))
    building = Column(String(255))
    floor = Column(String(100))
    room = Column(String(100))
    manufacturer = Column(String(255))
    model = Column(String(255))
    serial_number = Column(String(255))
    installation_date = Column(DateTime)
    warranty_expiry = Column(DateTime)
    status = Column(String(50), default='offline')
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime)

class TelemetryTable(Base):
    """SQLAlchemy Telemetry table model (TimescaleDB hypertable)"""
    __tablename__ = 'telemetry'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    temperature = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    vibration = Column(Float)
    power_consumption = Column(Float)
    status = Column(String(50), default='online')
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Database manager for PostgreSQL/TimescaleDB operations"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:password@localhost:5432/digital_twin"
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Convert to async URL
        self.async_database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        self.engine = None
        self.async_session = None
        self.redis_client = None
        
        logger.info("Database Manager initialized", database_url=self.database_url)
    
    async def initialize(self):
        """Initialize database connections and create tables"""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.async_database_url,
                echo=False,
                pool_size=10,
                max_overflow=20
            )
            
            # Create session factory
            self.async_session = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Initialize Redis
            self.redis_client = redis.from_url(self.redis_url)
            
            # Create tables
            await self.create_tables()
            
            # Setup TimescaleDB hypertable
            await self.setup_timescaledb()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize database", error=str(e))
            raise
    
    async def create_tables(self):
        """Create database tables"""
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        except Exception as e:
            logger.error("Failed to create tables", error=str(e))
            raise
    
    async def setup_timescaledb(self):
        """Setup TimescaleDB hypertable for telemetry data"""
        try:
            # Connect directly with asyncpg for TimescaleDB commands
            conn = await asyncpg.connect(self.database_url)
            
            # Create TimescaleDB extension if not exists
            await conn.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;")
            
            # Create hypertable for telemetry data
            try:
                await conn.execute("""
                    SELECT create_hypertable('telemetry', 'timestamp', 
                                           chunk_time_interval => INTERVAL '1 day',
                                           if_not_exists => TRUE);
                """)
                logger.info("TimescaleDB hypertable created for telemetry")
            except Exception as e:
                # Hypertable might already exist
                logger.warning("TimescaleDB hypertable setup warning", error=str(e))
            
            # Create indexes for better performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_telemetry_asset_id_timestamp 
                ON telemetry (asset_id, timestamp DESC);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp 
                ON telemetry (timestamp DESC);
            """)
            
            await conn.close()
            logger.info("TimescaleDB setup completed")
            
        except Exception as e:
            logger.error("Failed to setup TimescaleDB", error=str(e))
            # Continue without TimescaleDB features
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Database connections closed")
    
    # Asset operations
    async def create_asset(self, asset_data: AssetCreate) -> Asset:
        """Create a new asset"""
        try:
            async with self.async_session() as session:
                # Create asset record
                asset_record = AssetTable(
                    name=asset_data.name,
                    description=asset_data.description,
                    asset_type=asset_data.asset_type.value,
                    location=asset_data.location,
                    building=asset_data.building,
                    floor=asset_data.floor,
                    room=asset_data.room,
                    manufacturer=asset_data.manufacturer,
                    model=asset_data.model,
                    serial_number=asset_data.serial_number,
                    installation_date=asset_data.installation_date,
                    warranty_expiry=asset_data.warranty_expiry,
                    metadata=asset_data.metadata or {}
                )
                
                session.add(asset_record)
                await session.commit()
                await session.refresh(asset_record)
                
                # Convert to Pydantic model
                asset = Asset(
                    id=str(asset_record.id),
                    name=asset_record.name,
                    description=asset_record.description,
                    asset_type=AssetType(asset_record.asset_type),
                    location=asset_record.location,
                    building=asset_record.building,
                    floor=asset_record.floor,
                    room=asset_record.room,
                    manufacturer=asset_record.manufacturer,
                    model=asset_record.model,
                    serial_number=asset_record.serial_number,
                    installation_date=asset_record.installation_date,
                    warranty_expiry=asset_record.warranty_expiry,
                    status=AssetStatus(asset_record.status),
                    metadata=asset_record.metadata,
                    created_at=asset_record.created_at,
                    updated_at=asset_record.updated_at,
                    last_seen=asset_record.last_seen
                )
                
                # Cache in Redis
                await self.cache_asset(asset)
                
                return asset
                
        except Exception as e:
            logger.error("Failed to create asset", error=str(e))
            raise
    
    async def get_asset(self, asset_id: str) -> Optional[Asset]:
        """Get asset by ID"""
        try:
            # Try cache first
            cached_asset = await self.get_cached_asset(asset_id)
            if cached_asset:
                return cached_asset
            
            async with self.async_session() as session:
                result = await session.get(AssetTable, uuid.UUID(asset_id))
                if not result:
                    return None
                
                asset = Asset(
                    id=str(result.id),
                    name=result.name,
                    description=result.description,
                    asset_type=AssetType(result.asset_type),
                    location=result.location,
                    building=result.building,
                    floor=result.floor,
                    room=result.room,
                    manufacturer=result.manufacturer,
                    model=result.model,
                    serial_number=result.serial_number,
                    installation_date=result.installation_date,
                    warranty_expiry=result.warranty_expiry,
                    status=AssetStatus(result.status),
                    metadata=result.metadata,
                    created_at=result.created_at,
                    updated_at=result.updated_at,
                    last_seen=result.last_seen
                )
                
                # Cache the result
                await self.cache_asset(asset)
                
                return asset
                
        except Exception as e:
            logger.error("Failed to get asset", asset_id=asset_id, error=str(e))
            raise
    
    async def get_assets(self, skip: int = 0, limit: int = 100) -> List[Asset]:
        """Get assets with pagination"""
        try:
            async with self.async_session() as session:
                from sqlalchemy import select
                
                stmt = select(AssetTable).offset(skip).limit(limit)
                result = await session.execute(stmt)
                asset_records = result.scalars().all()
                
                assets = []
                for record in asset_records:
                    asset = Asset(
                        id=str(record.id),
                        name=record.name,
                        description=record.description,
                        asset_type=AssetType(record.asset_type),
                        location=record.location,
                        building=record.building,
                        floor=record.floor,
                        room=record.room,
                        manufacturer=record.manufacturer,
                        model=record.model,
                        serial_number=record.serial_number,
                        installation_date=record.installation_date,
                        warranty_expiry=record.warranty_expiry,
                        status=AssetStatus(record.status),
                        metadata=record.metadata,
                        created_at=record.created_at,
                        updated_at=record.updated_at,
                        last_seen=record.last_seen
                    )
                    assets.append(asset)
                
                return assets
                
        except Exception as e:
            logger.error("Failed to get assets", error=str(e))
            raise
    
    async def update_asset(self, asset_id: str, asset_update: AssetUpdate) -> Optional[Asset]:
        """Update asset"""
        try:
            async with self.async_session() as session:
                result = await session.get(AssetTable, uuid.UUID(asset_id))
                if not result:
                    return None
                
                # Update fields
                update_data = asset_update.dict(exclude_unset=True)
                for field, value in update_data.items():
                    if hasattr(result, field):
                        if field == 'asset_type' and value:
                            setattr(result, field, value.value)
                        elif field == 'status' and value:
                            setattr(result, field, value.value)
                        else:
                            setattr(result, field, value)
                
                result.updated_at = datetime.utcnow()
                
                await session.commit()
                await session.refresh(result)
                
                asset = Asset(
                    id=str(result.id),
                    name=result.name,
                    description=result.description,
                    asset_type=AssetType(result.asset_type),
                    location=result.location,
                    building=result.building,
                    floor=result.floor,
                    room=result.room,
                    manufacturer=result.manufacturer,
                    model=result.model,
                    serial_number=result.serial_number,
                    installation_date=result.installation_date,
                    warranty_expiry=result.warranty_expiry,
                    status=AssetStatus(result.status),
                    metadata=result.metadata,
                    created_at=result.created_at,
                    updated_at=result.updated_at,
                    last_seen=result.last_seen
                )
                
                # Update cache
                await self.cache_asset(asset)
                
                return asset
                
        except Exception as e:
            logger.error("Failed to update asset", asset_id=asset_id, error=str(e))
            raise
    
    async def delete_asset(self, asset_id: str) -> bool:
        """Delete asset"""
        try:
            async with self.async_session() as session:
                result = await session.get(AssetTable, uuid.UUID(asset_id))
                if not result:
                    return False
                
                await session.delete(result)
                await session.commit()
                
                # Remove from cache
                await self.remove_cached_asset(asset_id)
                
                return True
                
        except Exception as e:
            logger.error("Failed to delete asset", asset_id=asset_id, error=str(e))
            raise
    
    async def count_assets(self) -> int:
        """Count total assets"""
        try:
            async with self.async_session() as session:
                from sqlalchemy import select, func
                
                stmt = select(func.count(AssetTable.id))
                result = await session.execute(stmt)
                return result.scalar()
                
        except Exception as e:
            logger.error("Failed to count assets", error=str(e))
            raise
    
    # Telemetry operations
    async def create_telemetry(self, telemetry_data: TelemetryCreate) -> TelemetryData:
        """Create telemetry record"""
        try:
            async with self.async_session() as session:
                telemetry_record = TelemetryTable(
                    asset_id=uuid.UUID(telemetry_data.asset_id),
                    timestamp=telemetry_data.timestamp,
                    temperature=telemetry_data.temperature,
                    humidity=telemetry_data.humidity,
                    pressure=telemetry_data.pressure,
                    vibration=telemetry_data.vibration,
                    power_consumption=telemetry_data.power_consumption,
                    status=telemetry_data.status,
                    metadata=telemetry_data.metadata or {}
                )
                
                session.add(telemetry_record)
                await session.commit()
                await session.refresh(telemetry_record)
                
                # Update asset last_seen
                await self.update_asset_last_seen(telemetry_data.asset_id, telemetry_data.timestamp)
                
                telemetry = TelemetryData(
                    id=str(telemetry_record.id),
                    asset_id=str(telemetry_record.asset_id),
                    timestamp=telemetry_record.timestamp,
                    temperature=telemetry_record.temperature,
                    humidity=telemetry_record.humidity,
                    pressure=telemetry_record.pressure,
                    vibration=telemetry_record.vibration,
                    power_consumption=telemetry_record.power_consumption,
                    status=telemetry_record.status,
                    metadata=telemetry_record.metadata,
                    created_at=telemetry_record.created_at
                )
                
                return telemetry
                
        except Exception as e:
            logger.error("Failed to create telemetry", error=str(e))
            raise
    
    async def get_telemetry(self, 
                          asset_id: str, 
                          limit: int = 100,
                          start_time: Optional[str] = None,
                          end_time: Optional[str] = None) -> List[TelemetryData]:
        """Get telemetry data for asset"""
        try:
            async with self.async_session() as session:
                from sqlalchemy import select, and_
                
                stmt = select(TelemetryTable).where(
                    TelemetryTable.asset_id == uuid.UUID(asset_id)
                )
                
                # Add time filters if provided
                if start_time:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    stmt = stmt.where(TelemetryTable.timestamp >= start_dt)
                
                if end_time:
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    stmt = stmt.where(TelemetryTable.timestamp <= end_dt)
                
                stmt = stmt.order_by(TelemetryTable.timestamp.desc()).limit(limit)
                
                result = await session.execute(stmt)
                telemetry_records = result.scalars().all()
                
                telemetry_data = []
                for record in telemetry_records:
                    telemetry = TelemetryData(
                        id=str(record.id),
                        asset_id=str(record.asset_id),
                        timestamp=record.timestamp,
                        temperature=record.temperature,
                        humidity=record.humidity,
                        pressure=record.pressure,
                        vibration=record.vibration,
                        power_consumption=record.power_consumption,
                        status=record.status,
                        metadata=record.metadata,
                        created_at=record.created_at
                    )
                    telemetry_data.append(telemetry)
                
                return telemetry_data
                
        except Exception as e:
            logger.error("Failed to get telemetry", asset_id=asset_id, error=str(e))
            raise
    
    async def update_asset_last_seen(self, asset_id: str, timestamp: datetime):
        """Update asset last seen timestamp"""
        try:
            async with self.async_session() as session:
                result = await session.get(AssetTable, uuid.UUID(asset_id))
                if result:
                    result.last_seen = timestamp
                    result.status = 'online'  # Mark as online when receiving data
                    await session.commit()
                    
                    # Update cache
                    await self.invalidate_asset_cache(asset_id)
                    
        except Exception as e:
            logger.error("Failed to update asset last seen", asset_id=asset_id, error=str(e))
    
    # Cache operations
    async def cache_asset(self, asset: Asset):
        """Cache asset in Redis"""
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    f"asset:{asset.id}",
                    300,  # 5 minutes TTL
                    asset.json()
                )
        except Exception as e:
            logger.warning("Failed to cache asset", asset_id=asset.id, error=str(e))
    
    async def get_cached_asset(self, asset_id: str) -> Optional[Asset]:
        """Get cached asset from Redis"""
        try:
            if self.redis_client:
                cached_data = await self.redis_client.get(f"asset:{asset_id}")
                if cached_data:
                    return Asset.parse_raw(cached_data)
        except Exception as e:
            logger.warning("Failed to get cached asset", asset_id=asset_id, error=str(e))
        return None
    
    async def remove_cached_asset(self, asset_id: str):
        """Remove asset from cache"""
        try:
            if self.redis_client:
                await self.redis_client.delete(f"asset:{asset_id}")
        except Exception as e:
            logger.warning("Failed to remove cached asset", asset_id=asset_id, error=str(e))
    
    async def invalidate_asset_cache(self, asset_id: str):
        """Invalidate asset cache"""
        await self.remove_cached_asset(asset_id)

