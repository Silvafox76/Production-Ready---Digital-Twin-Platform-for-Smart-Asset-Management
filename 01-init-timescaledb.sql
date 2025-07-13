-- Initialize TimescaleDB extension and create tables for Digital Twin Platform

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create assets table
CREATE TABLE IF NOT EXISTS assets (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    asset_type VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    building VARCHAR(100),
    floor VARCHAR(50),
    room VARCHAR(50),
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    status VARCHAR(50) DEFAULT 'offline',
    installation_date TIMESTAMPTZ,
    warranty_expiry TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create telemetry data table
CREATE TABLE IF NOT EXISTS telemetry_data (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    asset_id VARCHAR(255) NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    vibration DOUBLE PRECISION,
    power_consumption DOUBLE PRECISION,
    status VARCHAR(50),
    metadata JSONB,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- Convert telemetry_data to hypertable
SELECT create_hypertable('telemetry_data', 'time', if_not_exists => TRUE);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    details JSONB,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- Create maintenance records table
CREATE TABLE IF NOT EXISTS maintenance_records (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(255) NOT NULL,
    maintenance_type VARCHAR(100) NOT NULL,
    description TEXT,
    scheduled_date TIMESTAMPTZ,
    completed_date TIMESTAMPTZ,
    technician VARCHAR(255),
    cost DECIMAL(10,2),
    notes TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- Create ML predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    asset_id VARCHAR(255) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    prediction_type VARCHAR(100) NOT NULL,
    prediction_value DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    prediction_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_telemetry_asset_time ON telemetry_data (asset_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_asset_created ON alerts (asset_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_maintenance_asset_scheduled ON maintenance_records (asset_id, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_predictions_asset_date ON ml_predictions (asset_id, prediction_date DESC);

-- Create continuous aggregates for telemetry data
CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    asset_id,
    AVG(temperature) as avg_temperature,
    MIN(temperature) as min_temperature,
    MAX(temperature) as max_temperature,
    AVG(humidity) as avg_humidity,
    MIN(humidity) as min_humidity,
    MAX(humidity) as max_humidity,
    AVG(pressure) as avg_pressure,
    MIN(pressure) as min_pressure,
    MAX(pressure) as max_pressure,
    AVG(vibration) as avg_vibration,
    MAX(vibration) as max_vibration,
    AVG(power_consumption) as avg_power_consumption,
    MAX(power_consumption) as max_power_consumption,
    COUNT(*) as data_points
FROM telemetry_data
GROUP BY bucket, asset_id;

-- Create daily aggregates
CREATE MATERIALIZED VIEW IF NOT EXISTS telemetry_daily
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', time) AS bucket,
    asset_id,
    AVG(temperature) as avg_temperature,
    MIN(temperature) as min_temperature,
    MAX(temperature) as max_temperature,
    AVG(humidity) as avg_humidity,
    MIN(humidity) as min_humidity,
    MAX(humidity) as max_humidity,
    AVG(pressure) as avg_pressure,
    MIN(pressure) as min_pressure,
    MAX(pressure) as max_pressure,
    AVG(vibration) as avg_vibration,
    MAX(vibration) as max_vibration,
    AVG(power_consumption) as avg_power_consumption,
    MAX(power_consumption) as max_power_consumption,
    COUNT(*) as data_points
FROM telemetry_data
GROUP BY bucket, asset_id;

-- Add refresh policies for continuous aggregates
SELECT add_continuous_aggregate_policy('telemetry_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

SELECT add_continuous_aggregate_policy('telemetry_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');

-- Create data retention policy (keep raw data for 90 days)
SELECT add_retention_policy('telemetry_data', INTERVAL '90 days');

-- Insert sample assets
INSERT INTO assets (id, name, description, asset_type, location, building, floor, room, manufacturer, model, serial_number, status, installation_date, warranty_expiry) VALUES
('asset_1', 'HVAC Unit 1', 'Main HVAC system for building A', 'hvac', 'Building A, Floor 1', 'Building A', 'Floor 1', 'Room 101', 'Siemens', 'Model-100X', 'SN000001', 'online', '2023-01-15', '2026-01-15'),
('asset_2', 'Water Pump 2', 'Primary water circulation pump', 'pump', 'Building A, Floor B1', 'Building A', 'Floor B1', 'Room B101', 'Honeywell', 'Model-200Y', 'SN000002', 'online', '2023-02-01', '2026-02-01'),
('asset_3', 'Motor 3', 'Ventilation motor for floor 2', 'motor', 'Building A, Floor 2', 'Building A', 'Floor 2', 'Room 201', 'Siemens', 'Model-300Z', 'SN000003', 'warning', '2023-03-01', '2026-03-01')
ON CONFLICT (id) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

