"""
TESS Data Service
Fetches and processes TESS light curves from MAST archive.
"""
import os
import logging
from typing import List, Dict, Optional
import numpy as np
from astropy.io import fits
from astropy.timeseries import BoxLeastSquares
import requests
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# MAST API endpoints
MAST_API_URL = "https://mast.stsci.edu/api/v0.1"
TESS_DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../data/tess")

# Ensure data directory exists
os.makedirs(TESS_DATA_DIR, exist_ok=True)

class TESSDataService:
    """
    Service for fetching and caching TESS light curve data.
    Uses MAST API for data retrieval.
    """
    
    def __init__(self):
        """Initialize TESS data service."""
        self.cache_dir = TESS_DATA_DIR
        logger.info(f"TESS data service initialized. Cache dir: {self.cache_dir}")
    
    def search_observations(self, sector: int, camera: int, ccd: int) -> List[Dict]:
        """
        Search for TESS observations in a specific sector/camera/CCD.
        
        Args:
            sector: TESS sector number (1-69+)
            camera: Camera number (1-4)
            ccd: CCD number (1-4)
            
        Returns:
            List of observation metadata dictionaries
        """
        logger.info(f"Searching TESS observations: Sector {sector}, Camera {camera}, CCD {ccd}")
        
        # For demo purposes, we'll use mock data
        # In production, this would query MAST API
        mock_observations = self._generate_mock_observations(sector, camera, ccd)
        
        logger.info(f"Found {len(mock_observations)} observations")
        return mock_observations
    
    def _generate_mock_observations(self, sector: int, camera: int, ccd: int) -> List[Dict]:
        """
        Generate mock TESS observations for demo purposes.
        In production, this would be replaced with actual MAST API calls.
        
        Args:
            sector: TESS sector number
            camera: Camera number
            ccd: CCD number
            
        Returns:
            List of mock observation metadata
        """
        # Generate 10-20 mock targets per sector/camera/CCD
        num_targets = np.random.randint(10, 21)
        observations = []
        
        for i in range(num_targets):
            tic_id = sector * 1000000 + camera * 10000 + ccd * 100 + i
            
            obs = {
                "tic_id": tic_id,
                "sector": sector,
                "camera": camera,
                "ccd": ccd,
                "ra": np.random.uniform(0, 360),
                "dec": np.random.uniform(-90, 90),
                "tmag": np.random.uniform(8, 16),  # TESS magnitude
                "has_data": True
            }
            observations.append(obs)
        
        return observations
    
    def fetch_light_curve(self, tic_id: int, sector: int) -> Optional[Dict]:
        """
        Fetch light curve data for a specific TIC ID and sector.
        
        Args:
            tic_id: TESS Input Catalog ID
            sector: TESS sector number
            
        Returns:
            Dictionary with time, flux, and flux_err arrays, or None if not found
        """
        cache_file = os.path.join(self.cache_dir, f"tic_{tic_id}_s{sector:02d}.json")
        
        # Check cache first
        if os.path.exists(cache_file):
            logger.debug(f"Loading cached light curve: TIC {tic_id}, Sector {sector}")
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return {
                    "time": np.array(data["time"]),
                    "flux": np.array(data["flux"]),
                    "flux_err": np.array(data["flux_err"]),
                    "tic_id": tic_id,
                    "sector": sector
                }
        
        # Generate mock light curve (in production, fetch from MAST)
        logger.info(f"Generating mock light curve: TIC {tic_id}, Sector {sector}")
        light_curve = self._generate_mock_light_curve(tic_id, sector)
        
        # Cache the data
        cache_data = {
            "time": light_curve["time"].tolist(),
            "flux": light_curve["flux"].tolist(),
            "flux_err": light_curve["flux_err"].tolist(),
            "tic_id": tic_id,
            "sector": sector,
            "cached_at": datetime.utcnow().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)
        
        return light_curve
    
    def _generate_mock_light_curve(self, tic_id: int, sector: int) -> Dict:
        """
        Generate mock TESS light curve with potential transit signals.
        
        Args:
            tic_id: TESS Input Catalog ID
            sector: TESS sector number
            
        Returns:
            Dictionary with time, flux, and flux_err arrays
        """
        # TESS observes for ~27 days per sector
        # 2-minute cadence = ~19,440 data points per sector
        num_points = 19440
        
        # Time array (days)
        time = np.linspace(0, 27, num_points)
        
        # Base flux (normalized to 1.0)
        flux = np.ones(num_points)
        
        # Add stellar variability (sinusoidal)
        variability_period = np.random.uniform(5, 20)  # days
        variability_amplitude = np.random.uniform(0.001, 0.01)
        flux += variability_amplitude * np.sin(2 * np.pi * time / variability_period)
        
        # Add noise
        noise_level = np.random.uniform(0.0005, 0.002)
        flux += np.random.normal(0, noise_level, num_points)
        
        # 30% chance of having a transit signal
        has_transit = np.random.random() < 0.3
        
        if has_transit:
            # Transit parameters
            period = np.random.uniform(1.5, 15)  # days
            depth = np.random.uniform(0.002, 0.02)  # 0.2% to 2% depth
            duration = np.random.uniform(0.05, 0.15)  # hours -> days
            t0 = np.random.uniform(0, period)  # first transit time
            
            # Add transit signal
            for transit_time in np.arange(t0, 27, period):
                # Box-shaped transit
                in_transit = np.abs(time - transit_time) < (duration / 2)
                flux[in_transit] -= depth
        
        # Flux errors (photon noise)
        flux_err = np.full(num_points, noise_level)
        
        return {
            "time": time,
            "flux": flux,
            "flux_err": flux_err,
            "tic_id": tic_id,
            "sector": sector,
            "has_injected_transit": has_transit
        }
    
    def run_bls(self, time: np.ndarray, flux: np.ndarray, flux_err: np.ndarray) -> Dict:
        """
        Run Box Least Squares (BLS) periodogram to detect transit signals.
        
        Args:
            time: Time array (days)
            flux: Flux array (normalized)
            flux_err: Flux error array
            
        Returns:
            Dictionary with BLS results
        """
        logger.debug("Running BLS periodogram")
        
        # Normalize flux (remove mean, divide by std)
        flux_normalized = (flux - np.mean(flux)) / np.std(flux)
        
        # Create BLS model
        model = BoxLeastSquares(time, flux_normalized)
        
        # Define period grid (0.5 to 20 days)
        periods = np.linspace(0.5, 20, 10000)
        
        # Run BLS
        results = model.power(periods, duration=np.linspace(0.05, 0.3, 10))
        
        # Find best period
        best_idx = np.argmax(results.power)
        best_period = results.period[best_idx]
        best_power = results.power[best_idx]
        best_duration = results.duration[best_idx]
        best_t0 = results.transit_time[best_idx]
        best_depth = results.depth[best_idx]
        
        # Calculate signal-to-noise ratio
        snr = best_power / np.median(results.power)
        
        logger.info(f"BLS results: Period={best_period:.3f}d, Power={best_power:.3f}, SNR={snr:.2f}")
        
        return {
            "period": float(best_period),
            "power": float(best_power),
            "duration": float(best_duration),
            "t0": float(best_t0),
            "depth": float(best_depth),
            "snr": float(snr),
            "periods": periods.tolist(),
            "power_spectrum": results.power.tolist()
        }
    
    def extract_features(self, time: np.ndarray, flux: np.ndarray, 
                        bls_results: Dict) -> Dict:
        """
        Extract features for ML-based transit vetting.
        
        Args:
            time: Time array
            flux: Flux array
            bls_results: BLS periodogram results
            
        Returns:
            Dictionary of features for ML classifier
        """
        # Fold light curve at detected period
        period = bls_results["period"]
        t0 = bls_results["t0"]
        phase = ((time - t0) % period) / period
        
        # Sort by phase
        sort_idx = np.argsort(phase)
        phase_sorted = phase[sort_idx]
        flux_sorted = flux[sort_idx]
        
        # Features for ML vetting
        features = {
            # BLS features
            "bls_power": bls_results["power"],
            "bls_snr": bls_results["snr"],
            "period": bls_results["period"],
            "depth": bls_results["depth"],
            "duration": bls_results["duration"],
            
            # Light curve statistics
            "flux_std": float(np.std(flux)),
            "flux_mad": float(np.median(np.abs(flux - np.median(flux)))),
            "flux_skew": float(self._calculate_skewness(flux)),
            "flux_kurtosis": float(self._calculate_kurtosis(flux)),
            
            # Transit shape features
            "transit_depth_ratio": float(abs(bls_results["depth"]) / np.std(flux)),
            "duration_ratio": float(bls_results["duration"] / bls_results["period"]),
            
            # Secondary eclipse check (phase 0.5)
            "secondary_depth": float(self._check_secondary_eclipse(phase_sorted, flux_sorted)),
            
            # Odd-even transit depth difference
            "odd_even_diff": float(self._odd_even_difference(time, flux, period, t0))
        }
        
        return features
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data."""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data."""
        mean = np.mean(data)
        std = np.std(data)
        return np.mean(((data - mean) / std) ** 4) - 3
    
    def _check_secondary_eclipse(self, phase: np.ndarray, flux: np.ndarray) -> float:
        """Check for secondary eclipse at phase 0.5."""
        # Look for dip at phase ~0.5 (secondary eclipse)
        secondary_mask = (phase > 0.45) & (phase < 0.55)
        if np.sum(secondary_mask) > 10:
            secondary_flux = np.median(flux[secondary_mask])
            baseline_flux = np.median(flux)
            return baseline_flux - secondary_flux
        return 0.0
    
    def _odd_even_difference(self, time: np.ndarray, flux: np.ndarray, 
                            period: float, t0: float) -> float:
        """Calculate difference between odd and even transits."""
        # Fold at period
        phase = ((time - t0) % period) / period
        
        # Identify transits (phase near 0)
        in_transit = (phase < 0.1) | (phase > 0.9)
        
        if np.sum(in_transit) < 20:
            return 0.0
        
        # Separate odd and even transits
        transit_number = np.floor((time - t0) / period)
        odd_transits = in_transit & (transit_number % 2 == 1)
        even_transits = in_transit & (transit_number % 2 == 0)
        
        if np.sum(odd_transits) > 5 and np.sum(even_transits) > 5:
            odd_depth = np.median(flux[odd_transits])
            even_depth = np.median(flux[even_transits])
            return abs(odd_depth - even_depth)
        
        return 0.0


# Global service instance
_tess_service: Optional[TESSDataService] = None

def get_tess_service() -> TESSDataService:
    """
    Get or create global TESS data service instance.
    
    Returns:
        TESSDataService instance
    """
    global _tess_service
    if _tess_service is None:
        _tess_service = TESSDataService()
    return _tess_service
