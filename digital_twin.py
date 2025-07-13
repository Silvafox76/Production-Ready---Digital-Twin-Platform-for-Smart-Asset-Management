"""
Digital Twin Platform API Routes
"""
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import random
import json

digital_twin_bp = Blueprint('digital_twin', __name__)

# Mock data for demonstration
MOCK_ASSETS = [
    {
        "id": "asset_1",
        "name": "HVAC Unit 1",
        "description": "Main HVAC system for building A",
        "asset_type": "hvac",
        "location": "Building A, Floor 1",
        "building": "Building A",
        "floor": "Floor 1",
        "room": "Room 101",
        "manufacturer": "Siemens",
        "model": "Model-100X",
        "serial_number": "SN000001",
        "status": "online",
        "installation_date": "2023-01-15T00:00:00Z",
        "warranty_expiry": "2026-01-15T00:00:00Z",
        "last_seen": datetime.now().isoformat(),
        "created_at": "2023-01-15T00:00:00Z",
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": "asset_2",
        "name": "Water Pump 2",
        "description": "Primary water circulation pump",
        "asset_type": "pump",
        "location": "Building A, Floor B1",
        "building": "Building A",
        "floor": "Floor B1",
        "room": "Room B101",
        "manufacturer": "Honeywell",
        "model": "Model-200Y",
        "serial_number": "SN000002",
        "status": "online",
        "installation_date": "2023-02-01T00:00:00Z",
        "warranty_expiry": "2026-02-01T00:00:00Z",
        "last_seen": datetime.now().isoformat(),
        "created_at": "2023-02-01T00:00:00Z",
        "updated_at": datetime.now().isoformat()
    },
    {
        "id": "asset_3",
        "name": "Motor 3",
        "description": "Ventilation motor for floor 2",
        "asset_type": "motor",
        "location": "Building A, Floor 2",
        "building": "Building A",
        "floor": "Floor 2",
        "room": "Room 201",
        "manufacturer": "Siemens",
        "model": "Model-300Z",
        "serial_number": "SN000003",
        "status": "warning",
        "installation_date": "2023-03-01T00:00:00Z",
        "warranty_expiry": "2026-03-01T00:00:00Z",
        "last_seen": datetime.now().isoformat(),
        "created_at": "2023-03-01T00:00:00Z",
        "updated_at": datetime.now().isoformat()
    }
]

def generate_mock_telemetry(asset_id, hours=24):
    """Generate mock telemetry data for an asset"""
    telemetry = []
    now = datetime.now()
    
    for i in range(hours * 12):  # Every 5 minutes
        timestamp = now - timedelta(minutes=i * 5)
        
        # Generate realistic HVAC data with some variation
        base_temp = 22.0 + random.uniform(-3, 3)
        base_humidity = 50.0 + random.uniform(-10, 10)
        base_pressure = 101.3 + random.uniform(-0.5, 0.5)
        base_vibration = 0.1 + random.uniform(0, 0.3)
        base_power = 15.0 + random.uniform(-5, 10)
        
        telemetry.append({
            "time": timestamp.isoformat(),
            "asset_id": asset_id,
            "temperature": round(base_temp, 2),
            "humidity": round(base_humidity, 2),
            "pressure": round(base_pressure, 2),
            "vibration": round(base_vibration, 3),
            "power_consumption": round(base_power, 2),
            "status": "normal" if random.random() > 0.1 else "warning"
        })
    
    return sorted(telemetry, key=lambda x: x['time'])

@digital_twin_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "Digital Twin Platform"
    })

@digital_twin_bp.route('/assets', methods=['GET'])
def get_assets():
    """Get all assets with pagination"""
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 100))
    
    # Apply pagination
    paginated_assets = MOCK_ASSETS[skip:skip + limit]
    
    return jsonify({
        "assets": paginated_assets,
        "total": len(MOCK_ASSETS),
        "skip": skip,
        "limit": limit
    })

