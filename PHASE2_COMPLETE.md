# Phase 2 Complete: Health Monitor Module ✅

## Overview
Phase 2 implements the **Health Monitor** module with real-time telemetry streaming, ML-based anomaly detection using IsolationForest, and the **unified alerts feed** (the core integration proof).

## What Was Implemented

### Backend Components

#### 1. Telemetry Simulator (`backend/app/services/telemetry.py`)
- **Realistic telemetry generation** with random walk behavior
- **4 metrics tracked**:
  - Battery Voltage (V)
  - Internal Temperature (°C)
  - Attitude Deviation (°)
  - Signal Strength (dBm)
- **Fault injection** for demo purposes:
  - `battery_drift`: Gradual voltage drop
  - `temp_spike`: Sudden temperature increase
  - `attitude_oscillation`: Sinusoidal oscillation
  - `signal_degradation`: Gradual signal loss
- **Mean-reverting random walk**: Keeps values realistic

#### 2. Anomaly Detector (`backend/app/services/anomaly.py`)
- **IsolationForest implementation** (MANDATORY - no z-score fallback)
- **Why IsolationForest?**
  - Genuine ML model (not just statistics)
  - No normal distribution assumption
  - Explainable "isolation" concept
  - Judge-defensible for contest
- **Rolling window**: 100 readings per metric
- **Contamination**: 10% expected anomaly rate
- **Automatic retraining**: Every 50 readings
- **Severity mapping**:
  - Score < -0.5: Critical
  - Score -0.5 to 0: Watch
  - Score > 0: Nominal

#### 3. Health Router (`backend/app/routers/health.py`)
- **WebSocket streaming** (`/api/health/ws/stream`)
  - Real-time telemetry push
  - Anomaly detection results
  - Connection management
- **REST endpoints**:
  - `GET /api/health/status`: Current health snapshot
  - `GET /api/health/alerts`: **Unified alerts feed** (THE INTEGRATION PROOF)
  - `POST /api/health/inject-fault`: Demo fault injection
  - `GET /api/health/statistics`: Anomaly detection stats
- **Background task**: Continuous telemetry generation (2-5s intervals)
- **Alert creation**: Automatic alerts for detected anomalies

#### 4. Main Application (`backend/app/main.py`)
- **Lifespan management**: Starts telemetry on startup
- **Background task**: Runs telemetry generation for ISS
- **Graceful shutdown**: Cancels tasks on exit

### Frontend Components

#### 1. Health Panel (`frontend/src/components/HealthPanel.jsx`)
- **Live telemetry display**: 4 metric cards with real-time updates
- **WebSocket integration**: Receives live data stream
- **Severity badges**: Visual status indicators
- **Fault injection controls**: Demo interface for judges
- **Unified alerts feed**: Shows both health and debris alerts
- **Connection status**: Live/disconnected indicator
- **Anomaly scores**: Displays IsolationForest scores

#### 2. API Client (`frontend/src/services/api.js`)
- Updated with health endpoints
- WebSocket factory method
- Error handling

## Key Features

### 🎯 Integration Proof: Unified Alerts Table
The **shared alerts table** is the core proof of integration:
- **Single table** stores alerts from both modules
- **Source field**: Distinguishes health vs debris
- **Response category**: Engineering vs operations
- **Severity levels**: Critical, watch, nominal
- **Query endpoint**: `/api/health/alerts` returns combined feed

### 🤖 IsolationForest (MANDATORY)
- **No z-score fallback** - pure ML approach
- **Explainable**: "Isolation" concept is intuitive
- **Adaptive**: Learns from data, no hardcoded thresholds
- **Judge-friendly**: Can demonstrate learning behavior

### 📡 WebSocket Streaming
- **Real-time updates**: No polling required
- **Efficient**: Push-based architecture
- **Scalable**: Connection manager handles multiple clients

### 🧪 Demo Controls
- **Fault injection**: Controllable anomalies for judges
- **4 fault types**: Different patterns to showcase detection
- **Duration control**: Configurable fault length

## Testing Phase 2

### Prerequisites
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

### Start Services

**Terminal 1 - Backend:**
```bash
cd backend
python run.py
```
Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database tables created successfully
INFO:     Telemetry generation task started for ISS (NORAD 25544)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Expected output:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Test Scenarios

#### 1. Normal Operation
1. Open http://localhost:5173
2. Navigate to "Health Monitor" tab
3. Verify:
   - ✅ 4 metric cards showing live data
   - ✅ "Live" indicator is green
   - ✅ Values updating every 2-5 seconds
   - ✅ All metrics show "NOMINAL" severity

