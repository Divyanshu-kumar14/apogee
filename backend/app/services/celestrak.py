"""
CelesTrak TLE Data Service
Fetches Two-Line Element (TLE) data from CelesTrak API.
Implements caching to avoid live API calls during demo.
"""
import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging
from .cache import cache_tle_data

logger = logging.getLogger(__name__)

class CelesTrakService:
    """
    Service for fetching and caching TLE data from CelesTrak.
    """
    
    BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", "data", "tles")
    
    def __init__(self):
        """Initialize CelesTrak service and ensure cache directory exists."""
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        logger.info(f"CelesTrak cache directory: {self.CACHE_DIR}")
    
    @cache_tle_data
    def fetch_spacecraft_tle(self, norad_id: int, use_cache: bool = True) -> Optional[Dict]:
        """
        Fetch TLE for a specific spacecraft by NORAD ID.
        Now with automatic memory caching (1 hour TTL).
        
        Args:
            norad_id: NORAD catalog number
            use_cache: If True, check file cache before making API call
            
        Returns:
            Dictionary with TLE data or None if not found
        """
        cache_file = os.path.join(self.CACHE_DIR, f"spacecraft_{norad_id}.json")
        
        # Check file cache first
        if use_cache and os.path.exists(cache_file):
            logger.info(f"Loading spacecraft {norad_id} from file cache")
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Fetch from API
        logger.info(f"Fetching spacecraft {norad_id} from CelesTrak API")
        try:
            params = {
                "CATNR": norad_id,
                "FORMAT": "JSON"
            }
            headers = {
                "User-Agent": "ApogeeSpaceDebrisDemo/1.0 (contact@apogee.demo)"
            }
            response = requests.get(self.BASE_URL, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data or len(data) == 0:
                logger.warning(f"No TLE data found for NORAD ID {norad_id}")
                return None
            
            tle_data = data[0]  # First result
            
            # Add metadata
            tle_data['fetched_at'] = datetime.utcnow().isoformat()
            tle_data['norad_id'] = norad_id
            
            # Cache the result to file
            with open(cache_file, 'w') as f:
                json.dump(tle_data, f, indent=2)
            
            logger.info(f"Successfully fetched and cached TLE for {tle_data.get('OBJECT_NAME', 'Unknown')}")
            return tle_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching TLE for NORAD ID {norad_id}: {e}")
            return None
    
    def fetch_catalog_subset(
        self, 
        group: str = "active", 
        limit: Optional[int] = None,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        Fetch a subset of the TLE catalog from CelesTrak.
        
        Args:
            group: CelesTrak group name (e.g., "active", "stations", "weather")
            limit: Maximum number of objects to return (None = all)
            use_cache: If True, check cache before making API call
            
        Returns:
            List of TLE data dictionaries
        """
        cache_file = os.path.join(self.CACHE_DIR, f"catalog_{group}.json")
        
        # Check cache first
        if use_cache and os.path.exists(cache_file):
            logger.info(f"Loading catalog group '{group}' from cache")
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if limit:
                    return data[:limit]
                return data
        
        # Fetch from API
        logger.info(f"Fetching catalog group '{group}' from CelesTrak")
        try:
            params = {
                "GROUP": group,
                "FORMAT": "JSON"
            }
            headers = {
                "User-Agent": "ApogeeSpaceDebrisDemo/1.0 (contact@apogee.demo)"
            }
            response = requests.get(self.BASE_URL, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Add metadata to each entry
            for entry in data:
                entry['fetched_at'] = datetime.utcnow().isoformat()
                entry['catalog_group'] = group
            
            # Cache the result
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Successfully fetched and cached {len(data)} objects from group '{group}'")
            
            if limit:
                return data[:limit]
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching catalog group '{group}': {e}")
            return []
    
    def parse_tle_data(self, tle_data: Dict) -> Dict:
        """
        Parse CelesTrak JSON TLE data into standardized format.
        
        Args:
            tle_data: Raw TLE data from CelesTrak API
            
        Returns:
            Parsed TLE data with computed orbital parameters
        """
        # Extract TLE lines if present
        tle_line1 = tle_data.get('TLE_LINE1', '')
        tle_line2 = tle_data.get('TLE_LINE2', '')
        
        try:
            if tle_line2:
                # Inclination (degrees)
                inclination = float(tle_line2[8:16].strip())
                
                # Mean motion (revolutions per day)
                mean_motion = float(tle_line2[52:63].strip())
            else:
                inclination = float(tle_data.get('INCLINATION', 0))
                mean_motion = float(tle_data.get('MEAN_MOTION', 0))
                
            # Compute approximate orbital period (minutes)
            period_minutes = 1440.0 / mean_motion if mean_motion > 0 else 0
            
            # Compute approximate semi-major axis (km)
            # Using simplified formula: a = (μ * T² / 4π²)^(1/3)
            # where μ = 398600.4418 km³/s² (Earth's gravitational parameter)
            # and T is period in seconds
            mu = 398600.4418  # km³/s²
            period_seconds = period_minutes * 60
            semi_major_axis = (mu * (period_seconds / (2 * 3.14159265359))**2)**(1/3) if period_seconds > 0 else 0
            
            # Earth radius
            earth_radius = 6371.0  # km
            
            # Approximate apogee and perigee (simplified circular orbit assumption)
            # For more accurate calculation, would need eccentricity
            altitude = semi_major_axis - earth_radius if semi_major_axis > 0 else 500
            
            return {
                'norad_id': int(tle_data.get('NORAD_CAT_ID', 0)),
                'name': tle_data.get('OBJECT_NAME', 'Unknown'),
                'tle_line1': tle_line1,
                'tle_line2': tle_line2,
                'inclination': inclination,
                'mean_motion': mean_motion,
                'period_minutes': period_minutes,
                'semi_major_axis_km': semi_major_axis,
                'apogee_km': altitude + 50,  # Rough estimate with buffer
                'perigee_km': altitude - 50,  # Rough estimate with buffer
                'last_updated': datetime.utcnow()
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"Error parsing TLE data: {e}")
            # Return basic data even if parsing fails
            return {
                'norad_id': int(tle_data.get('NORAD_CAT_ID', 0)),
                'name': tle_data.get('OBJECT_NAME', 'Unknown'),
                'tle_line1': tle_line1,
                'tle_line2': tle_line2,
                'apogee_km': 500.0,  # Default fallback
                'perigee_km': 400.0,  # Default fallback
                'last_updated': datetime.utcnow()
            }
    
    def clear_cache(self):
        """Clear all cached TLE data."""
        import glob
        cache_files = glob.glob(os.path.join(self.CACHE_DIR, "*.json"))
        for file in cache_files:
            os.remove(file)
        logger.info(f"Cleared {len(cache_files)} cached TLE files")
