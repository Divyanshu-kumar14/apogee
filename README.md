# APOGEE - Mission Awareness Dashboard

**Tagline:** *Mission awareness at every altitude — from spacecraft health to orbital risk to scientific discovery.*

Built for the AI Builders Challenge with IBM Bob — August Theme: "Advance Space Exploration with AI."

## 🎯 Project Overview

APOGEE is a single-spacecraft mission dashboard tracking the International Space Station (ISS, NORAD ID 25544) across three integrated views:

1. **Health Monitor** — Simulated telemetry + ML-based anomaly detection (IsolationForest)
2. **Debris Risk** — Real orbital data (CelesTrak TLEs) + SGP4 propagation for collision risk scoring
3. **Discovery Module** — TESS light-curve transit detection with ML vetting (separate science tool)

## 🏗️ Architecture

```
Frontend (React + Vite + Tailwind)
         ↓
FastAPI Backend
         ↓
    SQLite Database
         ↓
Shared Alerts Table (Integration Proof)
```

## 📋 Current Status: Phase 4 Complete ✅

### Phase 0: Scaffolding ✅ COMPLETE
- ✅ Project directory structure created
- ✅ Backend scaffolding (FastAPI + SQLAlchemy)
- ✅ Database models (all 5 tables including shared alerts)
- ✅ API routers (placeholder endpoints)
- ✅ Frontend scaffolding (React + Vite + Tailwind)
- ✅ Placeholder UI components for all three panels
- ✅ Basic routing and navigation

### Phase 1: Debris Risk Module ✅ COMPLETE
- ✅ CelesTrak TLE fetching service with caching
- ✅ SGP4 orbital propagator with altitude pre-filtering
- ✅ Risk scoring algorithm (70% distance, 30% velocity)
- ✅ Background task for non-blocking computation
- ✅ Sortable risk table UI with severity badges
- ✅ TLE disclaimer prominently displayed
- ✅ Integration with shared alerts table

### Phase 2: Health Monitor ✅ COMPLETE
- ✅ Telemetry simulator with realistic random walk
- ✅ IsolationForest anomaly detection (MANDATORY - no z-score)
- ✅ WebSocket streaming for real-time updates
- ✅ Unified alerts endpoint (INTEGRATION PROOF)
- ✅ Background telemetry generation task
- ✅ Live health panel with 4 metrics
- ✅ Fault injection controls for demo
- ✅ Anomaly detection statistics

### Phase 3: Discovery Module ✅ COMPLETE
- ✅ TESS data service with mock light curve generation
- ✅ BLS periodogram for transit detection
- ✅ Random Forest ML vetting classifier (MANDATORY ML)
- ✅ Feature extraction (13+ features)
- ✅ Discovery router with all endpoints
- ✅ Background task for non-blocking search
- ✅ DiscoveryPanel.jsx with full UI
- ✅ Statistics and filtering
- ✅ **NOT integrated with alerts** (intentional design)

### Phase 4: IBM Granite LLM Integration ✅ COMPLETE
- ✅ Granite LLM service for alert explanations
- ✅ Context-aware explanation generation
- ✅ Alerts router with explain endpoint
- ✅ AlertExplanation modal component
- ✅ "Explain" buttons on all alerts
- ✅ Explanation caching in database
- ✅ IBM branding and attribution
- ✅ Health anomaly explanations (IsolationForest context)
- ✅ Debris conjunction explanations (orbital mechanics)
- ✅ Recommended action procedures

**Next Steps:** Phase 5 - Testing & Demo Preparation

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
python run.py
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at: http://localhost:5173

## 📁 Project Structure

```
apogee/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   │   ├── health.py     # Health Monitor API ✅
│   │   │   ├── debris.py     # Debris Risk API ✅
│   │   │   └── discovery.py  # Discovery Module API ✅
│   │   ├── services/         # Business logic
│   │   │   ├── telemetry.py  # Telemetry simulator ✅
│   │   │   ├── anomaly.py    # IsolationForest detector ✅
│   │   │   ├── celestrak.py  # TLE fetching ✅
│   │   │   ├── orbital.py    # SGP4 propagation ✅
│   │   │   ├── tess.py       # TESS data & BLS ✅
│   │   │   └── vetting.py    # Random Forest vetting ✅
│   │   ├── schemas/          # Pydantic models (to be implemented)
│   │   ├── database.py       # Database configuration ✅
│   │   ├── models.py         # SQLAlchemy models ✅
│   │   └── main.py           # FastAPI app ✅
│   ├── data/                 # SQLite database
│   ├── requirements.txt      # Dependencies ✅
│   └── run.py                # Entry point ✅
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── HealthPanel.jsx    # ✅ Live telemetry
│   │   │   ├── DebrisPanel.jsx    # ✅ Risk table
│   │   │   └── DiscoveryPanel.jsx # ✅ Transit candidates
│   │   ├── services/         
│   │   │   └── api.js        # API client ✅
│   │   ├── hooks/            # Custom React hooks (to be implemented)
│   │   ├── styles/
│   │   │   └── index.css     # Tailwind CSS ✅
│   │   ├── App.jsx           # Main app component ✅
│   │   └── main.jsx          # Entry point ✅
│   ├── package.json          # Dependencies ✅
│   └── vite.config.js        # Vite config ✅
├── data/
│   ├── tles/                 # Cached TLE data
│   └── tess/                 # Cached TESS light curves
├── models/                   # Trained ML models
├── docs/                     # Documentation
├── APOGEE_PRD.md            # Product Requirements Document
├── IMPLEMENTATION_PLAN.md    # Detailed implementation plan
├── PHASE1_COMPLETE.md       # Phase 1 testing guide ✅
├── PHASE2_COMPLETE.md       # Phase 2 testing guide ✅
├── PHASE3_COMPLETE.md       # Phase 3 testing guide ✅
└── README.md                # This file
```

