# APOGEE — Detailed Phase-Wise Implementation Plan

**Document Version:** 1.0  
**Last Updated:** August 13, 2026  
**Project:** APOGEE - Mission Awareness Dashboard for Space Operations

---

## Executive Summary

This implementation plan breaks down the APOGEE project into 5 distinct phases, following the build order specified in the PRD. Each phase is designed to deliver a demoable increment, with clear success criteria and milestone checks before proceeding to the next phase.

**Critical Path:** Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4

**Estimated Timeline:** 
- Phase 0: 2-3 days
- Phase 1: 3-4 days  
- Phase 2: 4-5 days
- Phase 3: 3-4 days
- Phase 4: 2-3 days (time-permitting)

**Total:** 14-19 days for full implementation

---

## Pre-Implementation Checklist

### ⚠️ CRITICAL: Eligibility Verification (Must Complete First)

**Status:** 🔴 UNVERIFIED

**Action Required:**
1. Confirm build environment is IBM Bob (Roo Code-based IDE agent)
2. Verify access through university signup portal
3. Document IBM Bob version and configuration
4. Test basic IBM Bob functionality before writing any code

**Why This Matters:** Per contest rules, IBM Bob must be the core build tool. Failure to use IBM Bob can result in disqualification regardless of code quality.

**Deliverable:** Written confirmation that IBM Bob is set up and operational.

---

## Phase 0: Project Scaffolding & Foundation

**Objective:** Establish the complete technical foundation with all infrastructure, database schema, and basic routing in place. No feature logic yet—just the skeleton that all subsequent phases will build upon.

**Duration:** 2-3 days

### 0.1 Environment Setup

**Tasks:**
- [ ] Verify IBM Bob environment is active and accessible
- [ ] Create project root directory structure
- [ ] Initialize Git repository with .gitignore
- [ ] Document development environment requirements

**Deliverables:**
```
apogee/
├── backend/          # FastAPI application
├── frontend/         # React + Vite application
├── docs/            # Documentation
├── data/            # Cached data (TLEs, TESS light curves)
└── README.md
```

### 0.2 Backend Scaffolding (FastAPI)

**Tasks:**
- [ ] Initialize FastAPI project with proper structure
- [ ] Set up virtual environment and requirements.txt
- [ ] Configure CORS for local development
- [ ] Implement basic health check endpoint (`GET /health`)

**Required Dependencies:**
```python
fastapi==0.104.0
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
sqlite3  # Built-in
sgp4==2.23
scikit-learn==1.3.2
lightkurve==2.4.2
websockets==12.0
python-multipart==0.0.6
requests==2.31.0
```

**Directory Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # Database models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py        # /api/health/* routes
│   │   ├── debris.py        # /api/debris/* routes
│   │   └── discovery.py     # /api/discovery/* routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── telemetry.py     # Telemetry simulator
│   │   ├── anomaly.py       # IsolationForest detector
│   │   ├── orbital.py       # SGP4 propagation
│   │   └── transit.py       # BLS + ML vetting
│   └── schemas/
│       ├── __init__.py
│       └── api_models.py    # Pydantic models
├── requirements.txt
└── run.py
```

### 0.3 Database Schema Implementation

**Tasks:**
- [ ] Create SQLAlchemy models for all tables
- [ ] Implement database initialization script
- [ ] Add sample data seeding for testing
- [ ] Create database migration strategy (Alembic optional)

**Schema Definitions:**

```python
# Table: telemetry_reading
class TelemetryReading(Base):
    id: Integer (PK, autoincrement)
    spacecraft_id: String(50)
    timestamp: DateTime
    metric_name: String(100)  # battery_voltage, internal_temp_c, etc.
    value: Float
    
    Index: (spacecraft_id, metric_name, timestamp)

# Table: tracked_object
class TrackedObject(Base):
    norad_id: Integer (PK)
    name: String(100)
    tle_line1: String(69)
    tle_line2: String(69)
    last_updated: DateTime
    apogee_km: Float  # For pre-filtering
    perigee_km: Float  # For pre-filtering

# Table: conjunction_risk
class ConjunctionRisk(Base):
    id: Integer (PK, autoincrement)
    spacecraft_id: String(50)
    object_norad_id: Integer (FK → tracked_object.norad_id)
    closest_approach_km: Float
    relative_velocity_kmps: Float
    risk_score: Float  # 0-100
    computed_at: DateTime
    
    Index: (spacecraft_id, risk_score DESC)

