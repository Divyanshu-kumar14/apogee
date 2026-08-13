"""
Debris Risk API Router
Handles orbital conjunction analysis and risk assessment.
"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import TrackedObject, ConjunctionRisk, Alert
from ..services.celestrak import CelesTrakService
from ..services.orbital import OrbitalPropagator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
celestrak_service = CelesTrakService()
orbital_propagator = OrbitalPropagator(lookahead_hours=48, step_minutes=5)

def compute_debris_risks_task(spacecraft_id: str, db: Session):
    """
    Background task to compute debris conjunction risks.
    
    Steps:
    1. Fetch spacecraft TLE
    2. Fetch catalog subset
    3. Apply altitude-based pre-filtering
    4. Propagate orbits using SGP4
    5. Compute conjunction risks
    6. Store results and create alerts
    """
    try:
        logger.info(f"Starting debris risk computation for spacecraft {spacecraft_id}")
        
        # Step 1: Fetch spacecraft TLE
        spacecraft_tle_data = celestrak_service.fetch_spacecraft_tle(int(spacecraft_id))
        if not spacecraft_tle_data:
            logger.error(f"Failed to fetch TLE for spacecraft {spacecraft_id}")
            return
        
        spacecraft_tle = celestrak_service.parse_tle_data(spacecraft_tle_data)
        logger.info(f"Spacecraft: {spacecraft_tle['name']} (NORAD {spacecraft_tle['norad_id']})")
        
        # Store/update spacecraft in database
        spacecraft_obj = db.query(TrackedObject).filter(
            TrackedObject.norad_id == spacecraft_tle['norad_id']
        ).first()
        
        valid_keys = ['norad_id', 'name', 'tle_line1', 'tle_line2', 'apogee_km', 'perigee_km', 'last_updated']
        spacecraft_kwargs = {k: v for k, v in spacecraft_tle.items() if k in valid_keys}
        
        if spacecraft_obj:
            # Update existing
            spacecraft_obj.name = spacecraft_tle['name']
            spacecraft_obj.tle_line1 = spacecraft_tle['tle_line1']
            spacecraft_obj.tle_line2 = spacecraft_tle['tle_line2']
            spacecraft_obj.apogee_km = spacecraft_tle['apogee_km']
            spacecraft_obj.perigee_km = spacecraft_tle['perigee_km']
            spacecraft_obj.last_updated = spacecraft_tle['last_updated']
        else:
            # Create new
            spacecraft_obj = TrackedObject(**spacecraft_kwargs)
            db.add(spacecraft_obj)
        
        db.commit()
        
        # Step 2: Fetch catalog subset (limit to 1000 for demo)
        catalog_data = celestrak_service.fetch_catalog_subset(group="active", limit=1000)
        logger.info(f"Fetched {len(catalog_data)} objects from catalog")
        
        # Parse catalog data
        catalog = [celestrak_service.parse_tle_data(obj) for obj in catalog_data]
        
        # Store catalog objects in database
        for obj_data in catalog:
            obj = db.query(TrackedObject).filter(
                TrackedObject.norad_id == obj_data['norad_id']
            ).first()
            
            obj_kwargs = {k: v for k, v in obj_data.items() if k in valid_keys}
            
            if obj:
                # Update existing
                obj.name = obj_data['name']
                obj.tle_line1 = obj_data['tle_line1']
                obj.tle_line2 = obj_data['tle_line2']
                obj.apogee_km = obj_data['apogee_km']
                obj.perigee_km = obj_data['perigee_km']
                obj.last_updated = obj_data['last_updated']
            else:
                # Create new
                obj = TrackedObject(**obj_kwargs)
                db.add(obj)
        
        db.commit()
        logger.info("Catalog objects stored in database")
        
        # Step 3: Apply altitude-based pre-filtering
        filtered_catalog = orbital_propagator.filter_by_altitude_band(
            spacecraft_apogee=spacecraft_tle['apogee_km'],
            spacecraft_perigee=spacecraft_tle['perigee_km'],
            catalog=catalog,
            buffer_km=100.0
        )
        
        logger.info(f"Pre-filtering reduced catalog from {len(catalog)} to {len(filtered_catalog)} objects")
        
        # Step 4 & 5: Propagate and analyze conjunctions
        time_points = orbital_propagator.generate_time_points()
        risks_computed = 0
        alerts_created = 0
        
        # Clear old risks for this spacecraft
        db.query(ConjunctionRisk).filter(
            ConjunctionRisk.spacecraft_id == spacecraft_id
        ).delete()
        db.commit()
        
        for obj_data in filtered_catalog:
            # Skip self
            if obj_data['norad_id'] == spacecraft_tle['norad_id']:
                continue
            
            # Analyze conjunction
            result = orbital_propagator.analyze_conjunction(
                spacecraft_tle=spacecraft_tle,
                object_tle=obj_data,
                time_points=time_points
            )
            
            if result is None:
                continue
            
            # Store conjunction risk
            risk = ConjunctionRisk(
                spacecraft_id=spacecraft_id,
                object_norad_id=result['object_norad_id'],
                closest_approach_km=result['closest_approach_km'],
                relative_velocity_kmps=result['relative_velocity_kmps'],
                risk_score=result['risk_score'],
                computed_at=datetime.utcnow()
            )
            db.add(risk)
            risks_computed += 1
            
            # Create alert if risk is significant (score >= 40)
            if result['risk_score'] >= 40:
                severity = "critical" if result['risk_score'] >= 70 else "watch"
                
                message = (
                    f"Conjunction detected with {result['object_name']} "
                    f"(NORAD {result['object_norad_id']}). "
                    f"Closest approach: {result['closest_approach_km']:.2f} km "
                    f"at relative velocity {result['relative_velocity_kmps']:.2f} km/s. "
                    f"Risk score: {result['risk_score']:.1f}/100. "
                    f"TCA: {result['time_of_closest_approach'].strftime('%Y-%m-%d %H:%M UTC')}"
                )
                
                alert = Alert(
                    spacecraft_id=spacecraft_id,
                    source="debris",
                    response_category="flight_dynamics",
                    severity=severity,
                    message=message,
                    timestamp=datetime.utcnow(),
                    explained=False
                )
                db.add(alert)
                alerts_created += 1
        
        db.commit()
        
        logger.info(f"Debris risk computation complete: {risks_computed} risks computed, {alerts_created} alerts created")
        
    except Exception as e:
        logger.error(f"Error in debris risk computation: {e}", exc_info=True)
        db.rollback()

@router.post("/refresh")
async def refresh_debris_data(
    spacecraft_id: str = "25544",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Trigger debris risk computation (background task).
    Returns immediately with task status.
    
    This endpoint:
    1. Fetches TLEs from CelesTrak
    2. Applies altitude-based pre-filtering
    3. Runs SGP4 propagation
    4. Computes conjunction risks
    5. Creates alerts for high-risk conjunctions
    """
    logger.info(f"Debris refresh requested for spacecraft {spacecraft_id}")
    
    # Add background task
    background_tasks.add_task(compute_debris_risks_task, spacecraft_id, db)
    
    return {
        "status": "started",
        "message": f"Debris risk computation started for spacecraft {spacecraft_id}",
        "spacecraft_id": spacecraft_id,
        "note": "This is a background task. Check /api/debris/risks for results."
    }

