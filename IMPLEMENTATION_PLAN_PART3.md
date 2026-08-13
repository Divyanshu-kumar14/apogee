# APOGEE Implementation Plan - Part 3

## Phase 4: Polish & Additional Features (Continued)

**Priority Order:** Work through these in sequence, stop wherever time runs out.

### 4.1 IBM watsonx/Granite Alert Explainer (HIGHEST PRIORITY)

**Why First:** Directly addresses "effective use of...additional technologies" judging criterion. Low build cost, high judge visibility.

**Tasks:**
- [ ] Set up IBM watsonx API credentials
- [ ] Design prompt template for alert explanation
- [ ] Implement POST /api/health/alerts/{id}/explain endpoint
- [ ] Add caching mechanism (don't regenerate)
- [ ] Add "Explain" button to alert cards
- [ ] Display generated explanations in UI

**Implementation:**

```python
# services/alert_explainer.py
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams

class AlertExplainer:
    def __init__(self, api_key: str, project_id: str):
        self.model = Model(
            model_id="ibm/granite-13b-chat-v2",
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 200,
                GenParams.TEMPERATURE: 0.3
            },
            credentials={
                "apikey": api_key,
                "url": "https://us-south.ml.cloud.ibm.com"
            },
            project_id=project_id
        )
    
    def explain_health_alert(self, alert: Alert, telemetry_context: dict) -> str:
        """Generate natural language explanation for health anomaly"""
        
        prompt = f"""You are a spacecraft systems engineer. Explain this telemetry anomaly in clear, actionable language for mission operators.

Alert Details:
- Metric: {telemetry_context['metric_name']}
- Current Value: {telemetry_context['current_value']} {telemetry_context['unit']}
- Normal Range: {telemetry_context['normal_range']}
- Anomaly Score: {telemetry_context['anomaly_score']}
- Severity: {alert.severity}

Provide:
1. What the anomaly indicates
2. Possible causes
3. Recommended immediate actions

Keep response under 150 words, technical but clear."""

        response = self.model.generate_text(prompt=prompt)
        return response
    
    def explain_debris_alert(self, alert: Alert, conjunction_context: dict) -> str:
        """Generate natural language explanation for conjunction alert"""
        
        prompt = f"""You are a flight dynamics specialist. Explain this orbital conjunction risk in clear, actionable language for mission operators.

Alert Details:
- Object: {conjunction_context['object_name']} (NORAD {conjunction_context['norad_id']})
- Closest Approach: {conjunction_context['closest_approach_km']} km
- Relative Velocity: {conjunction_context['relative_velocity_kmps']} km/s
- Risk Score: {conjunction_context['risk_score']}/100
- Severity: {alert.severity}

Provide:
1. Assessment of collision risk
2. Key factors contributing to risk score
3. Recommended actions (monitoring vs maneuver consideration)

Keep response under 150 words, technical but clear."""

        response = self.model.generate_text(prompt=prompt)
        return response

# API endpoint
@router.post("/alerts/{alert_id}/explain")
async def explain_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    explainer: AlertExplainer = Depends(get_explainer)
):
    """Generate natural language explanation for alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Check if already explained
    if alert.explained:
        return {"explanation": alert.explanation}
    
    # Generate explanation based on source
    if alert.source == "health":
        # Get telemetry context
        context = get_telemetry_context(alert, db)
        explanation = explainer.explain_health_alert(alert, context)
    else:  # debris
        # Get conjunction context
        context = get_conjunction_context(alert, db)
        explanation = explainer.explain_debris_alert(alert, context)
    
    # Cache explanation
    alert.explanation = explanation
    alert.explained = True
    db.commit()
    
    return {"explanation": explanation}
```

**UI Integration:**

```jsx
// components/AlertCard.jsx
function AlertCard({ alert }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const handleExplain = async () => {
    setLoading(true);
    try {
      const response = await healthAPI.explainAlert(alert.id);
      setExplanation(response.explanation);
    } catch (error) {
      console.error('Failed to generate explanation:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="alert-card">
      {/* Alert content */}
      <p>{alert.message}</p>
      
      {/* Explain button */}
      <button 
        onClick={handleExplain}
        disabled={loading}
        className="text-sm text-blue-600 hover:text-blue-800 mt-2"
      >
        {loading ? 'Generating...' : '🤖 Explain with AI'}
      </button>
      
      {/* Explanation display */}
      {explanation && (
        <div className="mt-3 p-3 bg-blue-50 border-l-4 border-blue-400 rounded">
          <p className="text-sm text-gray-800">{explanation}</p>
          <p className="text-xs text-gray-500 mt-2">
            Generated by IBM Granite
          </p>
        </div>
      )}
    </div>
  );
}
```

**Success Criteria:**
- IBM watsonx API integrated successfully
- Explanations generated for both alert types
- Responses cached (no regeneration)
- Clear attribution to IBM Granite in UI
- Explanations are actionable and technical

### 4.2 KokonutUI Integration (Alert Feed Cards)

**Tasks:**
- [ ] Install KokonutUI library
- [ ] Apply liquid-glass card component to alert feed
- [ ] Test visual appearance
- [ ] Ensure accessibility maintained

**Implementation:**

```jsx
// Install: npm install kokonutui

import { GlassCard } from 'kokonutui';

function UnifiedAlertsFeed({ alerts }) {
  return (
    <div className="alerts-feed space-y-3">
      {alerts.map(alert => (
        <GlassCard
          key={alert.id}
          className="alert-glass-card"
          blur="md"
          opacity={0.8}
          borderColor={
            alert.severity === 'critical' ? 'red' :
            alert.severity === 'watch' ? 'yellow' : 'green'
          }
        >
          <AlertCardContent alert={alert} />
        </GlassCard>
      ))}
    </div>
  );
}
```

**Success Criteria:**
- Liquid-glass effect applied to alert cards
- Visual hierarchy maintained
- Performance acceptable (no lag)
- Works on all screen sizes

### 4.3 Motion Library Integration (State Transitions)

**Tasks:**
- [ ] Install Framer Motion
- [ ] Add spring animations to severity changes
- [ ] Animate alert card entry
- [ ] Test performance

**Implementation:**

```jsx
// Install: npm install framer-motion

import { motion, AnimatePresence } from 'framer-motion';

function MetricGauge({ severity, value }) {
  return (
    <motion.div
      animate={{
        borderColor: 
          severity === 'critical' ? '#dc2626' :
          severity === 'watch' ? '#f59e0b' : '#10b981'
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className="metric-gauge"
    >
      <motion.div
        animate={{ scale: severity === 'critical' ? 1.05 : 1 }}
        transition={{ type: 'spring' }}
      >
        {value}
      </motion.div>
    </motion.div>
  );
}

function UnifiedAlertsFeed({ alerts }) {
  return (
    <AnimatePresence>
      {alerts.map(alert => (
        <motion.div
          key={alert.id}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, x: -100 }}
          transition={{ type: 'spring', stiffness: 200 }}
        >
          <AlertCard alert={alert} />
        </motion.div>
      ))}
    </AnimatePresence>
  );
}
```

**Success Criteria:**
- Smooth spring-based transitions
- No jank or performance issues
- Animations enhance UX, don't distract
- Works across all panels

### 4.4 Bklit Integration (Charts & Gauges)

**Tasks:**
- [ ] Install Bklit library
- [ ] Replace Recharts with Bklit for risk table visualization
- [ ] Apply to telemetry trend gauges
- [ ] Test data binding

**Implementation:**

```jsx
// Install: npm install bklit

import { LineChart, BarChart } from 'bklit';

function RiskVisualization({ risks }) {
  const data = risks.map(r => ({
    x: r.object_norad_id,
    y: r.risk_score
  }));
  
  return (
    <BarChart
      data={data}
      height={300}
      colorScheme="danger"
      showGrid
      animate
    />
  );
}

function TelemetryTrend({ readings }) {
  const data = readings.map(r => ({
    x: new Date(r.timestamp),
    y: r.value
  }));
  
  return (
    <LineChart
      data={data}
      height={200}
      smooth
      showPoints={false}
      colorScheme="primary"
    />
  );
}
```

**Success Criteria:**
- Charts render correctly with real data
- Visual improvement over default charts
- Performance acceptable
- Responsive design maintained

### 4.5 Anime.js Integration (Discovery Module)

**Tasks:**
- [ ] Install Anime.js
- [ ] Add draw-in animation for folded light curve
- [ ] Test animation timing
- [ ] Ensure doesn't block interaction

**Implementation:**

```jsx
// Install: npm install animejs

import anime from 'animejs';
import { useEffect, useRef } from 'react';

function FoldedLightCurve({ data }) {
  const svgRef = useRef(null);
  
  useEffect(() => {
    if (svgRef.current && data) {
      // Animate path draw-in
      anime({
        targets: svgRef.current.querySelector('path'),
        strokeDashoffset: [anime.setDashoffset, 0],
        easing: 'easeInOutSine',
        duration: 1500,
        delay: 200
      });
    }
  }, [data]);
  
  return (
    <svg ref={svgRef} className="light-curve-chart">
      {/* Chart rendering */}
    </svg>
  );
}
```

**Success Criteria:**
- Smooth draw-in animation
- Doesn't delay chart interaction
- Works on candidate selection
- Enhances visual appeal

### 4.6 Spacecraft Selector Dropdown (Stretch Goal)

**Tasks:**
- [ ] Add spacecraft database table
- [ ] Implement GET /api/spacecraft endpoint
- [ ] Create dropdown component
- [ ] Wire to all panels
- [ ] Test switching between spacecraft

**Implementation:**

```python
# Additional spacecraft (beyond ISS)
SPACECRAFT_CATALOG = [
    {"id": "25544", "name": "ISS", "type": "Space Station"},
    {"id": "43013", "name": "Hubble Space Telescope", "type": "Observatory"},
    {"id": "25994", "name": "Tiangong", "type": "Space Station"},
    {"id": "37820", "name": "GOES-16", "type": "Weather Satellite"}
]

@router.get("/spacecraft")
async def list_spacecraft():
    """Get list of available spacecraft"""
    return {"spacecraft": SPACECRAFT_CATALOG}
```

```jsx
function SpacecraftSelector({ currentId, onChange }) {
  const [spacecraft, setSpacecraft] = useState([]);
  
  useEffect(() => {
    loadSpacecraft();
  }, []);
  
  const loadSpacecraft = async () => {
    const data = await api.getSpacecraft();
    setSpacecraft(data.spacecraft);
  };
  
  return (
    <select 
      value={currentId}
      onChange={(e) => onChange(e.target.value)}
      className="spacecraft-selector"
    >
      {spacecraft.map(sc => (
        <option key={sc.id} value={sc.id}>
          {sc.name} ({sc.type})
        </option>
      ))}
    </select>
  );
}
```

**Success Criteria:**
- Dropdown displays multiple spacecraft
- Switching updates all panels
- Data fetched for selected spacecraft
- No errors on switch

### 4.7 Historical Charting (Stretch Goal)

**Tasks:**
- [ ] Add time range selector
- [ ] Implement historical data query
- [ ] Create trend chart component
- [ ] Add to HealthPanel

**Implementation:**

```python
@router.get("/history")
async def get_telemetry_history(
    spacecraft_id: str,
    metric_name: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get historical telemetry data"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    readings = db.query(TelemetryReading).filter(
        TelemetryReading.spacecraft_id == spacecraft_id,
        TelemetryReading.metric_name == metric_name,
        TelemetryReading.timestamp >= cutoff
    ).order_by(TelemetryReading.timestamp).all()
    
    return {"readings": readings}
```

```jsx
function HistoricalTrend({ spacecraftId, metric }) {
  const [data, setData] = useState([]);
  const [timeRange, setTimeRange] = useState(24);
  
  useEffect(() => {
    loadHistory();
  }, [spacecraftId, metric, timeRange]);
  
  const loadHistory = async () => {
    const response = await healthAPI.getHistory(
      spacecraftId, 
      metric, 
      timeRange
    );
    setData(response.readings);
  };
  
  return (
    <div>
      <select value={timeRange} onChange={(e) => setTimeRange(e.target.value)}>
        <option value={6}>Last 6 hours</option>
        <option value={24}>Last 24 hours</option>
        <option value={72}>Last 3 days</option>
      </select>
      
      <LineChart data={data} />
    </div>
  );
}
```

**Success Criteria:**
- Historical data retrieved correctly
- Time range selector works
- Chart displays trends clearly
- Performance acceptable for large datasets

### 4.8 Export/Share View (Stretch Goal)

**Tasks:**
- [ ] Implement snapshot generation
- [ ] Add export to PDF/PNG
- [ ] Create shareable link
- [ ] Add to header

**Implementation:**

```jsx
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

function ExportButton() {
  const handleExport = async () => {
    const element = document.getElementById('dashboard-content');
    const canvas = await html2canvas(element);
    
    const pdf = new jsPDF('landscape');
    const imgData = canvas.toDataURL('image/png');
    pdf.addImage(imgData, 'PNG', 10, 10, 280, 190);
    pdf.save('apogee-dashboard.pdf');
  };
  
  return (
    <button onClick={handleExport} className="btn-secondary">
      📄 Export Dashboard
    </button>
  );
}
```

**Success Criteria:**
- PDF export works
- All panels captured
- Readable quality
- Fast generation

---

## Phase 5: Testing & Demo Preparation

**Objective:** Ensure all features work reliably for demo, prepare presenter(s), create demo script.

**Duration:** 1-2 days

### 5.1 End-to-End Testing

**Test Scenarios:**

1. **Debris Risk Flow:**
   - Click "Refresh Risk Data"
   - Verify background task starts
   - Confirm risk table populates
   - Check high-risk alerts appear in Health Monitor

2. **Health Monitor Flow:**
   - Verify live metrics updating
   - Click "Inject Battery Fault"
   - Confirm anomaly detected within 10 seconds
   - Verify Critical alert appears
   - Check unified feed shows both health and debris alerts

3. **Discovery Module Flow:**
   - Select confirmed planet candidate
   - Verify folded light curve displays
   - Check ML vetting result shown
   - Confirm no integration with alerts feed

4. **Alert Explainer Flow:**
   - Click "Explain with AI" on health alert
   - Verify Granite generates explanation
   - Check explanation is cached
   - Test on debris alert

5. **UI Polish Verification:**
   - Verify KokonutUI glass cards render
   - Check Motion animations on state changes
   - Confirm Bklit charts display correctly
   - Test Anime.js light curve animation

**Test Checklist:**
- [ ] All API endpoints respond correctly
- [ ] WebSocket connection stable
- [ ] Database queries performant
- [ ] No console errors
- [ ] Responsive design works
- [ ] All disclaimers visible
- [ ] "Simulated Telemetry" badge present

### 5.2 Performance Testing

**Metrics to Verify:**
- [ ] Debris refresh completes <30 seconds
- [ ] WebSocket latency <100ms
- [ ] Page load time <3 seconds
- [ ] No memory leaks over 1 hour
- [ ] Smooth animations (60fps)

**Load Testing:**
- [ ] 100+ tracked objects in debris catalog
- [ ] 1000+ telemetry readings in database
- [ ] 10+ alerts in unified feed
- [ ] Multiple WebSocket connections

### 5.3 Demo Script Creation

**Demo Flow (5-7 minutes):**

```markdown
# APOGEE Demo Script

## Introduction (30 seconds)
"APOGEE is a mission awareness dashboard that integrates three critical 
aspects of space operations: spacecraft health monitoring, orbital debris 
risk assessment, and scientific discovery—all in one unified interface."

## Part 1: Debris Risk Assessment (90 seconds)
1. Navigate to Debris Risk panel
2. Point out TLE disclaimer
3. Click "Refresh Risk Data"
4. Explain altitude-based pre-filtering
5. Show risk table with real CelesTrak data
6. Highlight risk scoring formula
7. Point out high-risk conjunction alert

## Part 2: Health Monitor & Integration Proof (120 seconds)
1. Navigate to Health Monitor
2. Show live telemetry metrics updating
3. Point out "Simulated Telemetry" badge
4. Explain IsolationForest anomaly detection
5. Click "Inject Battery Fault"
6. Watch anomaly detection trigger
7. **KEY MOMENT:** Show unified alerts feed with BOTH:
   - Health anomaly alert (Engineering response)
   - Debris conjunction alert (Flight Dynamics response)
8. Point out response_category badges
9. Click "Explain with AI" on an alert
10. Show IBM Granite-generated explanation

## Part 3: Discovery Module (90 seconds)
1. Navigate to Discovery Module
2. Emphasize: "Separate science tool, not integrated with operations"
3. Show candidate list
4. Select confirmed exoplanet (e.g., TOI-700)
5. Display folded light curve
6. Explain BLS detection
7. Highlight ML vetting result
8. Show rejected false positive for contrast

## Conclusion (30 seconds)
"APOGEE demonstrates genuine AI integration through:
- IsolationForest anomaly detection
- ML-vetted transit detection
- IBM Granite natural language explanations
All built with IBM Bob as the core development tool."

## Q&A Preparation
Be ready to explain:
- Why IsolationForest over z-score
- How BLS+ML vetting works
- Risk scoring formula details
- Why Discovery Module is separate
- IBM Bob's role in development
```

### 5.4 Presenter Preparation

**Technical Deep-Dive Prep:**

1. **IsolationForest Explanation:**
   - "Isolation Forest detects anomalies by measuring how easily a data point can be isolated from others. Anomalous points require fewer random splits to isolate. Unlike z-score, it doesn't assume normal distribution and can detect complex patterns."

2. **BLS+ML Vetting Pipeline:**
   - "BLS (Box Least Squares) is a classical algorithm that finds periodic dips in light curves. We pair it with a Random Forest classifier trained on features like transit depth, duration, and odd-even symmetry to distinguish real planets from eclipsing binaries and noise."

3. **Risk Scoring Formula:**
   - "Risk score combines inverse distance (exponential decay) with relative velocity (linear scaling). Close approaches with high relative velocity score highest. We explicitly don't claim this is a collision probability—TLE uncertainty is too high."

4. **Integration Architecture:**
   - "The shared alerts table is the integration proof. Both Health Monitor and Debris Risk write to it with different response_category tags. Discovery Module intentionally doesn't—it operates on different objects (stars, not spacecraft)."

5. **IBM Bob Usage:**
   - "IBM Bob was our core development tool throughout. We used it for [specific examples: code generation, debugging, architecture decisions]. The watsonx/Granite integration adds runtime AI on top of the build-time AI."

**Practice Questions:**
- "Why not use a simpler threshold-based anomaly detector?"
- "How do you handle false positives in transit detection?"
- "What's the accuracy of your risk scoring?"
- "Why isn't Discovery Module integrated with the alerts?"
- "How did IBM Bob help specifically?"

### 5.5 Documentation Finalization

**Required Documentation:**

1. **README.md:**
   - Project overview
   - Setup instructions
   - Demo instructions
   - Technology stack
   - IBM Bob usage notes

2. **ARCHITECTURE.md:**
   - System architecture diagram
   - Data flow diagrams
   - API documentation
   - Database schema

3. **ML_PIPELINES.md:**
   - IsolationForest methodology
   - BLS+ML vetting pipeline
   - Training data sources
   - Performance metrics

4. **DEMO_GUIDE.md:**
   - Demo script
   - Troubleshooting guide
   - Backup plans
   - Q&A prep

### 5.6 Final Checklist

**Pre-Demo Verification:**
- [ ] All dependencies installed
- [ ] Database seeded with test data
- [ ] TESS light curves cached
- [ ] IBM watsonx credentials configured
- [ ] All environment variables set
- [ ] Backup database created
- [ ] Demo script printed
- [ ] Presenter(s) rehearsed

**Code Quality:**
- [ ] No hardcoded credentials
- [ ] Proper error handling
- [ ] Logging implemented
- [ ] Code commented
- [ ] No debug print statements
- [ ] Git repository clean

**UI/UX:**
- [ ] All disclaimers visible
- [ ] Consistent styling
- [ ] No broken links
- [ ] Responsive design tested
- [ ] Accessibility checked
- [ ] Loading states implemented

**Compliance:**
- [ ] IBM Bob usage documented
- [ ] No fabricated data claims
- [ ] TLE uncertainty disclosed
- [ ] Simulated telemetry labeled
- [ ] Discovery Module clearly separated

---

## Risk Mitigation & Contingency Plans

### High-Risk Items

1. **CelesTrak API Downtime:**
   - **Mitigation:** Cache TLEs at build time
   - **Contingency:** Use pre-cached data, mention in demo

2. **IBM watsonx API Issues:**
   - **Mitigation:** Cache all explanations
   - **Contingency:** Show pre-generated explanations, explain caching

3. **WebSocket Connection Drops:**
   - **Mitigation:** Implement auto-reconnect
   - **Contingency:** Fall back to polling, mention in demo

4. **Anomaly Detection Not Triggering:**
   - **Mitigation:** Test fault injection thoroughly
   - **Contingency:** Use pre-recorded demo video

5. **Performance Issues During Demo:**
   - **Mitigation:** Optimize queries, add indexes
   - **Contingency:** Use smaller dataset, explain scaling

### Backup Plans

**Plan A:** Live demo with all features
**Plan B:** Live demo with cached data (no external APIs)
**Plan C:** Recorded demo video + live Q&A
**Plan D:** Slides + code walkthrough

---

## Success Metrics

### Technical Metrics
- ✅ All 5 phases completed
- ✅ All mandatory features implemented
- ✅ No critical bugs
- ✅ Performance targets met
- ✅ Code quality standards met

### Demo Metrics
- ✅ Demo runs smoothly (no crashes)
- ✅ All key features demonstrated
- ✅ Integration proof clear
- ✅ Q&A handled confidently
- ✅ Time limit respected (5-7 minutes)

### Judging Criteria Alignment
- ✅ **Innovation:** ML-based anomaly detection + transit vetting
- ✅ **Technical Execution:** Clean architecture, proper ML usage
- ✅ **IBM Bob Usage:** Core development tool, documented
- ✅ **Additional Technologies:** watsonx/Granite integration
- ✅ **Presentation:** Clear demo, confident Q&A
- ✅ **Completeness:** All core features working

---

## Post-Implementation Review

### Lessons Learned (To Document)
- What worked well?
- What was more difficult than expected?
- What would you do differently?
- What shortcuts were taken?
- What technical debt exists?

### Future Enhancements (Out of Scope)
- Real spacecraft telemetry integration
- Multi-spacecraft tracking
- Maneuver planning module
- Historical trend analysis
- Mobile app version
- Real-time collaboration features

---

## Appendix A: Quick Reference Commands

### Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python run.py

# Frontend
cd frontend
npm install
npm run dev

# Database
python scripts/init_db.py
python scripts/seed_data.py

# TESS Data
python scripts/download_tess_data.py

# ML Models
python scripts/train_transit_classifier.py
```

### Testing
```bash
# Backend tests
pytest tests/

# Frontend tests
npm test

# E2E tests
npm run test:e2e

# Performance tests
python scripts/performance_test.py
```

### Deployment
```bash
# Build frontend
npm run build

# Run production
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Docker (if time permits)
docker-compose up
```

---

## Appendix B: Troubleshooting Guide

### Common Issues

**Issue:** CelesTrak API returns 429 (rate limit)
**Solution:** Use cached TLEs, wait before retry

**Issue:** IsolationForest not detecting faults
**Solution:** Check window size, verify fault injection working

**Issue:** WebSocket disconnects frequently
**Solution:** Check firewall, increase timeout, verify reconnect logic

**Issue:** Light curves not loading
**Solution:** Verify FITS files cached, check lightkurve version

**Issue:** Granite API timeout
**Solution:** Reduce max_tokens, use cached explanations

**Issue:** Performance degradation
**Solution:** Add database indexes, optimize queries, reduce polling frequency

---

## Appendix C: Resource Links

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- React: https://react.dev/
- scikit-learn: https://scikit-learn.org/
- lightkurve: https://docs.lightkurve.org/
- sgp4: https://pypi.org/project/sgp4/
- IBM watsonx: https://www.ibm.com/watsonx

### Data Sources
- CelesTrak: https://celestrak.org/
- MAST (TESS): https://mast.stsci.edu/
- NASA Exoplanet Archive: https://exoplanetarchive.ipac.caltech.edu/

### Contest Resources
- AI Builders Challenge: [contest URL]
- IBM Bob Documentation: [Bob docs URL]
- Official Rules: [rules URL]

---

## Document Control

**Version:** 1.0  
**Last Updated:** August 13, 2026  
**Authors:** Implementation Team  
**Status:** Final  
**Next Review:** Post-implementation

---

# END OF IMPLEMENTATION PLAN

This completes the detailed phase-wise implementation plan for APOGEE. The plan is structured to:

1. **Front-load risk** (Phase 1: Debris Risk first—cleanest data)
2. **Prove integration** (Phase 2: Unified alerts feed)
3. **Add science value** (Phase 3: Discovery Module)
4. **Polish for judges** (Phase 4: IBM tech + UI)
5. **Ensure demo success** (Phase 5: Testing + prep)

Each phase has clear success criteria and mandatory gates. The team should not proceed to the next phase until the current phase's milestone check is passed.

**Critical Success Factors:**
- IBM Bob must be the core build tool (eligibility requirement)
- IsolationForest is mandatory (no z-score fallback)
- ML vetting is mandatory for Discovery Module
- Unified alerts feed is the integration proof
- All disclaimers must be visible in UI

**Time Management:**
- Phases 0-2 are mandatory (foundation + integration proof)
- Phase 3 is highly recommended (adds science value)
- Phase 4 is time-permitting (polish + IBM tech showcase)
- Phase 5 is mandatory (testing + demo prep)

Good luck with the implementation!