# Table: transit_candidate
class TransitCandidate(Base):
    id: Integer (PK, autoincrement)
    tic_id: Integer
    target_name: String(100)
    period_days: Float
    transit_depth: Float
    bls_power: Float
    ml_vetting_score: Float  # NEW: classifier confidence
    is_likely_planet: Boolean  # NEW: ML classification result
    flagged_at: DateTime

# Table: alerts (SHARED - CRITICAL FOR INTEGRATION)
class Alert(Base):
    id: Integer (PK, autoincrement)
    spacecraft_id: String(50)
    source: String(20)  # "health" | "debris"
    response_category: String(20)  # "engineering" | "flight_dynamics"
    severity: String(20)  # "nominal" | "watch" | "critical"
    message: Text
    timestamp: DateTime
    explained: Boolean  # For watsonx/Granite integration
    explanation: Text  # Cached LLM explanation
    
    Index: (spacecraft_id, severity, timestamp DESC)
```

**Success Criteria:**
- Database file created successfully
- All tables exist with correct schema
- Can insert and query test data
- Foreign key constraints working

### 0.4 Frontend Scaffolding (React + Vite)

**Tasks:**
- [ ] Initialize Vite project with React template
- [ ] Install and configure Tailwind CSS
- [ ] Set up React Router for navigation
- [ ] Create basic component structure
- [ ] Configure API client (axios/fetch)

**Required Dependencies:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2",
    "recharts": "^2.10.3",
    "tailwindcss": "^3.3.5"
  }
}
```

**Component Structure:**
```
frontend/src/
├── App.jsx                  # Main app shell
├── main.jsx                 # Entry point
├── components/
│   ├── Header.jsx           # Spacecraft selector
│   ├── HealthPanel.jsx      # Phase 2
│   ├── DebrisPanel.jsx      # Phase 1
│   ├── DiscoveryPanel.jsx   # Phase 3
│   └── shared/
│       ├── AlertCard.jsx
│       ├── MetricGauge.jsx
│       └── RiskTable.jsx
├── services/
│   └── api.js               # API client
├── hooks/
│   └── useWebSocket.js      # WebSocket hook
└── styles/
    └── index.css            # Tailwind imports
```

### 0.5 Basic Routing & Placeholder UI

**Tasks:**
- [ ] Implement App Shell with header
- [ ] Create placeholder panels (empty state)
- [ ] Add "Simulated Telemetry" badge to header
- [ ] Implement basic navigation/tabs
- [ ] Test frontend-backend connectivity

**UI Layout:**
```
┌─────────────────────────────────────────────────┐
│  APOGEE  [ISS - NORAD 25544]  🔴 Simulated Data │
├─────────────────────────────────────────────────┤
│  [Health Monitor] [Debris Risk] [Discovery]     │
├─────────────────────────────────────────────────┤
│                                                  │
│  [Placeholder Panel Content]                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Phase 0 Success Criteria (MANDATORY GATE)

**Must Pass All Before Phase 1:**
- ✅ FastAPI server starts without errors
- ✅ React dev server runs and displays placeholder UI
- ✅ Database schema created with all 5 tables
- ✅ Can make successful API call from frontend to backend
- ✅ Git repository initialized with proper .gitignore
- ✅ "Simulated Telemetry" badge visible in UI
- ✅ All three panel placeholders render correctly

**Deliverables:**
- Working FastAPI server on `http://localhost:8000`
- Working React app on `http://localhost:5173`
- SQLite database file with schema
- Documentation of API endpoints (even if not implemented)
- README with setup instructions

---

## Phase 1: Debris Risk Module (Highest Priority)

**Objective:** Implement the complete debris risk pipeline from TLE fetching through risk scoring, with a working UI. This is the cleanest data source and provides the clearest demonstration value.

**Duration:** 3-4 days

**Why First:** 
- Real external data (CelesTrak) with no simulation needed
- Clear, explainable risk metric
- Foundation for shared alerts table integration in Phase 2

### 1.1 CelesTrak Integration

**Tasks:**
- [ ] Research CelesTrak GP (General Perturbations) API
- [ ] Implement TLE fetching for ISS (NORAD 25544)
- [ ] Implement catalog subset fetching (active satellites)
- [ ] Add caching mechanism (save to `data/tles/`)
- [ ] Implement manual refresh trigger (no auto-fetch)

