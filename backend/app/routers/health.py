"""
Health Monitor API Router
Handles telemetry streaming, anomaly detection, and health alerts.
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import case
from typing import List
from ..database import get_db
from ..models import TelemetryReading, Alert
from ..services.telemetry import get_simulator, TELEMETRY_METRICS
from ..services.anomaly import get_detector
from datetime import datetime
import asyncio
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()

# Background telemetry generation task
async def telemetry_generation_task(spacecraft_id: str, db: Session):
    """
    Continuously generate telemetry readings and broadcast via WebSocket.
    Runs as a background task.
    """
    simulator = get_simulator(spacecraft_id)
    detector = get_detector()
    
    logger.info(f"Telemetry generation started for spacecraft {spacecraft_id}")
    
    try:
        while True:
            # Generate readings for all metrics
            for metric_name in TELEMETRY_METRICS.keys():
                value = simulator.generate_reading(metric_name)
                
                # Store in database
                reading = TelemetryReading(
                    spacecraft_id=spacecraft_id,
                    timestamp=datetime.utcnow(),
                    metric_name=metric_name,
                    value=value
                )
                db.add(reading)
                
                # Detect anomaly
                anomaly_result = detector.detect_anomaly(metric_name, value)
                
                # Create alert if anomaly detected
                if anomaly_result["is_anomaly"]:
                    alert = Alert(
                        spacecraft_id=spacecraft_id,
                        source="health",
                        response_category="engineering",
                        severity=anomaly_result["severity"],
                        message=(
                            f"Anomaly detected in {metric_name}: "
                            f"value={value:.2f} {TELEMETRY_METRICS[metric_name]['unit']}, "
                            f"anomaly_score={anomaly_result['anomaly_score']:.3f}"
                        ),
                        timestamp=datetime.utcnow(),
                        explained=False
                    )
                    db.add(alert)
                
                # Broadcast via WebSocket
                await manager.broadcast({
                    "type": "telemetry_update",
                    "spacecraft_id": spacecraft_id,
                    "metric_name": metric_name,
                    "value": value,
                    "unit": TELEMETRY_METRICS[metric_name]["unit"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "anomaly": anomaly_result
                })
            
            db.commit()
            
            # Wait 2-5 seconds between readings
            await asyncio.sleep(np.random.uniform(2, 5))
            
    except Exception as e:
        logger.error(f"Error in telemetry generation: {e}", exc_info=True)
        db.rollback()

# Import numpy for random sleep
import numpy as np

@router.get("/status")
async def get_health_status(
    spacecraft_id: str = "25544",
    db: Session = Depends(get_db)
):
    """
    Get current health status snapshot for spacecraft.
    Returns latest reading per metric with anomaly status.
    """
    detector = get_detector()
    latest_readings = {}
    
    for metric in TELEMETRY_METRICS.keys():
        reading = db.query(TelemetryReading).filter(
            TelemetryReading.spacecraft_id == spacecraft_id,
            TelemetryReading.metric_name == metric
        ).order_by(TelemetryReading.timestamp.desc()).first()
        
        if reading:
            # Get anomaly status
            anomaly = detector.detect_anomaly(metric, reading.value)
            latest_readings[metric] = {
                "value": reading.value,
                "unit": TELEMETRY_METRICS[metric]["unit"],
                "timestamp": reading.timestamp.isoformat(),
                "severity": anomaly["severity"],
                "anomaly_score": anomaly["anomaly_score"],
                "normal_range": TELEMETRY_METRICS[metric]["normal_range"]
            }
    
    # Determine overall status
    severities = [r["severity"] for r in latest_readings.values()]
    if "critical" in severities:
        overall_status = "critical"
    elif "watch" in severities:
        overall_status = "watch"
    else:
        overall_status = "nominal"
    
    return {
        "spacecraft_id": spacecraft_id,
        "metrics": latest_readings,
        "overall_status": overall_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/alerts")
async def get_unified_alerts(
    spacecraft_id: str = "25544",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get unified alerts feed (health anomalies + debris conjunctions).
    This is the core integration proof - reads from shared alerts table.
    """
    alerts = db.query(Alert).filter(
        Alert.spacecraft_id == spacecraft_id
    ).order_by(
        # Sort by severity first (critical, watch, nominal), then timestamp
        case(
            (Alert.severity == "critical", 1),
            (Alert.severity == "watch", 2),
            (Alert.severity == "nominal", 3),
            else_=4
        ),
        Alert.timestamp.desc()
    ).limit(limit).all()
    
    alert_list = [{
        "id": alert.id,
        "source": alert.source,
        "response_category": alert.response_category,
        "severity": alert.severity,
        "message": alert.message,
        "timestamp": alert.timestamp.isoformat(),
        "explained": alert.explained,
        "explanation": alert.explanation
    } for alert in alerts]
    
    return {
        "alerts": alert_list,
        "count": len(alert_list),
        "breakdown": {
            "health": len([a for a in alerts if a.source == "health"]),
            "debris": len([a for a in alerts if a.source == "debris"])
        }
    }

@router.post("/inject-fault")
async def inject_fault(
    fault_type: str,
    metric: str,
    duration_seconds: int = 60,
    spacecraft_id: str = "25544"
):
    """
    Inject synthetic fault for demo purposes.
    Allows controlled demonstration of anomaly detection.
    
    Available fault types:
    - battery_drift: Gradual voltage drop
    - temp_spike: Sudden temperature increase
    - attitude_oscillation: Sinusoidal oscillation
    - signal_degradation: Gradual signal loss
    """
    if metric not in TELEMETRY_METRICS:
        raise HTTPException(status_code=400, detail=f"Unknown metric: {metric}")
    
    valid_faults = ["battery_drift", "temp_spike", "attitude_oscillation", "signal_degradation"]
    if fault_type not in valid_faults:
        raise HTTPException(status_code=400, detail=f"Invalid fault type. Must be one of: {valid_faults}")
    
    simulator = get_simulator(spacecraft_id)
    simulator.inject_fault(fault_type, metric, duration_seconds)
    
    return {
        "status": "injected",
        "fault_type": fault_type,
        "metric": metric,
        "duration_seconds": duration_seconds,
        "spacecraft_id": spacecraft_id,
        "message": f"Fault '{fault_type}' injected on {metric} for {duration_seconds} seconds"
    }

@router.websocket("/ws/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    spacecraft_id: str = "25544"
):
    """
    WebSocket endpoint for live telemetry streaming.
    Pushes new readings and anomaly detection results in real-time.
    """
    await manager.connect(websocket)
    logger.info(f"WebSocket connection established for spacecraft {spacecraft_id}")
    
    try:
        while True:
            # Keep connection alive and receive any client messages
            data = await websocket.receive_text()
            # Echo back for connection verification
            await websocket.send_json({
                "type": "ack",
                "message": "Connection active"
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for spacecraft {spacecraft_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@router.get("/statistics")
async def get_statistics(
    spacecraft_id: str = "25544",
    db: Session = Depends(get_db)
):
    """
    Get anomaly detection statistics for all metrics.
    """
    detector = get_detector()
    stats = {}
    
    for metric in TELEMETRY_METRICS.keys():
        metric_stats = detector.get_statistics(metric)
        if metric_stats:
            stats[metric] = metric_stats
    
    return {
        "spacecraft_id": spacecraft_id,
        "statistics": stats
    }