@digital_twin_bp.route('/assets/<asset_id>', methods=['GET'])
def get_asset(asset_id):
    """Get a specific asset by ID"""
    asset = next((a for a in MOCK_ASSETS if a['id'] == asset_id), None)
    
    if not asset:
        return jsonify({"error": "Asset not found"}), 404
    
    return jsonify(asset)

@digital_twin_bp.route('/assets', methods=['POST'])
def create_asset():
    """Create a new asset"""
    data = request.get_json()
    
    # Generate new asset ID
    new_id = f"asset_{len(MOCK_ASSETS) + 1}"
    
    new_asset = {
        "id": new_id,
        "name": data.get('name', 'New Asset'),
        "description": data.get('description', ''),
        "asset_type": data.get('asset_type', 'unknown'),
        "location": data.get('location', ''),
        "building": data.get('building', ''),
        "floor": data.get('floor', ''),
        "room": data.get('room', ''),
        "manufacturer": data.get('manufacturer', ''),
        "model": data.get('model', ''),
        "serial_number": data.get('serial_number', ''),
        "status": "offline",
        "installation_date": data.get('installation_date', datetime.now().isoformat()),
        "warranty_expiry": data.get('warranty_expiry'),
        "last_seen": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    MOCK_ASSETS.append(new_asset)
    
    return jsonify(new_asset)

@digital_twin_bp.route('/assets/<asset_id>', methods=['PUT'])
def update_asset(asset_id):
    """Update an existing asset"""
    asset = next((a for a in MOCK_ASSETS if a['id'] == asset_id), None)
    
    if not asset:
        return jsonify({"error": "Asset not found"}), 404
    
    data = request.get_json()
    
    # Update asset fields
    for key, value in data.items():
        if key in asset and key not in ['id', 'created_at']:
            asset[key] = value
    
    asset['updated_at'] = datetime.now().isoformat()
    
    return jsonify(asset)

@digital_twin_bp.route('/assets/<asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    """Delete an asset"""
    global MOCK_ASSETS
    MOCK_ASSETS = [a for a in MOCK_ASSETS if a['id'] != asset_id]
    
    return jsonify({"message": f"Asset {asset_id} deleted successfully"})

@digital_twin_bp.route('/assets/<asset_id>/telemetry', methods=['GET'])
def get_asset_telemetry(asset_id):
    """Get telemetry data for a specific asset"""
    asset = next((a for a in MOCK_ASSETS if a['id'] == asset_id), None)
    
    if not asset:
        return jsonify({"error": "Asset not found"}), 404
    
    limit = int(request.args.get('limit', 100))
    hours = int(request.args.get('hours', 24))
    
    # Generate mock telemetry data
    telemetry = generate_mock_telemetry(asset_id, hours)
    
    # Apply limit
    if limit:
        telemetry = telemetry[-limit:]
    
    return jsonify({
        "asset_id": asset_id,
        "telemetry": telemetry,
        "count": len(telemetry)
    })

@digital_twin_bp.route('/telemetry', methods=['POST'])
def create_telemetry():
    """Create new telemetry data point"""
    data = request.get_json()
    
    # Validate required fields
    if 'asset_id' not in data:
        return jsonify({"error": "asset_id is required"}), 400
    
    # Create telemetry record
    telemetry_record = {
        "id": f"telemetry_{datetime.now().timestamp()}",
        "time": data.get('time', datetime.now().isoformat()),
        "asset_id": data['asset_id'],
        "temperature": data.get('temperature'),
        "humidity": data.get('humidity'),
        "pressure": data.get('pressure'),
        "vibration": data.get('vibration'),
        "power_consumption": data.get('power_consumption'),
        "status": data.get('status', 'normal'),
        "metadata": data.get('metadata', {})
    }
    
    return jsonify(telemetry_record)

@digital_twin_bp.route('/system/status', methods=['GET'])
def system_status():
    """Get system status and metrics"""
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "status": "operational",
        "services": {
            "api": "healthy",
            "database": "healthy",
            "mqtt": "healthy",
            "ml_engine": "healthy"
        },
        "metrics": {
            "total_assets": len(MOCK_ASSETS),
            "online_assets": len([a for a in MOCK_ASSETS if a['status'] == 'online']),
            "warning_assets": len([a for a in MOCK_ASSETS if a['status'] == 'warning']),
            "error_assets": len([a for a in MOCK_ASSETS if a['status'] == 'error']),
            "uptime_seconds": 3600,  # Mock uptime
            "memory_usage_mb": 256,  # Mock memory usage
            "cpu_usage_percent": 15.5  # Mock CPU usage
        }
    })