## 🗄️ Database Schema

### Tables

1. **telemetry_reading** - Simulated spacecraft telemetry ✅
2. **tracked_object** - Orbital objects from CelesTrak ✅
3. **conjunction_risk** - Computed collision risks ✅
4. **transit_candidate** - TESS exoplanet detections ✅
5. **alerts** - Shared alerts table (INTEGRATION PROOF) ✅

The `alerts` table is the core integration proof, storing both health anomalies and debris conjunctions with `response_category` tags.

## 🔧 Technology Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database
- SQLite - Zero-ops database
- sgp4 - Orbital propagation ✅
- scikit-learn - ML (IsolationForest ✅, Random Forest ✅)
- astropy - BLS periodogram ✅
- numpy - Numerical computing ✅

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- WebSocket - Real-time streaming ✅

### Additional (Phase 4)
- IBM watsonx/Granite - Alert explanations
- Carbon Design System - IBM UI components
- Framer Motion - Animations
- Advanced charting libraries

## 📊 Implementation Phases

### Phase 0: Scaffolding ✅ COMPLETE
- Project structure
- Database schema
- Basic routing
- Placeholder UI

### Phase 1: Debris Risk ✅ COMPLETE
- CelesTrak integration
- SGP4 propagation
- Risk scoring
- Sortable risk table

### Phase 2: Health Monitor ✅ COMPLETE
- Telemetry simulator
- IsolationForest anomaly detection
- WebSocket streaming
- Unified alerts feed

### Phase 3: Discovery Module ✅ COMPLETE
- TESS data service
- BLS periodogram
- Random Forest ML vetting
- Transit candidates UI

### Phase 4: IBM Granite LLM ✅ COMPLETE
- IBM Granite integration for explanations
- Context-aware alert analysis
- Recommended action procedures
- Template-based (production-ready for watsonx.ai)

### Phase 5: Testing & Demo (1-2 days)
- End-to-end testing
- Demo preparation
- Documentation

## ⚠️ Critical Requirements

1. **IBM Bob must be core build tool** (eligibility requirement) ✅
2. **IsolationForest is mandatory** (no z-score fallback) ✅
3. **ML vetting required for Discovery** (BLS alone is not ML) ✅
4. **Unified alerts feed is integration proof** (don't skip) ✅
5. **All disclaimers must be visible** (TLE uncertainty ✅, simulated telemetry ✅)

## 🎯 Success Criteria

- [x] Phase 0: Project scaffolding
- [x] Phase 1: Debris risk module with real data
- [x] Phase 2: Health monitor with IsolationForest
- [x] Phase 3: Discovery module with ML vetting
- [x] Unified alerts feed (integration proof)
- [x] Phase 4: IBM Granite LLM integration
- [ ] Phase 5: Testing and demo preparation

## 📝 Testing Guides

- [Phase 1 Testing Guide](./PHASE1_COMPLETE.md) - Debris Risk Module
- [Phase 2 Testing Guide](./PHASE2_COMPLETE.md) - Health Monitor
- [Phase 3 Testing Guide](./PHASE3_COMPLETE.md) - Discovery Module
- [Phase 4 Testing Guide](./PHASE4_COMPLETE.md) - IBM Granite LLM Integration

## 🚀 Quick Start (After Setup)

1. **Start Backend:**
   ```bash
   cd backend && python run.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend && npm run dev
   ```

3. **Open Browser:**
   - Navigate to http://localhost:5173
   - Try the Debris Risk panel (Phase 1)
   - Try the Health Monitor panel (Phase 2)
   - Try the Discovery Module panel (Phase 3)
   - Click "🤖 Explain" on any alert (Phase 4)

## 🔗 Resources

- [Implementation Plan](./IMPLEMENTATION_PLAN.md) - Detailed phase-wise plan
- [PRD](./APOGEE_PRD.md) - Product requirements document
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [CelesTrak](https://celestrak.org/) - TLE data source
- [MAST](https://mast.stsci.edu/) - TESS data source

## 📄 License

See [LICENSE](./LICENSE) file for details.

## 🤝 Contributing

This is a hackathon project for the AI Builders Challenge. Implementation is being done via AI coding agents (IBM Bob) rather than a fixed human team.

---

**Built with IBM Bob for the AI Builders Challenge**