**API Endpoint:**
```
CelesTrak GP API: https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json
```

**Data Model:**
```python
# Service: orbital.py
class CelesTrakService:
    def fetch_spacecraft_tle(self, norad_id: int) -> TrackedObject:
        """Fetch single spacecraft TLE"""
        
    def fetch_catalog_subset(self, group: str = "active") -> List[TrackedObject]:
        """Fetch catalog of tracked objects"""
        
    def cache_tles(self, objects: List[TrackedObject], cache_dir: str):
        """Save TLEs to local cache"""
```

**Success Criteria:**
- Can fetch ISS TLE successfully
- Can fetch catalog subset (limit to 1000 objects for testing)
- TLEs cached locally in JSON format
- Last update timestamp tracked

### 1.2 Altitude-Based Pre-Filter (CRITICAL FOR PERFORMANCE)

**Tasks:**
- [ ] Extract apogee/perigee from TLE data
- [ ] Implement altitude band overlap check
- [ ] Document filter logic with comments
- [ ] Test filter reduces object count by >80%

**Filter Logic:**
```python
def filter_by_altitude_band(
    spacecraft: TrackedObject,
    catalog: List[TrackedObject],
    buffer_km: float = 100.0
) -> List[TrackedObject]:
    """
    Pre-filter catalog to objects whose orbital altitude overlaps
    with the spacecraft's altitude band (with buffer).
    
    This reduces SGP4 propagation workload from ~16,000 objects
    to typically <500 objects for LEO spacecraft.
    """
    sc_min_alt = spacecraft.perigee_km - buffer_km
    sc_max_alt = spacecraft.apogee_km + buffer_km
    
    filtered = []
    for obj in catalog:
        # Check if altitude bands overlap
        if (obj.perigee_km <= sc_max_alt and 
            obj.apogee_km >= sc_min_alt):
            filtered.append(obj)
    
    return filtered
```

**Success Criteria:**
- Filter reduces catalog from ~1000 to <200 objects for ISS
- No false negatives (objects in same orbital shell not filtered out)
- Filter execution time <100ms

### 1.3 SGP4 Propagation Pipeline

**Tasks:**
- [ ] Install and test sgp4 Python library
- [ ] Implement propagation for single object
- [ ] Implement batch propagation for filtered catalog
- [ ] Calculate minimum separation distance
- [ ] Implement as background task (non-blocking)

**Propagation Logic:**
```python
from sgp4.api import Satrec, jday
import numpy as np

class OrbitalPropagator:
    def __init__(self, lookahead_hours: int = 48):
        self.lookahead_hours = lookahead_hours
        
    def propagate_object(
        self, 
        tle_line1: str, 
        tle_line2: str,
        time_points: List[datetime]
    ) -> List[Tuple[float, float, float]]:
        """
        Propagate single object using SGP4.
        Returns list of (x, y, z) positions in km (TEME frame).
        """
        satellite = Satrec.twoline2rv(tle_line1, tle_line2)
        positions = []
        
        for t in time_points:
            jd, fr = jday(t.year, t.month, t.day, 
                         t.hour, t.minute, t.second)
            e, r, v = satellite.sgp4(jd, fr)
            if e == 0:  # No error
                positions.append(r)
        
        return positions
    
    def compute_min_separation(
        self,
        pos1: List[Tuple[float, float, float]],
        pos2: List[Tuple[float, float, float]]
    ) -> Tuple[float, int]:
        """
        Compute minimum separation distance and time index.
        Returns (min_distance_km, time_index)
        """
        distances = []
        for p1, p2 in zip(pos1, pos2):
            dx = p1[0] - p2[0]
            dy = p1[1] - p2[1]
            dz = p1[2] - p2[2]
            dist = np.sqrt(dx**2 + dy**2 + dz**2)
            distances.append(dist)
        
        min_idx = np.argmin(distances)
        return distances[min_idx], min_idx
```

**Time Points Generation:**
```python
def generate_time_points(
    start: datetime,
    hours: int,
    step_minutes: int = 5
) -> List[datetime]:
    """Generate time points for propagation"""
    points = []
    current = start
    end = start + timedelta(hours=hours)
    
    while current <= end:
        points.append(current)
        current += timedelta(minutes=step_minutes)
    
    return points
```