@digital_twin_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts"""
    # Generate mock alerts
    alerts = [
        {
            "id": 1,
            "asset_id": "asset_3",
            "alert_type": "high_vibration",
            "severity": "warning",
            "message": "Vibration levels above normal threshold",
            "details": {"current_value": 0.45, "threshold": 0.4},
            "acknowledged": False,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat()
        },
        {
            "id": 2,
            "asset_id": "asset_1",
            "alert_type": "temperature_anomaly",
            "severity": "info",
            "message": "Temperature reading outside expected range",
            "details": {"current_value": 26.5, "expected_range": [18, 25]},
            "acknowledged": True,
            "acknowledged_by": "technician@company.com",
            "acknowledged_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "created_at": (datetime.now() - timedelta(hours=3)).isoformat()
        }
    ]
    
    return jsonify({
        "alerts": alerts,
        "total": len(alerts),
        "unacknowledged": len([a for a in alerts if not a['acknowledged']])
    })

@digital_twin_bp.route('/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get analytics data for dashboard"""
    return jsonify({
        "summary": {
            "total_assets": len(MOCK_ASSETS),
            "online_assets": len([a for a in MOCK_ASSETS if a['status'] == 'online']),
            "warning_assets": len([a for a in MOCK_ASSETS if a['status'] == 'warning']),
            "error_assets": len([a for a in MOCK_ASSETS if a['status'] == 'error']),
            "total_energy_consumption": 1250.5,
            "average_efficiency": 87.3,
            "maintenance_due": 2
        },
        "energy_trends": [
            {"date": "2025-07-06", "consumption": 1200},
            {"date": "2025-07-07", "consumption": 1180},
            {"date": "2025-07-08", "consumption": 1220},
            {"date": "2025-07-09", "consumption": 1190},
            {"date": "2025-07-10", "consumption": 1210},
            {"date": "2025-07-11", "consumption": 1230},
            {"date": "2025-07-12", "consumption": 1250}
        ],
        "asset_performance": [
            {"asset_id": "asset_1", "efficiency": 92.1, "uptime": 99.2},
            {"asset_id": "asset_2", "efficiency": 88.5, "uptime": 97.8},
            {"asset_id": "asset_3", "efficiency": 81.2, "uptime": 94.5}
        ]
    })

@digital_twin_bp.route('/ml/predictions/<asset_id>', methods=['GET'])
def get_ml_predictions(asset_id):
    """Get ML predictions for an asset"""
    # Generate mock predictions
    predictions = {
        "asset_id": asset_id,
        "predictions": [
            {
                "type": "failure_probability",
                "value": random.uniform(0.1, 0.3),
                "confidence": random.uniform(0.8, 0.95),
                "time_horizon": "7_days"
            },
            {
                "type": "maintenance_recommendation",
                "value": "routine_inspection",
                "confidence": random.uniform(0.7, 0.9),
                "time_horizon": "30_days"
            },
            {
                "type": "energy_optimization",
                "value": random.uniform(5, 15),  # Percentage improvement
                "confidence": random.uniform(0.6, 0.8),
                "time_horizon": "immediate"
            }
        ],
        "generated_at": datetime.now().isoformat()
    }
    
    return jsonify(predictions)

