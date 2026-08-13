# APOGEE Implementation Plan - Part 2

## Phase 2: Health Monitor (Continued)

### 2.4 Unified Alerts Feed UI Component (Continued)

```jsx
// components/UnifiedAlertsFeed.jsx (continued)
  return (
    <div className="alerts-feed">
      <h3 className="text-xl font-bold mb-4">
        Unified Alerts Feed
        <span className="text-sm text-gray-500 ml-2">
          ({alerts.length} active)
        </span>
      </h3>
      
      <div className="space-y-3">
        {alerts.map(alert => (
          <div 
            key={alert.id}
            className="alert-card border-l-4 p-4 rounded shadow-sm"
            style={{
              borderLeftColor: 
                alert.severity === 'critical' ? '#dc2626' :
                alert.severity === 'watch' ? '#f59e0b' : '#10b981'
            }}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <span className="text-2xl">
                  {getSeverityIcon(alert.severity)}
                </span>
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    {getCategoryBadge(alert.response_category)}
                    <span className="text-xs text-gray-500">
                      {alert.source === 'health' ? '📊 Telemetry' : '🛰️ Debris'}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-gray-900">
                    {alert.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**Success Criteria:**
- Alerts from both sources render together
- Sorted by severity (critical first)
- Response category badges visible
- Clear visual distinction between sources
- Real-time updates (polling every 5s)

### 2.5 HealthPanel Complete Implementation

**Tasks:**
- [ ] Create metric gauge components
- [ ] Integrate WebSocket for live updates
- [ ] Add unified alerts feed
- [ ] Implement "Inject Fault" button
- [ ] Add current status summary

**Component Structure:**

```jsx
// components/HealthPanel.jsx
import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import MetricGauge from './shared/MetricGauge';
import UnifiedAlertsFeed from './UnifiedAlertsFeed';