**Success Criteria:**
- Can propagate ISS over 48-hour window
- Can propagate filtered catalog (batch operation)
- Minimum separation calculated correctly
- Background task completes without blocking API

### 1.4 Risk Scoring Formula

**Tasks:**
- [ ] Design risk scoring formula
- [ ] Document formula with inline comments
- [ ] Implement relative velocity calculation
- [ ] Test with known close approaches
- [ ] Validate score range (0-100)

**Risk Score Formula:**
```python
def calculate_risk_score(
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
    
    Args:
        min_distance_km: Minimum separation distance
        relative_velocity_kmps: Relative velocity at closest approach
        distance_threshold_km: Distance below which risk is maximum
        velocity_weight: Weight for velocity component (0-1)
    
    Returns:
        Risk score from 0 (no risk) to 100 (critical risk)
    """
    # Distance component (exponential decay)
    # Risk = 100 at distance = 0, decays to ~0 at 50km
    distance_score = 100 * np.exp(-min_distance_km / distance_threshold_km)
    
    # Velocity component (linear scaling)
    # Higher relative velocity = higher risk
    velocity_score = min(100, (relative_velocity_kmps / 15.0) * 100)
    
    # Weighted combination
    distance_weight = 1.0 - velocity_weight
    risk_score = (distance_weight * distance_score + 
                  velocity_weight * velocity_score)
    
    return np.clip(risk_score, 0, 100)
```

**Risk Thresholds:**
- **Critical (🔴):** risk_score >= 70
- **Watch (🟡):** 40 <= risk_score < 70
- **Nominal (🟢):** risk_score < 40

**Success Criteria:**
- Formula produces sensible scores for test cases
- Close approaches (<5km) score >80
- Distant objects (>50km) score <10
- Formula is explainable to judges

### 1.5 Alerts Table Integration

**Tasks:**
- [ ] Implement alert creation for high-risk conjunctions
- [ ] Add response_category: "flight_dynamics" tag
- [ ] Format alert message with object details
- [ ] Test alert insertion and retrieval

**Alert Creation Logic:**
```python
def create_debris_alert(
    spacecraft_id: str,
    conjunction: ConjunctionRisk,
    tracked_object: TrackedObject,
    db: Session
) -> Alert:
    """Create alert for high-risk conjunction"""
    
    severity = "critical" if conjunction.risk_score >= 70 else "watch"
    
    message = (
        f"Conjunction detected with {tracked_object.name} "
        f"(NORAD {tracked_object.norad_id}). "
        f"Closest approach: {conjunction.closest_approach_km:.2f} km "
        f"at relative velocity {conjunction.relative_velocity_kmps:.2f} km/s. "
        f"Risk score: {conjunction.risk_score:.1f}/100"
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
    db.commit()
    return alert
```

**Success Criteria:**
- Alerts created for risk_score >= 40
- response_category correctly set
- Alert message is clear and actionable
- Can query alerts by spacecraft_id and severity

### 1.6 API Endpoints Implementation

**Tasks:**
- [ ] Implement POST /api/debris/refresh
- [ ] Implement GET /api/debris/risks
- [ ] Implement GET /api/debris/status (refresh progress)
- [ ] Add error handling and logging
- [ ] Document endpoints with OpenAPI

**Endpoint Specifications:**

```python
# POST /api/debris/refresh
@router.post("/refresh")
async def refresh_debris_data(
    spacecraft_id: str = "25544",  # ISS default
    background_tasks: BackgroundTasks
):
    """
    Trigger debris risk computation (background task).
    Returns immediately with task ID.
    """
    task_id = str(uuid.uuid4())
    background_tasks.add_task(
        compute_debris_risks,
        spacecraft_id=spacecraft_id,
        task_id=task_id
    )
    return {
        "status": "started",
        "task_id": task_id,
        "message": "Debris risk computation started"
    }

# GET /api/debris/risks
@router.get("/risks")
async def get_debris_risks(
    spacecraft_id: str = "25544",
    min_risk_score: float = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get sorted list of conjunction risks for spacecraft.
    """
    risks = db.query(ConjunctionRisk).filter(
        ConjunctionRisk.spacecraft_id == spacecraft_id,
        ConjunctionRisk.risk_score >= min_risk_score
    ).order_by(
        ConjunctionRisk.risk_score.desc()
    ).limit(limit).all()
    
    return {"risks": risks, "count": len(risks)}

# GET /api/debris/status
@router.get("/status/{task_id}")
async def get_refresh_status(task_id: str):
    """Check status of background refresh task"""
    # Implementation depends on task tracking mechanism
    pass
```

