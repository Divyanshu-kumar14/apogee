"""
Health Monitor API Router
Handles telemetry streaming, anomaly detection, and health alerts.
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import TelemetryReading, Alert
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/status")
async def get_health_status(
    spacecraft_id: str = "25544",
    db: Session = Depends(get_db)
):
    """
    Get current health status snapshot for spacecraft.
    Returns latest reading per metric with anomaly status.
    """
    # TODO: Implement in Phase 2
    return {
        "spacecraft_id": spacecraft_id,
        "status": "placeholder",
        "message": "Health status endpoint - to be implemented in Phase 2"
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
    # TODO: Implement in Phase 2
    alerts = db.query(Alert).filter(
        Alert.spacecraft_id == spacecraft_id
    ).order_by(Alert.timestamp.desc()).limit(limit).all()
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "breakdown": {
            "health": len([a for a in alerts if a.source == "health"]),
            "debris": len([a for a in alerts if a.source == "debris"])
        }
    }

@router.post("/inject-fault")
async def inject_fault(
    fault_type: str,
    metric: str,
    duration_seconds: int = 60
):
    """
    Inject synthetic fault for demo purposes.
    Allows controlled demonstration of anomaly detection.
    """
    # TODO: Implement in Phase 2
    return {
        "status": "placeholder",
        "message": "Fault injection endpoint - to be implemented in Phase 2",
        "fault_type": fault_type,
        "metric": metric,
        "duration": duration_seconds
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
    await websocket.accept()
    logger.info(f"WebSocket connection established for spacecraft {spacecraft_id}")
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # TODO: Implement live streaming in Phase 2
            await websocket.send_json({
                "type": "placeholder",
                "message": "WebSocket streaming - to be implemented in Phase 2"
            })
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for spacecraft {spacecraft_id}")
