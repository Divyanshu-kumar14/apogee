"""
Discovery Module API Router
Handles TESS exoplanet transit detection and analysis.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import TransitCandidate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/candidates")
async def get_transit_candidates(
    min_confidence: float = 0.0,
    only_likely_planets: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get list of transit candidates from TESS data.
    Filtered by ML vetting confidence score.
    """
    query = db.query(TransitCandidate)
    
    if only_likely_planets:
        query = query.filter(TransitCandidate.is_likely_planet == True)
    
    if min_confidence > 0:
        query = query.filter(TransitCandidate.ml_vetting_score >= min_confidence)
    
    candidates = query.order_by(
        TransitCandidate.ml_vetting_score.desc()
    ).all()
    
    return {
        "candidates": candidates,
        "count": len(candidates)
    }

@router.get("/candidates/{tic_id}")
async def get_candidate_details(
    tic_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information for a specific transit candidate.
    """
    candidate = db.query(TransitCandidate).filter(
        TransitCandidate.tic_id == tic_id
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate

@router.get("/candidates/{tic_id}/lightcurve")
async def get_folded_lightcurve(
    tic_id: int,
    db: Session = Depends(get_db)
):
    """
    Get folded light curve data for visualization.
    Returns phase-folded flux data for charting.
    """
    candidate = db.query(TransitCandidate).filter(
        TransitCandidate.tic_id == tic_id
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # TODO: Implement in Phase 3 - load cached folded light curve data
    return {
        "tic_id": tic_id,
        "target_name": candidate.target_name,
        "period_days": candidate.period_days,
        "transit_depth": candidate.transit_depth,
        "is_likely_planet": candidate.is_likely_planet,
        "confidence": candidate.ml_vetting_score,
        "lightcurve": {
            "phase": [],
            "flux": []
        },
        "message": "Light curve data - to be implemented in Phase 3"
    }