**Success Criteria:**
- POST /api/debris/refresh returns immediately
- Background task completes within 30 seconds
- GET /api/debris/risks returns sorted risk table
- Error handling for invalid spacecraft_id

### 1.7 DebrisPanel UI Implementation

**Tasks:**
- [ ] Create DebrisPanel component
- [ ] Implement sortable risk table
- [ ] Add "Refresh Risk Data" button
- [ ] Display TLE disclaimer text
- [ ] Add loading states and error handling
- [ ] Style with Tailwind CSS

**Component Structure:**

```jsx
// DebrisPanel.jsx
import React, { useState, useEffect } from 'react';
import { debrisAPI } from '../services/api';

export default function DebrisPanel({ spacecraftId = "25544" }) {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  const handleRefresh = async () => {
    setLoading(true);
    try {
      const response = await debrisAPI.refresh(spacecraftId);
      // Poll for completion
      await pollRefreshStatus(response.task_id);
      await loadRisks();
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const loadRisks = async () => {
    const data = await debrisAPI.getRisks(spacecraftId);
    setRisks(data.risks);
    setLastUpdate(new Date());
  };
  
  useEffect(() => {
    loadRisks();
  }, [spacecraftId]);
  
  return (
    <div className="debris-panel p-6">
      <div className="header flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Debris Risk Assessment</h2>
        <button 
          onClick={handleRefresh}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Refreshing...' : 'Refresh Risk Data'}
        </button>
      </div>
      
      <div className="disclaimer bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
        <p className="text-sm text-yellow-800">
          ⚠️ Risk scores are derived from public two-line element (TLE) data, 
          which carries inherent positional uncertainty. This is a relative 
          risk indicator, not a collision probability.
        </p>
      </div>
      
      {lastUpdate && (
        <p className="text-sm text-gray-600 mb-4">
          Last updated: {lastUpdate.toLocaleString()}
        </p>
      )}
      
      <RiskTable risks={risks} />
    </div>
  );
}

// RiskTable.jsx
function RiskTable({ risks }) {
  const [sortField, setSortField] = useState('risk_score');
  const [sortDirection, setSortDirection] = useState('desc');
  
  const sortedRisks = [...risks].sort((a, b) => {
    const multiplier = sortDirection === 'asc' ? 1 : -1;
    return multiplier * (a[sortField] - b[sortField]);
  });
  
  const getSeverityColor = (score) => {
    if (score >= 70) return 'text-red-600 bg-red-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };
  
  return (
    <table className="w-full border-collapse">
      <thead>
        <tr className="bg-gray-100">
          <th onClick={() => handleSort('object_norad_id')}>Object ID</th>
          <th onClick={() => handleSort('closest_approach_km')}>
            Closest Approach (km)
          </th>
          <th onClick={() => handleSort('relative_velocity_kmps')}>
            Relative Velocity (km/s)
          </th>
          <th onClick={() => handleSort('risk_score')}>Risk Score</th>
        </tr>
      </thead>
      <tbody>
        {sortedRisks.map(risk => (
          <tr key={risk.id} className="border-b hover:bg-gray-50">
            <td>{risk.object_norad_id}</td>
            <td>{risk.closest_approach_km.toFixed(2)}</td>
            <td>{risk.relative_velocity_kmps.toFixed(2)}</td>
            <td>
              <span className={`px-3 py-1 rounded-full font-semibold ${getSeverityColor(risk.risk_score)}`}>
                {risk.risk_score.toFixed(1)}
              </span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

**UI Requirements:**
- Table sortable by all columns
- Risk score displayed with color coding
- Disclaimer text prominently displayed
- Loading spinner during refresh
- Last update timestamp visible
- Responsive design (mobile-friendly)

### Phase 1 Milestone Check (MANDATORY GATE)

**Must Demonstrate Before Phase 2:**

1. **Data Flow Test:**
   - Click "Refresh Risk Data" button
   - Verify background task starts
   - Confirm TLE data fetched from CelesTrak
   - Verify altitude filter reduces object count
   - Confirm SGP4 propagation completes
   - Check risk scores calculated correctly

2. **UI Verification:**
   - Risk table displays with real data
   - Can sort by each column
   - Risk scores color-coded correctly
   - Disclaimer text visible
   - Last update timestamp accurate

3. **Database Verification:**
   - `tracked_object` table populated
   - `conjunction_risk` table has entries
   - `alerts` table has debris alerts (if any high-risk)
   - Can query by spacecraft_id

4. **Performance Check:**
   - Refresh completes within 30 seconds
   - No request timeouts
   - UI remains responsive during refresh

**Deliverables:**
- Working DebrisPanel with real CelesTrak data
- Documented risk scoring formula
- Test results showing filter effectiveness
- Screenshots of working UI

**⚠️ DO NOT PROCEED TO PHASE 2 UNTIL:**
- All Phase 1 success criteria met
- Milestone check passed
- Team can explain risk scoring formula
- Demo path tested end-to-end

---

## Phase 2: Health Monitor (Core Integration)

**Objective:** Implement telemetry simulation, ML-based anomaly detection, and the unified alerts feed that proves Apogee is one integrated system, not three separate demos.

**Duration:** 4-5 days

**Why Second:** Builds on Phase 1's spacecraft_id and alerts table foundation. The unified alerts feed (health + debris) is the core integration proof.

### 2.1 Telemetry Data Model & Simulator

**Tasks:**
- [ ] Design telemetry metrics specification
- [ ] Implement baseline random walk generator
- [ ] Add synthetic fault pattern injection
- [ ] Create background task for continuous generation
- [ ] Store readings in database

**Telemetry Metrics:**

```python
TELEMETRY_METRICS = {
    "battery_voltage": {
        "baseline": 28.0,  # Volts
        "normal_range": (26.0, 30.0),
        "noise_std": 0.2,
        "unit": "V"
    },
    "internal_temp_c": {
        "baseline": 22.0,  # Celsius
        "normal_range": (18.0, 26.0),
        "noise_std": 0.5,
        "unit": "°C"
    },
    "attitude_deviation_deg": {
        "baseline": 0.5,  # Degrees
        "normal_range": (0.0, 2.0),
        "noise_std": 0.1,
        "unit": "°"
    },
    "signal_strength_db": {
        "baseline": -85.0,  # dBm
        "normal_range": (-95.0, -75.0),
        "noise_std": 2.0,
        "unit": "dBm"
    }
}
```

**Simulator Implementation:**

```python
import numpy as np
from datetime import datetime, timedelta
import asyncio

