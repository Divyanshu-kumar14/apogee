"""
Telemetry Simulation Service
Generates realistic spacecraft telemetry with fault injection capabilities.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import asyncio
import logging

logger = logging.getLogger(__name__)

# Telemetry metric specifications
TELEMETRY_METRICS = {
    "battery_voltage": {
        "baseline": 28.0,  # Volts
        "normal_range": (26.0, 30.0),
        "noise_std": 0.2,
        "unit": "V",
        "drift_rate": 0.01  # Mean reversion rate
    },
    "internal_temp_c": {
        "baseline": 22.0,  # Celsius
        "normal_range": (18.0, 26.0),
        "noise_std": 0.5,
        "unit": "°C",
        "drift_rate": 0.05
    },
    "attitude_deviation_deg": {
        "baseline": 0.5,  # Degrees
        "normal_range": (0.0, 2.0),
        "noise_std": 0.1,
        "unit": "°",
        "drift_rate": 0.08
    },
    "signal_strength_db": {
        "baseline": -85.0,  # dBm
        "normal_range": (-95.0, -75.0),
        "noise_std": 2.0,
        "unit": "dBm",
        "drift_rate": 0.03
    }
}

class TelemetrySimulator:
    """
    Simulates spacecraft telemetry with realistic random walk behavior
    and controllable fault injection for demo purposes.
    """
    
    def __init__(self, spacecraft_id: str):
        """
        Initialize telemetry simulator for a spacecraft.
        
        Args:
            spacecraft_id: Unique identifier for the spacecraft
        """
        self.spacecraft_id = spacecraft_id
        self.current_values = {
            metric: spec["baseline"] 
            for metric, spec in TELEMETRY_METRICS.items()
        }
        self.fault_active = None
        self.running = False
        logger.info(f"Telemetry simulator initialized for spacecraft {spacecraft_id}")
    
    def generate_reading(self, metric_name: str) -> float:
        """
        Generate single telemetry reading with random walk behavior.
        
        Uses mean-reverting random walk to keep values realistic:
        - Random noise around current value
        - Drift back toward baseline (mean reversion)
        - Clamped to reasonable bounds
        
        Args:
            metric_name: Name of the metric to generate
            
        Returns:
            Generated metric value
        """
        if metric_name not in TELEMETRY_METRICS:
            logger.error(f"Unknown metric: {metric_name}")
            return 0.0
        
        spec = TELEMETRY_METRICS[metric_name]
        
        # Apply fault pattern if active
        if self.fault_active and self.fault_active["metric"] == metric_name:
            return self._apply_fault_pattern(metric_name)
        
        # Normal random walk with mean reversion
        current = self.current_values[metric_name]
        noise = np.random.normal(0, spec["noise_std"])
        
        # Mean reversion: drift back toward baseline
        drift = spec["drift_rate"] * (spec["baseline"] - current)
        new_value = current + drift + noise
        
        # Clamp to reasonable bounds (wider than normal range)
        min_bound = spec["normal_range"][0] - 3 * spec["noise_std"]
        max_bound = spec["normal_range"][1] + 3 * spec["noise_std"]
        new_value = np.clip(new_value, min_bound, max_bound)
        
        self.current_values[metric_name] = new_value
        return float(new_value)
    
    def inject_fault(self, fault_type: str, metric: str, duration_seconds: int):
        """
        Inject synthetic fault pattern for demo purposes.
        
        Available fault types:
        - battery_drift: Gradual voltage drop
        - temp_spike: Sudden temperature increase
        - attitude_oscillation: Sinusoidal oscillation
        - signal_degradation: Gradual signal loss
        
        Args:
            fault_type: Type of fault to inject
            metric: Metric to apply fault to
            duration_seconds: How long the fault should last
        """
        self.fault_active = {
            "type": fault_type,
            "metric": metric,
            "start_time": datetime.utcnow(),
            "duration": duration_seconds
        }
        logger.info(f"Fault injected: {fault_type} on {metric} for {duration_seconds}s")
    
    def _apply_fault_pattern(self, metric_name: str) -> float:
        """
        Apply fault-specific behavior to metric reading.
        
        Args:
            metric_name: Name of the metric
            
        Returns:
            Faulty metric value
        """
        fault = self.fault_active
        elapsed = (datetime.utcnow() - fault["start_time"]).total_seconds()
        
        # Clear fault if duration exceeded
        if elapsed > fault["duration"]:
            logger.info(f"Fault cleared: {fault['type']} on {fault['metric']}")
            self.fault_active = None
            return self.generate_reading(metric_name)
        
        spec = TELEMETRY_METRICS[metric_name]
        
        if fault["type"] == "battery_drift":
            # Gradual voltage drop (0.05V per second)
            drift_rate = -0.05
            return spec["baseline"] + (drift_rate * elapsed)
        
        elif fault["type"] == "temp_spike":
            # Sudden temperature increase
            spike_magnitude = 8.0  # Degrees
            return spec["baseline"] + spike_magnitude
        
        elif fault["type"] == "attitude_oscillation":
            # Sinusoidal oscillation
            frequency = 0.1  # Hz
            amplitude = 3.0  # Degrees
            return spec["baseline"] + amplitude * np.sin(2 * np.pi * frequency * elapsed)
        
        elif fault["type"] == "signal_degradation":
            # Gradual signal loss (0.5 dBm per second)
            degradation_rate = -0.5
            return spec["baseline"] + (degradation_rate * elapsed)
        
        # Unknown fault type, return normal reading
        return self.generate_reading(metric_name)
    
    def get_all_readings(self) -> Dict[str, Dict]:
        """
        Generate readings for all metrics at once.
        
        Returns:
            Dictionary mapping metric names to reading data
        """
        readings = {}
        timestamp = datetime.utcnow()
        
        for metric_name in TELEMETRY_METRICS.keys():
            value = self.generate_reading(metric_name)
            spec = TELEMETRY_METRICS[metric_name]
            
            readings[metric_name] = {
                "value": value,
                "unit": spec["unit"],
                "timestamp": timestamp.isoformat(),
                "normal_range": spec["normal_range"]
            }
        
        return readings
    
    def reset(self):
        """Reset all metrics to baseline values."""
        self.current_values = {
            metric: spec["baseline"] 
            for metric, spec in TELEMETRY_METRICS.items()
        }
        self.fault_active = None
        logger.info(f"Telemetry simulator reset for spacecraft {self.spacecraft_id}")


# Global simulator instances (one per spacecraft)
_simulators: Dict[str, TelemetrySimulator] = {}

def get_simulator(spacecraft_id: str) -> TelemetrySimulator:
    """
    Get or create telemetry simulator for a spacecraft.
    
    Args:
        spacecraft_id: Spacecraft identifier
        
    Returns:
        TelemetrySimulator instance
    """
    if spacecraft_id not in _simulators:
        _simulators[spacecraft_id] = TelemetrySimulator(spacecraft_id)
    return _simulators[spacecraft_id]
