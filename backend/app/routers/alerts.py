"""
Alerts API Router
Handles alert explanations using IBM Granite LLM.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert
from ..services.granite import get_granite_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{alert_id}/explain")
async def explain_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate natural language explanation for an alert using IBM Granite LLM.
    
    Args:
        alert_id: Database ID of the alert
        
    Returns:
        Alert with generated explanation
    """
    # Fetch alert from database
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if already explained
    if alert.explained and alert.explanation:
        return {
            "alert_id": alert.id,
            "explained": True,
            "explanation": alert.explanation,
            "cached": True
        }
    
    # Generate explanation using Granite LLM
    granite_service = get_granite_service()
    
    try:
        # Convert alert to dictionary
        alert_dict = {
            "id": alert.id,
            "spacecraft_id": alert.spacecraft_id,
            "source": alert.source,
            "response_category": alert.response_category,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat()
        }
        
        # Generate explanation
        explanation = granite_service.explain_alert(alert_dict)
        
        # Update alert in database
        alert.explanation = explanation
        alert.explained = True
        db.commit()
        
        logger.info(f"Generated explanation for alert {alert_id}")
        
        return {
            "alert_id": alert.id,
            "explained": True,
            "explanation": explanation,
            "cached": False
        }
        
    except Exception as e:
        logger.error(f"Error generating explanation for alert {alert_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        )

@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """
    Get alert details including explanation if available.
    
    Args:
        alert_id: Database ID of the alert
        
    Returns:
        Alert details
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {
        "id": alert.id,
        "spacecraft_id": alert.spacecraft_id,
        "source": alert.source,
        "response_category": alert.response_category,
        "severity": alert.severity,
        "message": alert.message,
        "timestamp": alert.timestamp.isoformat(),
        "explained": alert.explained,
        "explanation": alert.explanation
    }

@router.get("/")
async def list_alerts(
    skip: int = 0,
    limit: int = 50,
    severity: str = None,
    source: str = None,
    spacecraft_id: str = None,
    db: Session = Depends(get_db)
):
    """
    List alerts with pagination and filtering.
    
    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 50, max: 100)
        severity: Filter by severity (optional)
        source: Filter by source (optional)
        spacecraft_id: Filter by spacecraft ID (optional)
        
    Returns:
        Paginated list of alerts with metadata
    """
    # Enforce maximum limit
    limit = min(limit, 100)
    
    # Build query with filters
    query = db.query(Alert)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    if source:
        query = query.filter(Alert.source == source)
    if spacecraft_id:
        query = query.filter(Alert.spacecraft_id == spacecraft_id)
    
    # Get total count for pagination metadata
    total = query.count()
    
    # Apply pagination and ordering
    alerts = query.order_by(Alert.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Convert to dict
    alert_list = [
        {
            "id": alert.id,
            "spacecraft_id": alert.spacecraft_id,
            "source": alert.source,
            "response_category": alert.response_category,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat(),
            "explained": alert.explained,
            "explanation": alert.explanation if alert.explained else None
        }
        for alert in alerts
    ]
    
    return {
        "alerts": alert_list,
        "pagination": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
    }