class TelemetrySimulator:
    def __init__(self, spacecraft_id: str):
        self.spacecraft_id = spacecraft_id
        self.current_values = {
            metric: spec["baseline"] 
            for metric, spec in TELEMETRY_METRICS.items()
        }
        self.fault_active = None
        
    def generate_reading(self, metric_name: str) -> float:
        """Generate single telemetry reading with random walk"""
        spec = TELEMETRY_METRICS[metric_name]
        
        # Apply fault pattern if active
        if self.fault_active and self.fault_active["metric"] == metric_name:
            return self._apply_fault_pattern(metric_name)
        
        # Normal random walk
        current = self.current_values[metric_name]
        noise = np.random.normal(0, spec["noise_std"])
        
        # Random walk with mean reversion
        drift = 0.1 * (spec["baseline"] - current)
        new_value = current + drift + noise
        
        # Clamp to reasonable bounds (wider than normal range)
        min_bound = spec["normal_range"][0] - 3 * spec["noise_std"]
        max_bound = spec["normal_range"][1] + 3 * spec["noise_std"]
        new_value = np.clip(new_value, min_bound, max_bound)
        
        self.current_values[metric_name] = new_value
        return new_value
    
    def inject_fault(self, fault_type: str, metric: str, duration_seconds: int):
        """Inject synthetic fault pattern for demo"""
        self.fault_active = {
            "type": fault_type,
            "metric": metric,
            "start_time": datetime.utcnow(),
            "duration": duration_seconds
        }
    
    def _apply_fault_pattern(self, metric_name: str) -> float:
        """Apply fault-specific behavior"""
        fault = self.fault_active
        elapsed = (datetime.utcnow() - fault["start_time"]).total_seconds()
        
        # Clear fault if duration exceeded
        if elapsed > fault["duration"]:
            self.fault_active = None
            return self.generate_reading(metric_name)
        
        spec = TELEMETRY_METRICS[metric_name]
        
        if fault["type"] == "battery_drift":
            # Gradual voltage drop
            drift_rate = -0.05  # Volts per second
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
            # Gradual signal loss
            degradation_rate = -0.5  # dBm per second
            return spec["baseline"] + (degradation_rate * elapsed)
        
        return self.generate_reading(metric_name)