export default function HealthPanel({ spacecraftId = "25544" }) {
  const [metrics, setMetrics] = useState({
    battery_voltage: { value: 28.0, severity: 'nominal' },
    internal_temp_c: { value: 22.0, severity: 'nominal' },
    attitude_deviation_deg: { value: 0.5, severity: 'nominal' },
    signal_strength_db: { value: -85.0, severity: 'nominal' }
  });
  
  const [injecting, setInjecting] = useState(false);
  
  // WebSocket connection for live updates
  const { isConnected } = useWebSocket(
    `ws://localhost:8000/api/health/ws/stream?spacecraft_id=${spacecraftId}`,
    (message) => {
      if (message.type === 'telemetry_update') {
        setMetrics(prev => ({
          ...prev,
          [message.metric_name]: {
            value: message.value,
            severity: message.anomaly.severity
          }
        }));
      }
    }
  );
  
  const handleInjectFault = async (faultType, metric) => {
    setInjecting(true);
    try {
      await healthAPI.injectFault({
        fault_type: faultType,
        metric: metric,
        duration_seconds: 60
      });
    } catch (error) {
      console.error('Fault injection failed:', error);
    } finally {
      setInjecting(false);
    }
  };
  
  return (
    <div className="health-panel p-6">
      {/* Header */}
      <div className="header mb-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">Health Monitor</h2>
          <div className="flex items-center space-x-3">
            <span className={`px-3 py-1 rounded-full text-sm ${
              isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {isConnected ? '🟢 Live' : '🔴 Disconnected'}
            </span>
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
              ⚠️ Simulated Telemetry
            </span>
          </div>
        </div>
      </div>
      
      {/* Metric Gauges */}
      <div className="metrics-grid grid grid-cols-2 gap-4 mb-6">
        <MetricGauge
          name="Battery Voltage"
          value={metrics.battery_voltage.value}
          unit="V"
          severity={metrics.battery_voltage.severity}
          normalRange={[26.0, 30.0]}
        />
        <MetricGauge
          name="Internal Temperature"
          value={metrics.internal_temp_c.value}
          unit="°C"
          severity={metrics.internal_temp_c.severity}
          normalRange={[18.0, 26.0]}
        />
        <MetricGauge
          name="Attitude Deviation"
          value={metrics.attitude_deviation_deg.value}
          unit="°"
          severity={metrics.attitude_deviation_deg.severity}
          normalRange={[0.0, 2.0]}
        />
        <MetricGauge
          name="Signal Strength"
          value={metrics.signal_strength_db.value}
          unit="dBm"
          severity={metrics.signal_strength_db.severity}
          normalRange={[-95.0, -75.0]}
        />
      </div>
      
      {/* Demo Controls */}
      <div className="demo-controls bg-gray-50 p-4 rounded mb-6">
        <h3 className="text-sm font-semibold mb-3">Demo Controls</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => handleInjectFault('battery_drift', 'battery_voltage')}
            disabled={injecting}
            className="btn-secondary text-sm"
          >
            Inject Battery Fault
          </button>
          <button
            onClick={() => handleInjectFault('temp_spike', 'internal_temp_c')}
            disabled={injecting}
            className="btn-secondary text-sm"
          >
            Inject Temp Spike
          </button>
          <button
            onClick={() => handleInjectFault('attitude_oscillation', 'attitude_deviation_deg')}
            disabled={injecting}
            className="btn-secondary text-sm"
          >
            Inject Attitude Fault
          </button>
        </div>
      </div>
      
      {/* Unified Alerts Feed */}
      <UnifiedAlertsFeed spacecraftId={spacecraftId} />
    </div>
  );
}
```

**MetricGauge Component:**

```jsx
// components/shared/MetricGauge.jsx
export default function MetricGauge({ name, value, unit, severity, normalRange }) {
  const getSeverityColor = () => {
    switch(severity) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'watch': return 'border-yellow-500 bg-yellow-50';
      default: return 'border-green-500 bg-green-50';
    }
  };
  
  const getPercentage = () => {
    const [min, max] = normalRange;
    const range = max - min;
    const normalized = (value - min) / range;
    return Math.max(0, Math.min(100, normalized * 100));
  };
  
  return (
    <div className={`metric-gauge border-l-4 p-4 rounded ${getSeverityColor()}`}>
      <div className="flex justify-between items-start mb-2">
        <h4 className="text-sm font-semibold text-gray-700">{name}</h4>
        <span className={`text-xs px-2 py-1 rounded ${
          severity === 'critical' ? 'bg-red-200 text-red-800' :
          severity === 'watch' ? 'bg-yellow-200 text-yellow-800' :
          'bg-green-200 text-green-800'
        }`}>
          {severity.toUpperCase()}
        </span>
      </div>
      
      <div className="value text-3xl font-bold text-gray-900 mb-2">
        {value.toFixed(2)} <span className="text-lg text-gray-500">{unit}</span>
      </div>
      
      <div className="range-indicator">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getPercentage()}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{normalRange[0]}</span>
          <span>{normalRange[1]}</span>
        </div>
      </div>
    </div>
  );
}
```

### 2.6 API Endpoints Implementation

**Tasks:**
- [ ] Implement GET /api/health/status
- [ ] Implement WS /api/health/stream
- [ ] Implement GET /api/health/alerts
- [ ] Implement POST /api/health/inject-fault

**Endpoint Specifications:**

```python
# GET /api/health/status
@router.get("/status")
async def get_health_status(
    spacecraft_id: str = "25544",
    db: Session = Depends(get_db)
):
    """Get current health status snapshot"""
    # Get latest reading per metric
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
                "timestamp": reading.timestamp,
                "severity": anomaly["severity"],
                "anomaly_score": anomaly["anomaly_score"]
            }
    
    return {
        "spacecraft_id": spacecraft_id,
        "metrics": latest_readings,
        "overall_status": get_overall_status(latest_readings)
    }

# POST /api/health/inject-fault
@router.post("/inject-fault")
async def inject_fault(
    fault_request: FaultInjectionRequest,
    background_tasks: BackgroundTasks
):
    """Inject synthetic fault for demo purposes"""
    simulator.inject_fault(
        fault_type=fault_request.fault_type,
        metric=fault_request.metric,
        duration_seconds=fault_request.duration_seconds
    )
    
    return {
        "status": "injected",
        "fault_type": fault_request.fault_type,
        "metric": fault_request.metric,
        "duration": fault_request.duration_seconds
    }
```

### Phase 2 Milestone Check (MANDATORY GATE)

**Must Demonstrate Before Phase 3:**

1. **Telemetry Simulation:**
   - All 4 metrics generating realistic readings
   - Background task running continuously
   - Readings stored in database

2. **Anomaly Detection:**
   - IsolationForest detecting injected faults
   - Severity levels assigned correctly
   - Alerts created in shared table

3. **WebSocket Stream:**
   - Live updates pushing to frontend
   - No polling required for metric updates
   - Reconnection working after disconnect

4. **Unified Alerts Feed:**
   - Health anomalies visible
   - Debris conjunctions visible (from Phase 1)
   - Both sources in same feed
   - Response category badges displayed
   - Sorted by severity

5. **Demo Control:**
   - "Inject Fault" button works
   - Fault appears as Critical alert within 10 seconds
   - Alert includes both health and debris sources

**Critical Integration Test:**
```
1. Start with clean alerts table
2. Trigger debris refresh (Phase 1) → should create debris alerts
3. Inject battery fault → should create health alert
4. Verify unified feed shows BOTH alert types
5. Verify response_category badges are different
6. Verify severity sorting works
```

**Deliverables:**
- Working HealthPanel with live metrics
- IsolationForest anomaly detection operational
- Unified alerts feed displaying both sources
- Demo video showing fault injection → alert creation
- Documentation of anomaly detection methodology

**⚠️ DO NOT PROCEED TO PHASE 3 UNTIL:**
- All Phase 2 success criteria met
- Milestone check passed
- Unified alerts feed proven working
- Team can explain IsolationForest approach

---

## Phase 3: Discovery Module (Science Tool)

**Objective:** Implement TESS light curve analysis with BLS periodogram and ML-based transit vetting. This is intentionally separate from the operational alerts system.

**Duration:** 3-4 days

**Why Third:** Least integrated feature, can be developed independently. Only proceed if Phases 1-2 are solid.

### 3.1 TESS Data Selection & Caching

**Tasks:**
- [ ] Research TESS Input Catalog (TIC)
- [ ] Select 5-10 target TIC IDs
- [ ] Download light curves using lightkurve
- [ ] Cache locally (no live MAST calls)
- [ ] Document target selection rationale

**Target Selection Strategy:**

```python
# Recommended TIC IDs (mix of confirmed planets + negatives)
TESS_TARGETS = {
    # Confirmed exoplanet hosts
    "TIC 307210830": {  # TOI-700 (Earth-sized planets)
        "tic_id": 307210830,
        "name": "TOI-700",
        "has_planets": True,
        "expected_period": 9.98,  # days
        "notes": "Multi-planet system, good demo"
    },
    "TIC 261136679": {  # LHS 3844 (hot super-Earth)
        "tic_id": 261136679,
        "name": "LHS 3844",
        "has_planets": True,
        "expected_period": 0.46,
        "notes": "Short period, clear signal"
    },
    "TIC 410214986": {  # TOI-1685 (hot Jupiter)
        "tic_id": 410214986,
        "name": "TOI-1685",
        "has_planets": True,
        "expected_period": 0.67,
        "notes": "Deep transit, easy detection"
    },
    
    # Clean negatives (no known planets)
    "TIC 123456789": {  # Example quiet star
        "tic_id": 123456789,
        "name": "Quiet Star 1",
        "has_planets": False,
        "notes": "Control - should show no transits"
    },
    
    # Eclipsing binary (false positive test)
    "TIC 987654321": {
        "tic_id": 987654321,
        "name": "Eclipsing Binary",
        "has_planets": False,
        "notes": "Should be rejected by ML vetting"
    }
}
```

**Data Download Script:**

```python
import lightkurve as lk
import os

def download_and_cache_lightcurves(cache_dir: str = "data/tess"):
    """Download TESS light curves and cache locally"""
    os.makedirs(cache_dir, exist_ok=True)
    
    for target_name, target_info in TESS_TARGETS.items():
        tic_id = target_info["tic_id"]
        cache_file = os.path.join(cache_dir, f"TIC_{tic_id}.fits")
        
        if os.path.exists(cache_file):
            print(f"Already cached: {target_name}")
            continue
        
        try:
            # Search for light curves
            search_result = lk.search_lightcurve(
                f"TIC {tic_id}",
                mission="TESS"
            )
            
            if len(search_result) == 0:
                print(f"No data found for {target_name}")
                continue
            
            # Download first available sector
            lc = search_result[0].download()
            
            # Save to cache
            lc.to_fits(cache_file, overwrite=True)
            print(f"Cached: {target_name} → {cache_file}")
            
        except Exception as e:
            print(f"Error downloading {target_name}: {e}")

# Run at build time, not during demo
if __name__ == "__main__":
    download_and_cache_lightcurves()
```

**Success Criteria:**
- 5-10 light curves cached locally
- Mix of confirmed planets and negatives
- FITS files readable by lightkurve
- No MAST API calls during demo

### 3.2 Light Curve Preprocessing

**Tasks:**
- [ ] Load cached FITS files
- [ ] Extract PDCSAP flux
- [ ] Implement detrending
- [ ] Handle data gaps
- [ ] Normalize flux

**Preprocessing Pipeline:**

```python
import lightkurve as lk
import numpy as np

class LightCurveProcessor:
    def __init__(self, cache_dir: str = "data/tess"):
        self.cache_dir = cache_dir
    
    def load_lightcurve(self, tic_id: int) -> lk.LightCurve:
        """Load cached light curve"""
        cache_file = os.path.join(self.cache_dir, f"TIC_{tic_id}.fits")
        return lk.read(cache_file)
    
    def preprocess(self, lc: lk.LightCurve) -> lk.LightCurve:
        """
        Preprocess light curve for transit detection.
        
        Steps:
        1. Remove NaN values
        2. Flatten (detrend) using Savitzky-Golay filter
        3. Normalize to median = 1.0
        """
        # Remove NaNs
        lc = lc.remove_nans()
        
        # Flatten using built-in method
        # This removes long-term trends while preserving transits
        lc_flat = lc.flatten(window_length=401)
        
        # Normalize
        lc_flat = lc_flat.normalize()
        
        return lc_flat
    
    def get_quality_metrics(self, lc: lk.LightCurve) -> dict:
        """Calculate data quality metrics"""
        return {
            "n_points": len(lc.time),
            "time_span_days": float(lc.time[-1] - lc.time[0]),
            "median_flux": float(np.median(lc.flux)),
            "flux_std": float(np.std(lc.flux)),
            "cadence_minutes": float(np.median(np.diff(lc.time)) * 24 * 60)
        }
```

**Success Criteria:**
- Detrending removes stellar variability
- Transits preserved in flattened curve
- No artifacts introduced
- Quality metrics calculated

### 3.3 BLS Periodogram Implementation

**Tasks:**
- [ ] Integrate astropy BLS
- [ ] Configure search parameters
- [ ] Extract best period/depth/power
- [ ] Calculate transit duration
- [ ] Compute SNR

**BLS Pipeline:**

```python
from astropy.timeseries import BoxLeastSquares
import numpy as np

class BLSDetector:
    def __init__(
        self,
        min_period: float = 0.5,  # days
        max_period: float = 20.0,  # days
        duration_range: tuple = (0.01, 0.2)  # fraction of period
    ):
        self.min_period = min_period
        self.max_period = max_period
        self.duration_range = duration_range
    
    def run_bls(self, lc: lk.LightCurve) -> dict:
        """
        Run Box Least Squares periodogram.
        
        Returns dict with:
        - period: best period (days)
        - depth: transit depth (relative flux)
        - duration: transit duration (hours)
        - power: BLS power (detection significance)
        - snr: signal-to-noise ratio
        """
        # Create BLS model
        model = BoxLeastSquares(lc.time.value, lc.flux.value)
        
        # Run periodogram
        periodogram = model.autopower(
            duration=self.duration_range,
            minimum_period=self.min_period,
            maximum_period=self.max_period
        )
        
        # Extract best period
        best_idx = np.argmax(periodogram.power)
        period = periodogram.period[best_idx]
        power = periodogram.power[best_idx]
        duration = periodogram.duration[best_idx]
        
        # Get transit parameters at best period
        stats = model.compute_stats(
            period=period,
            duration=duration,
            transit_time=periodogram.transit_time[best_idx]
        )
        
        depth = stats['depth'][0]
        snr = stats['depth'][0] / stats['depth_err'][0]
        
        return {
            "period": float(period),
            "depth": float(depth),
            "duration_hours": float(duration * 24),
            "power": float(power),
            "snr": float(snr),
            "transit_time": float(periodogram.transit_time[best_idx])
        }
    
    def fold_lightcurve(
        self,
        lc: lk.LightCurve,
        period: float,
        transit_time: float
    ) -> lk.LightCurve:
        """Fold light curve at detected period"""
        return lc.fold(period=period, epoch_time=transit_time)
```

**Success Criteria:**
- BLS detects known planets correctly
- Period accuracy within 1%
- Depth measurements reasonable
- SNR > 5 for confirmed transits

### 3.4 ML Vetting Classifier (MANDATORY)

**Tasks:**
- [ ] Design feature extraction
- [ ] Create training dataset
- [ ] Train scikit-learn classifier
- [ ] Implement vetting pipeline
- [ ] Validate on test cases

**Why ML Vetting is Required:**
- BLS alone is classical signal processing (no learned component)
- Real exoplanet pipelines (NASA Astronet) use ML vetting
- Distinguishes planets from false positives (eclipsing binaries, noise)
- Makes Discovery Module genuinely ML-based

**Feature Engineering:**

```python
def extract_transit_features(lc: lk.LightCurve, bls_result: dict) -> np.ndarray:
    """
    Extract features for ML vetting classifier.
    
    Features:
    1. Transit depth (relative flux)
    2. Transit duration (hours)
    3. Period (days)
    4. SNR (signal-to-noise ratio)
    5. Odd-even depth mismatch (asymmetry test)
    6. Secondary eclipse depth (eclipsing binary test)
    7. Shape parameter (V-shaped vs U-shaped)
    """
    period = bls_result["period"]
    depth = bls_result["depth"]
    duration = bls_result["duration_hours"]
    snr = bls_result["snr"]
    
    # Fold at detected period
    lc_folded = lc.fold(period=period, epoch_time=bls_result["transit_time"])
    
    # Odd-even test: compare odd vs even transits
    odd_transits = lc_folded[::2]
    even_transits = lc_folded[1::2]
    odd_depth = np.abs(np.min(odd_transits.flux) - 1.0)
    even_depth = np.abs(np.min(even_transits.flux) - 1.0)
    odd_even_mismatch = np.abs(odd_depth - even_depth) / depth
    
    # Secondary eclipse test: check for signal at phase 0.5
    phase_05_window = lc_folded[(lc_folded.phase > 0.45) & (lc_folded.phase < 0.55)]
    secondary_depth = np.abs(np.min(phase_05_window.flux) - 1.0) if len(phase_05_window) > 0 else 0.0
    
    # Shape parameter: transit bottom flatness
    in_transit = lc_folded[(lc_folded.phase > -0.02) & (lc_folded.phase < 0.02)]
    shape_param = np.std(in_transit.flux) / depth if len(in_transit) > 10 else 1.0
    
    features = np.array([
        depth,
        duration,
        period,
        snr,
        odd_even_mismatch,
        secondary_depth / depth if depth > 0 else 0.0,
        shape_param
    ])
    
    return features

# Feature names for interpretability
FEATURE_NAMES = [
    "depth",
    "duration_hours",
    "period_days",
    "snr",
    "odd_even_mismatch",
    "secondary_eclipse_ratio",
    "shape_parameter"
]
```

**Classifier Training:**

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

class TransitVettingClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.is_trained = False
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """
        Train classifier on labeled examples.
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (1 = planet, 0 = false positive)
        """
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"Training accuracy: {train_score:.3f}")
        print(f"Test accuracy: {test_score:.3f}")
        
        self.is_trained = True
    
    def predict(self, features: np.ndarray) -> dict:
        """
        Vet transit candidate.
        
        Returns:
            {
                "is_likely_planet": bool,
                "confidence": float (0-1),
                "feature_importances": dict
            }
        """
        if not self.is_trained:
            raise ValueError("Classifier not trained")
        
        # Reshape for single prediction
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Predict
        prediction = self.model.predict(features)[0]
        confidence = self.model.predict_proba(features)[0][prediction]
        
        # Feature importances
        importances = dict(zip(
            FEATURE_NAMES,
            self.model.feature_importances_
        ))
        
        return {
            "is_likely_planet": bool(prediction),
            "confidence": float(confidence),
            "feature_importances": importances
        }
    
    def save(self, filepath: str):
        """Save trained model"""
        joblib.dump(self.model, filepath)
    
    def load(self, filepath: str):
        """Load trained model"""
        self.model = joblib.load(filepath)
        self.is_trained = True

# Training data creation (simplified - real version would use NASA Exoplanet Archive)
def create_training_data():
    """
    Create synthetic training dataset.
    In production, use real labeled data from NASA Exoplanet Archive.
    """
    # Confirmed planets (label = 1)
    planets = np.array([
        [0.01, 2.5, 3.5, 15.0, 0.05, 0.02, 0.3],  # Hot Jupiter
        [0.005, 3.0, 10.0, 12.0, 0.08, 0.01, 0.4],  # Warm Neptune
        [0.002, 4.0, 15.0, 8.0, 0.10, 0.00, 0.5],  # Super-Earth
    ])
    
    # False positives (label = 0)
    false_positives = np.array([
        [0.02, 5.0, 2.0, 20.0, 0.30, 0.15, 0.8],  # Eclipsing binary (high odd-even, secondary)
        [0.001, 1.0, 5.0, 3.0, 0.50, 0.00, 1.2],  # Noise (low SNR, high mismatch)
        [0.015, 6.0, 1.5, 18.0, 0.05, 0.20, 0.2],  # Grazing binary (secondary eclipse)
    ])
    
    X = np.vstack([planets, false_positives])
    y = np.array([1, 1, 1, 0, 0, 0])
    
    return X, y

# Train and save model (run at build time)
if __name__ == "__main__":
    X, y = create_training_data()
    classifier = TransitVettingClassifier()
    classifier.train(X, y)
    classifier.save("models/transit_vetting_classifier.pkl")
```

**Success Criteria:**
- Classifier trained on labeled data
- Test accuracy > 80%
- Correctly identifies known planets
- Rejects eclipsing binaries
- Model saved and loadable

### 3.5 Complete Transit Detection Pipeline

**Tasks:**
- [ ] Integrate all components
- [ ] Process all cached targets
- [ ] Store results in database
- [ ] Generate folded light curves
- [ ] Create API endpoints

**Full Pipeline:**

```python
class TransitDetectionPipeline:
    def __init__(self):
        self.processor = LightCurveProcessor()
        self.bls = BLSDetector()
        self.classifier = TransitVettingClassifier()
        self.classifier.load("models/transit_vetting_classifier.pkl")
    
    def process_target(self, tic_id: int, target_name: str) -> dict:
        """
        Run complete transit detection pipeline on one target.
        
        Returns:
            {
                "tic_id": int,
                "target_name": str,
                "bls_result": dict,
                "vetting_result": dict,
                "quality_metrics": dict
            }
        """
        # Load and preprocess
        lc = self.processor.load_lightcurve(tic_id)
        lc_processed = self.processor.preprocess(lc)
        quality = self.processor.get_quality_metrics(lc_processed)
        
        # Run BLS
        bls_result = self.bls.run_bls(lc_processed)
        
        # Extract features
        features = extract_transit_features(lc_processed, bls_result)
        
        # ML vetting
        vetting_result = self.classifier.predict(features)
        
        # Generate folded light curve for visualization
        lc_folded = self.bls.fold_lightcurve(
            lc_processed,
            bls_result["period"],
            bls_result["transit_time"]
        )
        
        return {
            "tic_id": tic_id,
            "target_name": target_name,
            "bls_result": bls_result,
            "vetting_result": vetting_result,
            "quality_metrics": quality,
            "folded_lightcurve": {
                "phase": lc_folded.phase.value.tolist(),
                "flux": lc_folded.flux.value.tolist()
            }
        }
    
    def process_all_targets(self, db: Session):
        """Process all cached targets and store in database"""
        for target_name, target_info in TESS_TARGETS.items():
            tic_id = target_info["tic_id"]
            
            try:
                result = self.process_target(tic_id, target_name)
                
                # Store in database
                candidate = TransitCandidate(
                    tic_id=tic_id,
                    target_name=target_name,
                    period_days=result["bls_result"]["period"],
                    transit_depth=result["bls_result"]["depth"],
                    bls_power=result["bls_result"]["power"],
                    ml_vetting_score=result["vetting_result"]["confidence"],
                    is_likely_planet=result["vetting_result"]["is_likely_planet"],
                    flagged_at=datetime.utcnow()
                )
                
                db.add(candidate)
                db.commit()
                
                print(f"Processed: {target_name} - Planet: {candidate.is_likely_planet}")
                
            except Exception as e:
                print(f"Error processing {target_name}: {e}")

# Run at build time
if __name__ == "__main__":
    from database import SessionLocal
    db = SessionLocal()
    pipeline = TransitDetectionPipeline()
    pipeline.process_all_targets(db)
    db.close()
```

**Success Criteria:**
- All targets processed successfully
- Results stored in database
- Folded light curves generated
- ML vetting scores calculated

### 3.6 API Endpoints Implementation

**Tasks:**
- [ ] Implement GET /api/discovery/candidates
- [ ] Implement GET /api/discovery/candidates/{tic_id}/lightcurve
- [ ] Add filtering by vetting score
- [ ] Document endpoints

**Endpoint Specifications:**

```python
# GET /api/discovery/candidates
@router.get("/candidates")
async def get_transit_candidates(
    min_confidence: float = 0.0,
    only_likely_planets: bool = False,
    db: Session = Depends(get_db)
):
    """Get list of transit candidates"""
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

# GET /api/discovery/candidates/{tic_id}/lightcurve
@router.get("/candidates/{tic_id}/lightcurve")
async def get_folded_lightcurve(
    tic_id: int,
    db: Session = Depends(get_db)
):
    """Get folded light curve data for visualization"""
    candidate = db.query(TransitCandidate).filter(
        TransitCandidate.tic_id == tic_id
    ).first()
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Load cached folded light curve
    cache_file = f"data/tess/folded/TIC_{tic_id}_folded.json"
    with open(cache_file, 'r') as f:
        lightcurve_data = json.load(f)
    
    return {
        "tic_id": tic_id,
        "target_name": candidate.target_name,
        "period_days": candidate.period_days,
        "transit_depth": candidate.transit_depth,
        "is_likely_planet": candidate.is_likely_planet,
        "confidence": candidate.ml_vetting_score,
        "lightcurve": lightcurve_data
    }
```

### 3.7 DiscoveryPanel UI Implementation

**Tasks:**
- [ ] Create DiscoveryPanel component
- [ ] Implement candidate list
- [ ] Add folded light curve chart
- [ ] Display ML vetting results
- [ ] Add clear separation from operational panels

**Component Structure:**

```jsx
// components/DiscoveryPanel.jsx
import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function DiscoveryPanel() {
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [lightcurve, setLightcurve] = useState(null);
  
  useEffect(() => {
    loadCandidates();
  }, []);
  
  const loadCandidates = async () => {
    const data = await discoveryAPI.getCandidates();
    setCandidates(data.candidates);
  };
  
  const handleSelectCandidate = async (tic_id) => {
    const data = await discoveryAPI.getLightcurve(tic_id);
    setSelectedCandidate(data);
    setLightcurve(data.lightcurve);
  };
  
  return (
    <div className="discovery-panel p-6">
      {/* Header with clear separation */}
      <div className="header mb-6 border-l-4 border-purple-500 pl-4">
        <h2 className="text-2xl font-bold text-purple-900">
          🔭 Discovery Module
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Science Tool — Independent of spacecraft telemetry
        </p>
        <p className="text-xs text-gray-500 mt-1">
          TESS exoplanet transit detection using BLS + ML vetting
        </p>
      </div>
      
      <div className="grid grid-cols-3 gap-6">
        {/* Candidate List */}
        <div className="col-span-1">
          <h3 className="text-lg font-semibold mb-3">Transit Candidates</h3>
          <div className="space-y-2">
            {candidates.map(candidate => (
              <div
                key={candidate.tic_id}
                onClick={() => handleSelectCandidate(candidate.tic_id)}
                className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                  selectedCandidate?.tic_id === candidate.tic_id ? 'border-purple-500 bg-purple-50' : ''
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-sm">{candidate.target_name}</p>
                    <p className="text-xs text-gray-500">TIC {candidate.tic_id}</p>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    candidate.is_likely_planet 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {candidate.is_likely_planet ? '✓ Planet' : '✗ Rejected'}
                  </span>
                </div>
                <div className="mt-2 text-xs text-gray-600">
                  <p>Period: {candidate.period_days.toFixed(2)} days</p>
                  <p>Confidence: {(candidate.ml_vetting_score * 100).toFixed(1)}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Light Curve Visualization */}
        <div className="col-span-2">
          {selectedCandidate ? (
            <div>
              <h3 className="text-lg font-semibold mb-3">
                Folded Light Curve: {selectedCandidate.target_name}
              </h3>
              
              <div className="bg-white p-4 rounded border mb-4">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={lightcurve}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="phase" 
                      label={{ value: 'Orbital Phase', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis 
                      label={{ value: 'Normalized Flux', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Line 
                      type="monotone" 
                      dataKey="flux" 
                      stroke="#8b5cf6" 
                      dot={false}
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded">
                  <h4 className="font-semibold text-sm mb-2">Detection Parameters</h4>
                  <dl className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Period:</dt>
                      <dd className="font-medium">{selectedCandidate.period_days.toFixed(3)} days</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Transit Depth:</dt>
                      <dd className="font-medium">{(selectedCandidate.transit_depth * 100).toFixed(2)}%</dd>
                    </div>
                  </dl>
                </div>
                
                <div className="bg-gray-50 p-4 rounded">
                  <h4 className="font-semibold text-sm mb-2">ML Vetting Result</h4>
                  <dl className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Classification:</dt>
                      <dd className={`font-medium ${
                        selectedCandidate.is_likely_planet ? 'text-green-600' : 'text-gray-600'
                      }`}>
                        {selectedCandidate.is_likely_planet ? 'Likely Planet' : 'False Positive'}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-gray-600">Confidence:</dt>
                      <dd className="font-medium">
                        {(selectedCandidate.confidence * 100).toFixed(1)}%
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <p>Select a candidate to view light curve</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

### Phase 3 Milestone Check (MANDATORY GATE)

**Must Demonstrate Before Phase 4:**

1. **Data Pipeline:**
   - TESS light curves cached locally
   - No live MAST API calls during demo
   - All targets processed successfully

2. **BLS Detection:**
   - Known planets detected with correct periods
   - Period accuracy within 1%
   - Transit depths reasonable

3. **ML Vetting:**
   - Classifier trained and saved
   - Correctly identifies confirmed planets
   - Rejects eclipsing binaries
   - Confidence scores sensible

4. **UI Verification:**
   - Candidate list displays all targets
   - Folded light curves render correctly
   - ML vetting results visible
   - Clear visual separation from operational panels

5. **Integration Check:**
   - Discovery Module does NOT write to alerts table
   - Clearly labeled as separate science tool
   - No false claims of integration

**Deliverables:**
- Working DiscoveryPanel with real TESS data
- Trained ML vetting classifier
- Documentation of BLS+ML pipeline
- Test results showing vetting accuracy

**⚠️ DO NOT PROCEED TO PHASE 4 UNTIL:**
- All Phase 3 success criteria met
- ML vetting demonstrably working
- Team can explain BLS and classifier approach
- Clear separation from operational features maintained

---

## Phase 4: Polish & Additional Features

**Objective:** Add IBM watsonx/Granite integration, apply UI polish libraries, and implement stretch goals if time permits.

**Duration:** 2-3 days (time-permitting)

**Priority Order:** Work through these in sequence, stop wherever tim