@router.get("/risks")
async def get_debris_risks(
    spacecraft_id: str = "25544",
    min_risk_score: float = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get sorted list of conjunction risks for spacecraft.
    Returns risks above minimum score threshold, sorted by risk score descending.
    """
    risks = db.query(ConjunctionRisk).filter(
        ConjunctionRisk.spacecraft_id == spacecraft_id,
        ConjunctionRisk.risk_score >= min_risk_score
    ).order_by(
        ConjunctionRisk.risk_score.desc()
    ).limit(limit).all()
    
    # Get object names
    risk_list = []
    for risk in risks:
        obj = db.query(TrackedObject).filter(
            TrackedObject.norad_id == risk.object_norad_id
        ).first()
        
        risk_list.append({
            "id": risk.id,
            "object_norad_id": risk.object_norad_id,
            "object_name": obj.name if obj else "Unknown",
            "closest_approach_km": risk.closest_approach_km,
            "relative_velocity_kmps": risk.relative_velocity_kmps,
            "risk_score": risk.risk_score,
            "computed_at": risk.computed_at.isoformat()
        })
    
    return {
        "risks": risk_list,
        "count": len(risk_list),
        "spacecraft_id": spacecraft_id
    }

@router.get("/objects")
async def get_tracked_objects(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of tracked objects from TLE catalog.
    Useful for debugging and verification.
    """
    objects = db.query(TrackedObject).limit(limit).all()
    
    object_list = [{
        "norad_id": obj.norad_id,
        "name": obj.name,
        "apogee_km": obj.apogee_km,
        "perigee_km": obj.perigee_km,
        "last_updated": obj.last_updated.isoformat() if obj.last_updated else None
    } for obj in objects]
    
    return {
        "objects": object_list,
        "count": len(object_list)
    }