# Background task
async def telemetry_generation_task(spacecraft_id: str, db: Session):
    """Continuously generate telemetry readings"""
    simulator = TelemetrySimulator(spacecraft_id)
    
    while True:
        for metric_name in TELEMETRY_METRICS.keys():
            value = simulator.generate_reading(metric_name)
            
            reading = TelemetryReading(
                spacecraft_id=spacecraft_id,
                timestamp=datetime.utcnow(),
                metric_name=metric_name,
                value=value
            )
            db.add(reading)
        
        db.commit()
        
        # Wait 2-5 seconds between readings
        await asyncio.sleep(np.random.uniform(2, 5))
```

**Success Criteria:**
- Simulator generates realistic readings
- Fault injection works reliably
- Readings stored in database
- Background task runs continuously

### 2.2 Anomaly Detection (IsolationForest - MANDATORY)

**Tasks:**
- [ ] Implement rolling window per metric
- [ ] Integrate scikit-learn IsolationForest
- [ ] Implement periodic model retraining
- [ ] Calculate anomaly scores
- [ ] Map scores to severity levels
- [ ] Create alerts for anomalies

**Anomaly Detector Implementation:**

```python
from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self, window_size: int = 100, contamination: float = 0.1):
        """
        IsolationForest-based anomaly detector.
        
        Args:
            window_size: Number of recent readings to maintain
            contamination: Expected proportion of anomalies (0.1 = 10%)
        """
        self.window_size = window_size
        self.contamination = contamination
        self.models = {}  # One model per metric
        self.windows = {}  # Rolling windows per metric
        
    def update_window(self, metric_name: str, value: float):
        """Add new reading to rolling window"""
        if metric_name not in self.windows:
            self.windows[metric_name] = []
        
        self.windows[metric_name].append(value)
        
        # Maintain window size
        if len(self.windows[metric_name]) > self.window_size:
            self.windows[metric_name].pop(0)
    
    def fit_model(self, metric_name: str):
        """Fit IsolationForest on current window"""
        if metric_name not in self.windows:
            return
        
        window = self.windows[metric_name]
        if len(window) < 20:  # Need minimum data
            return
        
        # Reshape for sklearn (needs 2D array)
        X = np.array(window).reshape(-1, 1)
        
        # Fit IsolationForest
        model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        model.fit(X)
        
        self.models[metric_name] = model
    
    def detect_anomaly(self, metric_name: str, value: float) -> dict:
        """
        Detect if new value is anomalous.
        
        Returns:
            {
                "is_anomaly": bool,
                "anomaly_score": float,  # -1 to 1 (lower = more anomalous)
                "severity": str  # "nominal" | "watch" | "critical"
            }
        """
        # Update window
        self.update_window(metric_name, value)
        
        # Refit model periodically (every 50 readings)
        if len(self.windows[metric_name]) % 50 == 0:
            self.fit_model(metric_name)
        
        # Check if model exists
        if metric_name not in self.models:
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "severity": "nominal"
            }
        
        # Predict
        model = self.models[metric_name]
        X = np.array([[value]])
        
        prediction = model.predict(X)[0]  # 1 = normal, -1 = anomaly
        score = model.score_samples(X)[0]  # Anomaly score
        
        # Map to severity
        is_anomaly = (prediction == -1)
        
        if is_anomaly:
            # More negative score = more anomalous
            if score < -0.5:
                severity = "critical"
            else:
                severity = "watch"
        else:
            severity = "nominal"
        
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": float(score),
            "severity": severity
        }

# Integration with telemetry stream
detector = AnomalyDetector()

async def process_telemetry_reading(reading: TelemetryReading, db: Session):
    """Process new reading through anomaly detector"""
    result = detector.detect_anomaly(reading.metric_name, reading.value)
    
    # Create alert if anomaly detected
    if result["is_anomaly"]:
        alert = Alert(
            spacecraft_id=reading.spacecraft_id,
            source="health",
            response_category="engineering",
            severity=result["severity"],
            message=(
                f"Anomaly detected in {reading.metric_name}: "
                f"value={reading.value:.2f}, "
                f"anomaly_score={result['anomaly_score']:.3f}"
            ),
            timestamp=reading.timestamp,
            explained=False
        )
        db.add(alert)
        db.commit()
    
    return result
