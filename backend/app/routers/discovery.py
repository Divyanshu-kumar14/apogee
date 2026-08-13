"""
Discovery Module API Router
Handles TESS data processing, transit detection, and ML vetting.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import TransitCandidate
from ..services.tess import get_tess_service
from ..services.vetting import get_vetting_classifier
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/candidates")
async def get_transit_candidates(
    limit: int = 50,
    min_confidence: float = 0.0,
    db: Session = Depends(get_db)
):
    """
    Get list of transit candidates from database.
    
    Args:
        limit: Maximum number of candidates to return
        min_confidence: Minimum vetting confidence (0.0 to 1.0)
        
    Returns:
        List of transit candidates with vetting results
    """
    candidates = db.query(TransitCandidate).filter(
        TransitCandidate.vetting_confidence >= min_confidence
    ).order_by(
        TransitCandidate.vetting_confidence.desc()
    ).limit(limit).all()
    
    candidate_list = [{
        "id": c.id,
        "tic_id": c.tic_id,
        "sector": c.sector,
        "period": c.period,
        "epoch": c.epoch,
        "depth": c.depth,
        "duration": c.duration,
        "snr": c.snr,
        "disposition": c.disposition,
        "vetting_confidence": c.vetting_confidence,
        "discovered_at": c.discovered_at.isoformat()
    } for c in candidates]
    
    return {
        "candidates": candidate_list,
        "count": len(candidate_list)
    }

@router.post("/search")
async def search_transits(
    sector: int,
    camera: int,
    ccd: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Search for transit candidates in a specific TESS sector/camera/CCD.
    Runs as background task due to computational intensity.
    
    Args:
        sector: TESS sector number (1-69+)
        camera: Camera number (1-4)
        ccd: CCD number (1-4)
        
    Returns:
        Task status and estimated completion time
    """
    # Validate inputs
    if not (1 <= sector <= 100):
        raise HTTPException(status_code=400, detail="Sector must be between 1 and 100")
    if not (1 <= camera <= 4):
        raise HTTPException(status_code=400, detail="Camera must be between 1 and 4")
    if not (1 <= ccd <= 4):
        raise HTTPException(status_code=400, detail="CCD must be between 1 and 4")
    
    # Add background task
    background_tasks.add_task(
        process_tess_sector,
        sector, camera, ccd, db
    )
    
    return {
        "status": "processing",
        "sector": sector,
        "camera": camera,
        "ccd": ccd,
        "message": f"Transit search started for Sector {sector}, Camera {camera}, CCD {ccd}",
        "estimated_time": "2-5 minutes"
    }

async def process_tess_sector(sector: int, camera: int, ccd: int, db: Session):
    """
    Background task to process TESS sector and detect transits.
    
    Args:
        sector: TESS sector number
        camera: Camera number
        ccd: CCD number
        db: Database session
    """
    logger.info(f"Starting transit search: Sector {sector}, Camera {camera}, CCD {ccd}")
    
    tess_service = get_tess_service()
    vetting_classifier = get_vetting_classifier()
    
    try:
        # Search for observations
        observations = tess_service.search_observations(sector, camera, ccd)
        logger.info(f"Found {len(observations)} observations to process")
        
        candidates_found = 0
        
        # Process each observation
        for obs in observations:
            tic_id = obs["tic_id"]
            
            # Fetch light curve
            light_curve = tess_service.fetch_light_curve(tic_id, sector)
            if light_curve is None:
                continue
            
            # Run BLS periodogram
            bls_results = tess_service.run_bls(
                light_curve["time"],
                light_curve["flux"],
                light_curve["flux_err"]
            )
            
            # Check if signal is significant (SNR > 7)
            if bls_results["snr"] < 7:
                continue
            
            # Extract features for ML vetting
            features = tess_service.extract_features(
                light_curve["time"],
                light_curve["flux"],
                bls_results
            )
            
            # ML vetting
            is_planet, confidence, disposition = vetting_classifier.predict(features)
            
            # Only save if confidence > 0.5
            if confidence < 0.5:
                continue
            
            # Check if candidate already exists
            existing = db.query(TransitCandidate).filter(
                TransitCandidate.tic_id == tic_id,
                TransitCandidate.sector == sector
            ).first()
            
            if existing:
                # Update existing candidate
                existing.period = bls_results["period"]
                existing.epoch = bls_results["t0"]
                existing.depth = bls_results["depth"]
                existing.duration = bls_results["duration"]
                existing.snr = bls_results["snr"]
                existing.disposition = disposition
                existing.vetting_confidence = confidence
            else:
                # Create new candidate
                candidate = TransitCandidate(
                    tic_id=tic_id,
                    sector=sector,
                    period=bls_results["period"],
                    epoch=bls_results["t0"],
                    depth=bls_results["depth"],
                    duration=bls_results["duration"],
                    snr=bls_results["snr"],
                    disposition=disposition,
                    vetting_confidence=confidence,
                    discovered_at=datetime.utcnow()
                )
                db.add(candidate)
            
            candidates_found += 1
            
            # Commit every 10 candidates
            if candidates_found % 10 == 0:
                db.commit()
        
        # Final commit
        db.commit()
        
        logger.info(f"Transit search complete: {candidates_found} candidates found")
        
    except Exception as e:
        logger.error(f"Error processing TESS sector: {e}", exc_info=True)
        db.rollback()

