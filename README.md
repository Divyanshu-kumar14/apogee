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

## 📋 Current Status: Phase 0 Complete ✅

**Completed:**
- ✅ Project directory structure created
- ✅ Backend scaffolding (FastAPI + SQLAlchemy)
- ✅ Database models (all 5 tables including shared alerts)
- ✅ API routers (placeholder endpoints)
- ✅ Frontend scaffolding (React + Vite + Tailwind)
- ✅ Placeholder UI components for all three panels
- ✅ Basic routing and navigation

**Next Steps:** Phase 1 - Debris Risk Module (highest priority)

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
│   │   │   ├── health.py     # Health Monitor API
│   │   │   ├── debris.py     # Debris Risk API
│   │   │   └── discovery.py  # Discovery Module API
│   │   ├── services/         # Business logic (to be implemented)
│   │   ├── schemas/          # Pydantic models (to be implemented)
│   │   ├── database.py       # Database configuration
│   │   ├── models.py         # SQLAlchemy models
│   │   └── main.py           # FastAPI app
│   ├── data/                 # SQLite database
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── HealthPanel.jsx
│   │   │   ├── DebrisPanel.jsx
│   │   │   └── DiscoveryPanel.jsx
│   │   ├── services/         # API client (to be implemented)
│   │   ├── hooks/            # Custom React hooks (to be implemented)
│   │   ├── styles/
│   │   │   └── index.css     # Tailwind CSS
│   │   ├── App.jsx           # Main app component
│   │   └── main.jsx          # Entry point
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── tles/                 # Cached TLE data
│   └── tess/                 # Cached TESS light curves
├── models/                   # Trained ML models
├── docs/                     # Documentation
├── APOGEE_PRD.md            # Product Requirements Document
├── IMPLEMENTATION_PLAN.md    # Detailed implementation plan
└── README.md                # This file
```

## 🗄️ Database Schema

### Tables

1. **telemetry_reading** - Simulated spacecraft telemetry
2. **tracked_object** - Orbital objects from CelesTrak
3. **conjunction_risk** - Computed collision risks
4. **transit_candidate** - TESS exoplanet detections
5. **alerts** - Shared alerts table (INTEGRATION PROOF)

The `alerts` table is the core integration proof, storing both health anomalies and debris conjunctions with `response_category` tags.

## 🔧 Technology Stack

### Backend
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM for database
- SQLite - Zero-ops database
- sgp4 - Orbital propagation
- scikit-learn - ML (IsolationForest, Random Forest)
- lightkurve - TESS data processing

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Recharts - Data visualization
- Axios - HTTP client

### Additional (Phase 4)
- IBM watsonx/Granite - Alert explanations
- KokonutUI - Liquid-glass UI components
- Framer Motion - Animations
- Bklit - Advanced charts
- Anime.js - Light curve animations

## 📊 Implementation Phases

### Phase 0: Scaffolding ✅ COMPLETE
- Project structure
- Database schema
- Basic routing
- Placeholder UI

### Phase 1: Debris Risk (Next - 3-4 days)
- CelesTrak integration
- SGP4 propagation
- Risk scoring
- Sortable risk table

### Phase 2: Health Monitor (4-5 days)
- Telemetry simulator
- IsolationForest anomaly detection
- WebSocket streaming
- Unified alerts feed

### Phase 3: Discovery Module (3-4 days)
- TESS data caching
- BLS periodogram
- ML vetting classifier
- Light curve visualization

### Phase 4: Polish (2-3 days, time-permitting)
- IBM Granite integration
- UI polish libraries
- Stretch goals

### Phase 5: Testing & Demo (1-2 days)
- End-to-end testing
- Demo preparation
- Documentation

## ⚠️ Critical Requirements

1. **IBM Bob must be core build tool** (eligibility requirement)
2. **IsolationForest is mandatory** (no z-score fallback)
3. **ML vetting required for Discovery** (BLS alone is not ML)
4. **Unified alerts feed is integration proof** (don't skip)
5. **All disclaimers must be visible** (TLE uncertainty, simulated telemetry)

## 🎯 Success Criteria

- [ ] All 5 phases completed
- [ ] Debris risk table with real CelesTrak data
- [ ] Health anomalies detected by IsolationForest
- [ ] Unified alerts feed showing both sources
- [ ] Discovery module with ML-vetted transits
- [ ] Demo runs smoothly (5-7 minutes)

## 📝 Development Notes

### Phase 0 Completion Checklist
- ✅ Directory structure created
- ✅ Backend FastAPI app initialized
- ✅ Database models defined (all 5 tables)
- ✅ API routers created (placeholder endpoints)
- ✅ Frontend React app initialized
- ✅ Tailwind CSS configured
- ✅ All three panels created (placeholder content)
- ✅ Basic navigation working

### Next Immediate Steps
1. Implement CelesTrak TLE fetching service
2. Add SGP4 propagation logic
3. Create risk scoring algorithm
4. Build debris risk table UI
5. Test with ISS data

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