```

**Why IsolationForest (Not Z-Score):**
- **Genuine ML:** IsolationForest is a learned model, z-score is just statistics
- **No assumptions:** Works without assuming normal distribution
- **Multivariate potential:** Can be extended to detect patterns across metrics
- **Judge-defensible:** Can explain "isolation" concept clearly

**Success Criteria:**
- IsolationForest detects injected faults reliably
- False positive rate <10% on normal data
- Model retrains periodically without blocking
- Anomaly scores map sensibly to severity levels

### 2.3 WebSocket Live Stream

**Tasks:**
- [ ] Implement WebSocket endpoint
- [ ] Push new readings to connected clients
- [ ] Include anomaly detection results
- [ ] Handle client connections/disconnections
- [ ] Add reconnection logic on frontend

**WebSocket Implementation:**

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Handle disconnected clients
                pass

manager = ConnectionManager()

@router.websocket("/ws/health/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    spacecraft_id: str = "25544"
):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# In telemetry generation task
async def broadcast_reading(reading: TelemetryReading, anomaly_result: dict):
    """Broadcast new reading to WebSocket clients"""
    message = {
        "type": "telemetry_update",
        "spacecraft_id": reading.spacecraft_id,
        "metric_name": reading.metric_name,
        "value": reading.value,
        "timestamp": reading.timestamp.isoformat(),
        "anomaly": anomaly_result
    }
    await manager.broadcast(message)
```

**Frontend WebSocket Hook:**

```javascript
// hooks/useWebSocket.js
import { useEffect, useState, useRef } from 'react';

export function useWebSocket(url, onMessage) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  
  const connect = () => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      
      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };
    
    wsRef.current = ws;
  };
  
  useEffect(() => {
    connect();
    
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);
  
  return { isConnected };
}
```

**Success Criteria:**
- WebSocket connection established successfully
- New readings pushed in real-time
- Frontend updates without polling
- Reconnection works after disconnect

### 2.4 Unified Alerts Feed (CRITICAL INTEGRATION PROOF)

**Tasks:**
- [ ] Implement GET /api/health/alerts endpoint
- [ ] Query shared alerts table (health + debris)
- [ ] Sort by severity and timestamp
- [ ] Add response_category badges
- [ ] Display in HealthPanel UI

**API Endpoint:**

```python
@router.get("/alerts")
async def get_unified_alerts(
    spacecraft_id: str = "25544",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get unified alerts feed (health anomalies + debris conjunctions).
    This is the core integration proof.
    """
    alerts = db.query(Alert).filter(
        Alert.spacecraft_id == spacecraft_id
    ).order_by(
        # Sort by severity first, then timestamp
        case(
            (Alert.severity == "critical", 1),
            (Alert.severity == "watch", 2),
            (Alert.severity == "nominal", 3)
        ),
        Alert.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "breakdown": {
            "health": len([a for a in alerts if a.source == "health"]),
            "debris": len([a for a in alerts if a.source == "debris"])
        }
    }
```

**UI Component:**

```jsx
// components/UnifiedAlertsFeed.jsx
export default function UnifiedAlertsFeed({ spacecraftId }) {
  const [alerts, setAlerts] = useState([]);
  
  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 5000);
    return () => clearInterval(interval);
  }, [spacecraftId]);
  
  const loadAlerts = async () => {
    const data = await healthAPI.getAlerts(spacecraftId);
    setAlerts(data.alerts);
  };
  
  const getSeverityIcon = (severity) => {
    switch(severity) {
      case 'critical': return '🔴';
      case 'watch': return '🟡';
      default: return '🟢';
    }
  };
  
  const getCategoryBadge = (category) => {
    const styles = {
      engineering: 'bg-blue-100 text-blue-800',
      flight_dynamics: 'bg-purple-100 text-purple-800'
    };
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-semibold ${styles[category]}`}>
        {category === 'engineering' ? '🔧 Engineering' : '🛰️ Flight Dynamics'}
      </span>
    );
  };
  
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
            key={alert.i