@router.get("/candidate/{candidate_id}")
async def get_candidate_details(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific transit candidate.
    
    Args:
        candidate_id: Database ID of the candidate
        
    Returns:
        Detailed candidate information including light curve data
    """
    candidate = db.query(TransitCandidate).filter(
        TransitCandidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Fetch light curve data
    tess_service = get_tess_service()
    light_curve = tess_service.fetch_light_curve(candidate.tic_id, candidate.sector)
    
    if light_curve is None:
        raise HTTPException(status_code=500, detail="Failed to fetch light curve data")
    
    # Run BLS again to get full results
    bls_results = tess_service.run_bls(
        light_curve["time"],
        light_curve["flux"],
        light_curve["flux_err"]
    )
    
    return {
        "candidate": {
            "id": candidate.id,
            "tic_id": candidate.tic_id,
            "sector": candidate.sector,
            "period": candidate.period,
            "epoch": candidate.epoch,
            "depth": candidate.depth,
            "duration": candidate.duration,
            "snr": candidate.snr,
            "disposition": candidate.disposition,
            "vetting_confidence": candidate.vetting_confidence,
            "discovered_at": candidate.discovered_at.isoformat()
        },
        "light_curve": {
            "time": light_curve["time"].tolist(),
            "flux": light_curve["flux"].tolist(),
            "flux_err": light_curve["flux_err"].tolist()
        },
        "bls_results": {
            "period": bls_results["period"],
            "power": bls_results["power"],
            "duration": bls_results["duration"],
            "t0": bls_results["t0"],
            "depth": bls_results["depth"],
            "snr": bls_results["snr"]
        }
    }

@router.get("/statistics")
async def get_discovery_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about transit candidates in the database.
    
    Returns:
        Statistics including counts by disposition and confidence ranges
    """
    total_candidates = db.query(TransitCandidate).count()
    
    # Count by disposition
    dispositions = {}
    for disp in ["CONFIRMED", "CANDIDATE", "LIKELY", "FALSE_POSITIVE", "LIKELY_FP", "UNCERTAIN"]:
        count = db.query(TransitCandidate).filter(
            TransitCandidate.disposition == disp
        ).count()
        dispositions[disp] = count
    
    # Count by confidence ranges
    high_confidence = db.query(TransitCandidate).filter(
        TransitCandidate.vetting_confidence >= 0.8
    ).count()
    
    medium_confidence = db.query(TransitCandidate).filter(
        TransitCandidate.vetting_confidence >= 0.6,
        TransitCandidate.vetting_confidence < 0.8
    ).count()
    
    low_confidence = db.query(TransitCandidate).filter(
        TransitCandidate.vetting_confidence < 0.6
    ).count()
    
    return {
        "total_candidates": total_candidates,
        "by_disposition": dispositions,
        "by_confidence": {
            "high": high_confidence,
            "medium": medium_confidence,
            "low": low_confidence
        }
    }

@router.get("/feature-importance")
async def get_feature_importance():
    """
    Get feature importance scores from the ML vetting classifier.
    
    Returns:
        Dictionary of feature names and their importance scores
    """
    classifier = get_vetting_classifier()
    importance = classifier.get_feature_importance()
    
    # Sort by importance
    sorted_importance = dict(sorted(
        importance.items(),
        key=lambda x: x[1],
        reverse=True
    ))
    
    return {
        "feature_importance": sorted_importance,
        "model_type": "RandomForestClassifier",
        "n_features": len(importance)
    }