#### 2. Fault Injection
1. In demo controls, select:
   - Fault Type: "Battery Drift"
   - Metric: "Battery Voltage"
   - Duration: 60 seconds
2. Click "Inject Fault"
3. Verify:
   - ✅ Battery voltage starts dropping
   - ✅ Severity changes to "WATCH" or "CRITICAL"
   - ✅ Alert appears in unified feed
   - ✅ Alert shows "🏥 Health" source
   - ✅ Anomaly score becomes more negative

#### 3. Unified Alerts Feed
1. Inject a health fault (as above)
2. Trigger debris computation (from Debris panel)
3. Verify unified feed shows:
   - ✅ Health alerts (🏥 Health)
   - ✅ Debris alerts (🛰️ Debris)
   - ✅ Sorted by severity (critical first)
   - ✅ Different response categories

#### 4. WebSocket Reconnection
1. Stop backend server
2. Verify:
   - ✅ "Disconnected" indicator appears
3. Restart backend
4. Refresh page
5. Verify:
   - ✅ "Live" indicator returns
   - ✅ Data streaming resumes

#### 5. IsolationForest Learning
1. Let system run for 5+ minutes
2. Inject fault
3. Verify:
   - ✅ Detection happens quickly (model is trained)
   - ✅ Anomaly scores are meaningful
4. Check statistics endpoint:
   ```bash
   curl http://localhost:8000/api/health/statistics?spacecraft_id=25544
   ```
5. Verify:
   - ✅ Each metric has statistics
   - ✅ `has_model: true` for all metrics

### API Testing

**Health Status:**
```bash
curl http://localhost:8000/api/health/status?spacecraft_id=25544
```

**Unified Alerts:**
```bash
curl http://localhost:8000/api/health/alerts?spacecraft_id=25544&limit=50
```

**Inject Fault:**
```bash
curl -X POST "http://localhost:8000/api/health/inject-fault?fault_type=temp_spike&metric=internal_temp_c&duration_seconds=60"
```

**Statistics:**
```bash
curl http://localhost:8000/api/health/statistics?spacecraft_id=25544
```

## Success Criteria ✅

- [x] Telemetry simulator generates realistic data
- [x] IsolationForest detects anomalies (NO z-score fallback)
- [x] WebSocket streams live telemetry
- [x] Unified alerts table stores both health and debris alerts
- [x] Frontend displays live metrics with severity badges
- [x] Fault injection works for demo purposes
- [x] Alerts feed shows combined health + debris alerts
- [x] Background task runs continuously
- [x] Graceful startup/shutdown

## What's Next: Phase 3

**Discovery Module** (TESS data + BLS + ML vetting):
1. TESS data fetching from MAST
2. Box Least Squares (BLS) periodogram
3. ML-based transit vetting
4. Candidate visualization
5. **NOT integrated with alerts** (separate science tool)

## Technical Notes

### Why IsolationForest?
- **Contest requirement**: Must use genuine ML, not statistics
- **Explainable**: "Isolation" is intuitive - anomalies are easier to isolate
- **No assumptions**: Doesn't require normal distribution
- **Adaptive**: Learns from data patterns
- **Judge-friendly**: Can demonstrate learning in real-time

### Database Schema
The `alerts` table is the integration proof:
```sql
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY,
    spacecraft_id VARCHAR NOT NULL,
    source VARCHAR NOT NULL,           -- 'health' or 'debris'
    response_category VARCHAR NOT NULL, -- 'engineering' or 'operations'
    severity VARCHAR NOT NULL,          -- 'critical', 'watch', 'nominal'
    message TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    explained BOOLEAN DEFAULT FALSE,
    explanation TEXT
);
```

### Performance
- **Telemetry generation**: 2-5 second intervals
- **Model retraining**: Every 50 readings
- **Window size**: 100 readings per metric
- **WebSocket**: Push-based, no polling overhead

## Known Limitations
- Single spacecraft support (ISS only)
- In-memory model storage (resets on restart)
- No historical data persistence beyond database
- WebSocket doesn't auto-reconnect (requires page refresh)

## Demo Script for Judges

1. **Show normal operation** (30 seconds)
   - Point out live updates
   - Explain 4 metrics being monitored

2. **Inject battery drift fault** (60 seconds)
   - Show fault injection controls
   - Watch anomaly detection trigger
   - Point out alert in unified feed

3. **Show unified alerts** (30 seconds)
   - Scroll through combined health + debris alerts
   - Highlight different sources and categories
   - Explain integration proof

4. **Explain IsolationForest** (60 seconds)
   - Show anomaly scores
   - Explain "isolation" concept
   - Demonstrate it's ML, not statistics

Total demo time: ~3 minutes
