"""
Orbital Propagation Service
Uses SGP4 to propagate satellite orbits and compute conjunction risks.
Implements altitude-based pre-filtering for performance optimization.
"""
from sgp4.api import Satrec, jday
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class OrbitalPropagator:
    """
    Service for orbital propagation and conjunction analysis using SGP4.
    """
    
    def __init__(self, lookahead_hours: int = 48, step_minutes: int = 5):
        """
        Initialize orbital propagator.
        
        Args:
            lookahead_hours: Time window for propagation (default 48 hours)
            step_minutes: Time step for propagation (default 5 minutes)
        """
        self.lookahead_hours = lookahead_hours
        self.step_minutes = step_minutes
        logger.info(f"Orbital propagator initialized: {lookahead_hours}h lookahead, {step_minutes}min steps")
    
    def filter_by_altitude_band(
        self,
        spacecraft_apogee: float,
        spacecraft_perigee: float,
        catalog: List[Dict],
        buffer_km: float = 100.0
    ) -> List[Dict]:
        """
        Pre-filter catalog to objects whose orbital altitude overlaps
        with the spacecraft's altitude band (with buffer).
        
        This is CRITICAL for performance - reduces SGP4 propagation workload
        from ~16,000 objects to typically <500 objects for LEO spacecraft.
        
        Args:
            spacecraft_apogee: Spacecraft apogee altitude (km)
            spacecraft_perigee: Spacecraft perigee altitude (km)
            catalog: List of tracked objects with apogee/perigee data
            buffer_km: Altitude buffer for overlap check (default 100 km)
            
        Returns:
            Filtered list of objects in overlapping altitude band
        """
        sc_min_alt = spacecraft_perigee - buffer_km
        sc_max_alt = spacecraft_apogee + buffer_km
        
        filtered = []
        for obj in catalog:
            obj_apogee = obj.get('apogee_km', 0)
            obj_perigee = obj.get('perigee_km', 0)
            
            # Check if altitude bands overlap
            if obj_perigee <= sc_max_alt and obj_apogee >= sc_min_alt:
                filtered.append(obj)
        
        logger.info(f"Altitude filter: {len(catalog)} → {len(filtered)} objects "
                   f"(spacecraft band: {sc_min_alt:.1f}-{sc_max_alt:.1f} km)")
        
        return filtered
    
    def generate_time_points(
        self,
        start: Optional[datetime] = None,
        hours: Optional[int] = None,
        step_minutes: Optional[int] = None
    ) -> List[datetime]:
        """
        Generate time points for propagation.
        
        Args:
            start: Start time (default: now)
            hours: Duration in hours (default: self.lookahead_hours)
            step_minutes: Time step (default: self.step_minutes)
            
        Returns:
            List of datetime objects
        """
        if start is None:
            start = datetime.utcnow()
        if hours is None:
            hours = self.lookahead_hours
        if step_minutes is None:
            step_minutes = self.step_minutes
        
        points = []
        current = start
        end = start + timedelta(hours=hours)
        
        while current <= end:
            points.append(current)
            current += timedelta(minutes=step_minutes)
        
        logger.debug(f"Generated {len(points)} time points over {hours}h")
        return points
    
    def propagate_object(
        self,
        tle_line1: str,
        tle_line2: str,
        time_points: List[datetime]
    ) -> List[Tuple[float, float, float]]:
        """
        Propagate single object using SGP4.
        
        Args:
            tle_line1: TLE line 1
            tle_line2: TLE line 2
            time_points: List of times to propagate to
            
        Returns:
            List of (x, y, z) positions in km (TEME frame)
            Empty list if propagation fails
        """
        try:
            satellite = Satrec.twoline2rv(tle_line1, tle_line2)
            positions = []
            
            for t in time_points:
                jd, fr = jday(t.year, t.month, t.day, t.hour, t.minute, t.second)
                error_code, r, v = satellite.sgp4(jd, fr)
                
                if error_code == 0:  # No error
                    positions.append(r)
                else:
                    logger.warning(f"SGP4 error code {error_code} at {t}")
                    positions.append((0, 0, 0))  # Placeholder for failed propagation
            
            return positions
            
        except Exception as e:
            logger.error(f"Error propagating object: {e}")
            return []
    
    def compute_min_separation(
        self,
        pos1: List[Tuple[float, float, float]],
        pos2: List[Tuple[float, float, float]]
    ) -> Tuple[float, int, Tuple[float, float, float]]:
        """
        Compute minimum separation distance between two propagated orbits.
        
        Args:
            pos1: Position list for object 1
            pos2: Position list for object 2
            
        Returns:
            Tuple of (min_distance_km, time_index, relative_position_vector)
        """
        if len(pos1) != len(pos2):
            logger.error("Position lists must have same length")
            return (float('inf'), -1, (0, 0, 0))
        
        distances = []
        relative_positions = []
        
        for p1, p2 in zip(pos1, pos2):
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            dz = p1[2] - p2[2]
            dist = np.sqrt(dx**2 + dy**2 + dz**2)
            distances.append(dist)
            relative_positions.append((dx, dy, dz))
        
        min_idx = np.argmin(distances)
        min_distance = distances[min_idx]
        relative_pos = relative_positions[min_idx]
        
        return (min_distance, min_idx, relative_pos)
    
    def compute_relative_velocity(
        self,
        pos1: List[Tuple[float, float, float]],
        pos2: List[Tuple[float, float, float]],
        time_index: int,
        time_step_seconds: float
    ) -> float:
        """
        Compute relative velocity at closest approach.
        
        Args:
            pos1: Position list for object 1
            pos2: Position list for object 2
            time_index: Index of closest approach
            time_step_seconds: Time step between positions
            
        Returns:
            Relative velocity in km/s
        """
        if time_index <= 0 or time_index >= len(pos1) - 1:
            return 0.0
        
        # Compute velocities using finite differences
        # v = (pos[i+1] - pos[i-1]) / (2 * dt)
        
        # Object 1 velocity
        v1_x = (pos1[time_index + 1][0] - pos1[time_index - 1][0]) / (2 * time_step_seconds)
        v1_y = (pos1[time_index + 1][1] - pos1[time_index - 1][1]) / (2 * time_step_seconds)
        v1_z = (pos1[time_index + 1][2] - pos1[time_index - 1][2]) / (2 * time_step_seconds)
        
        # Object 2 velocity
        v2_x = (pos2[time_index + 1][0] - pos2[time_index - 1][0]) / (2 * time_step_seconds)
        v2_y = (pos2[time_index + 1][1] - pos2[time_index - 1][1]) / (2 * time_step_seconds)
        v2_z = (pos2[time_index + 1][2] - pos2[time_index - 1][2]) / (2 * time_step_seconds)
        
        # Relative velocity magnitude
        rel_v_x = v1_x - v2_x
        rel_v_y = v1_y - v2_y
        rel_v_z = v1_z - v2_z
        
        rel_velocity = np.sqrt(rel_v_x**2 + rel_v_y**2 + rel_v_z**2)
        
        return rel_velocity
    
    def calculate_risk_score(
        self,
        min_distance_km: float,
        relative_velocity_kmps: float,
        distance_threshold_km: float = 10.0,
        velocity_weight: float = 0.3
    ) -> float:
        """
        Calculate relative risk score (0-100) for a conjunction.
        
        Formula:
        - Distance component: exponential decay from threshold
        - Velocity component: linear scaling up to 15 km/s
        - Combined: weighted sum, clamped to [0, 100]
        
        This is NOT a collision probability - it's a relative risk indicator
        for prioritizing conjunctions. TLE positional uncertainty is too high
        for precise probability calculations.
        
        Args:
            min_distance_km: Minimum separation distance
            relative_velocity_kmps: Relative velocity at closest approach
            distance_threshold_km: Distance below which risk is maximum (default 10 km)
            velocity_weight: Weight for velocity component 0-1 (default 0.3)
            
        Returns:
            Risk score from 0 (no risk) to 100 (critical risk)
        """
        # Distance component (exponential decay)
        # Risk = 100 at distance = 0, decays to ~0 at 50km
        distance_score = 100 * np.exp(-min_distance_km / distance_threshold_km)
        
        # Velocity component (linear scaling)
        # Higher relative velocity = higher risk (less time to react)
        velocity_score = min(100, (relative_velocity_kmps / 15.0) * 100)
        
        # Weighted combination
        distance_weight = 1.0 - velocity_weight
        risk_score = (distance_weight * distance_score + 
                      velocity_weight * velocity_score)
        
        return float(np.clip(risk_score, 0, 100))
    
    def analyze_conjunction(
        self,
        spacecraft_tle: Dict,
        object_tle: Dict,
        time_points: Optional[List[datetime]] = None
    ) -> Optional[Dict]:
        """
        Analyze conjunction between spacecraft and tracked object.
        
        Args:
            spacecraft_tle: Spacecraft TLE data
            object_tle: Tracked object TLE data
            time_points: Time points for propagation (default: auto-generate)
            
        Returns:
            Dictionary with conjunction analysis results or None if propagation fails
        """
        if time_points is None:
            time_points = self.generate_time_points()
        
        # Propagate both objects
        sc_positions = self.propagate_object(
            spacecraft_tle['tle_line1'],
            spacecraft_tle['tle_line2'],
            time_points
        )
        
        obj_positions = self.propagate_object(
            object_tle['tle_line1'],
            object_tle['tle_line2'],
            time_points
        )
        
        if not sc_positions or not obj_positions:
            logger.warning(f"Failed to propagate spacecraft or object {object_tle.get('norad_id')}")
            return None
        
        # Compute minimum separation
        min_distance, time_idx, rel_pos = self.compute_min_separation(sc_positions, obj_positions)
        
        # Compute relative velocity
        time_step_seconds = self.step_minutes * 60
        rel_velocity = self.compute_relative_velocity(
            sc_positions, obj_positions, time_idx, time_step_seconds
        )
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(min_distance, rel_velocity)
        
        # Time of closest approach
        tca = time_points[time_idx] if time_idx >= 0 else datetime.utcnow()
        
        return {
            'object_norad_id': object_tle['norad_id'],
            'object_name': object_tle['name'],
            'closest_approach_km': min_distance,
            'relative_velocity_kmps': rel_velocity,
            'risk_score': risk_score,
            'time_of_closest_approach': tca,
            'relative_position': rel_pos
        }
