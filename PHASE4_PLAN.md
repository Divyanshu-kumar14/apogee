# Phase 4 Implementation Plan: Polish & IBM Integrations

## Overview
Phase 4 focuses on IBM-specific integrations and UI polish to enhance the demo experience and meet contest requirements.

## Goals
1. Integrate IBM Granite LLM for alert explanations
2. Add Carbon Design System components (optional - time permitting)
3. Polish UI/UX across all panels
4. Prepare for demo presentation

## Priority Order

### High Priority (Must Have)
1. **IBM Granite LLM Integration** ✅ Contest Requirement
   - Alert explanation generation
   - Natural language insights
   - Context-aware responses

2. **Alert Explanation UI**
   - "Explain" button on alerts
   - Modal/panel for explanations
   - Loading states

3. **Demo Preparation**
   - Demo script refinement
   - Key talking points
   - Judge Q&A preparation

### Medium Priority (Should Have)
1. **UI Polish**
   - Consistent styling
   - Loading states
   - Error handling improvements
   - Responsive design fixes

2. **Data Visualization**
   - Light curve charts (Discovery)
   - Telemetry trend charts (Health)
   - Risk timeline (Debris)

### Low Priority (Nice to Have)
1. **Carbon Design System**
   - Replace Tailwind components
   - IBM branding
   - Consistent design language

2. **Animations**
   - Smooth transitions
   - Loading animations
   - Alert notifications

## Implementation Strategy

### 1. IBM Granite LLM Integration

**Approach:**
- Use IBM watsonx.ai API or local Granite model
- Create explanation service in backend
- Add endpoint: `POST /api/alerts/{id}/explain`
- Generate context-aware explanations

**Features:**
- Explain health anomalies (why IsolationForest flagged it)
- Explain debris risks (orbital mechanics context)
- Suggest response actions
- Provide technical details

**Example Explanations:**

*Health Anomaly:*
```
The battery voltage dropped from 28.0V to 26.5V over 60 seconds, 
which is 3.2 standard deviations below the normal range. The 
IsolationForest model detected this as anomalous because the rate 
of change is inconsistent with typical battery discharge patterns. 

Recommended Action: Check battery health and charging system.
```

*Debris Conjunction:*
```
Object 12345 will pass within 2.3 km of ISS in 4.2 hours. The 
relative velocity is 7.8 km/s. Based on SGP4 propagation, this 
represents a high-risk conjunction requiring operational response.

Recommended Action: Prepare collision avoidance maneuver if risk 
exceeds threshold.
```

### 2. Backend Implementation

**New Service:** `backend/app/services/granite.py`
- Granite LLM client
- Prompt templates
- Context building
- Response formatting

**New Endpoint:** `backend/app/routers/alerts.py`
- `POST /api/alerts/{id}/explain`
- Fetch alert details
- Generate explanation
- Update alert with explanation

**Database Update:**
- Alert model already has `explanation` field ✅
- Just need to populate it

### 3. Frontend Implementation

**Alert Explanation UI:**
- Add "Explain" button to each alert
- Show loading spinner during generation
- Display explanation in expandable section
- Cache explanations (don't regenerate)

**Components:**
- `AlertExplanation.jsx` - Explanation display
- Update `HealthPanel.jsx` - Add explain buttons
- Update `DebrisPanel.jsx` - Add explain buttons

### 4. UI Polish

**Consistency:**
- Standardize button styles
- Consistent spacing
- Unified color scheme
- Loading states everywhere

**Error Handling:**
- Graceful degradation
- User-friendly error messages
- Retry mechanisms

**Responsive Design:**
- Mobile-friendly layouts
- Tablet optimization
- Desktop enhancements

## Implementation Steps

### Step 1: Granite Service (Backend)
1. Create `backend/app/services/granite.py`
2. Implement LLM client (mock or real)
3. Create prompt templates
4. Test explanation generation

### Step 2: Alerts Router (Backend)
1. Create `backend/app/routers/alerts.py`
2. Add explain endpoint
3. Integrate with Granite service
4. Update alert model

### Step 3: Explanation UI (Frontend)
1. Create `AlertExplanation.jsx` component
2. Add explain buttons to alerts
3. Handle loading/error states
4. Display explanations

### Step 4: UI Polish
1. Standardize component styles
2. Add loading states
3. Improve error handling
4. Test responsive design

### Step 5: Demo Preparation
1. Create demo script
2. Prepare talking points
3. Test full workflow
4. Document key features

## Technical Decisions

### Granite LLM Approach

**Option A: IBM watsonx.ai API** (Preferred if available)
- Pros: Official IBM integration, production-ready
- Cons: Requires API key, internet connection

**Option B: Mock Granite Service** (Fallback for demo)
- Pros: Works offline, no API key needed
- Cons: Not real LLM, template-based

**Decision:** Start with mock service, upgrade to real API if available

### Carbon Design System

**Decision:** Skip for now (time constraint)
- Tailwind CSS is working well
- Carbon would require significant refactoring
- Focus on functionality over branding

## Success Criteria

- [x] Phase 0-3 complete
- [ ] IBM Granite integration working
- [ ] Alert explanations generated
- [ ] UI polished and consistent
- [ ] Demo script prepared
- [ ] All features tested

## Timeline

- **Granite Integration:** 2-3 hours
- **UI Implementation:** 1-2 hours
- **Polish & Testing:** 1-2 hours
- **Demo Prep:** 1 hour

**Total:** 5-8 hours

## Notes

- Focus on IBM Granite integration (contest requirement)
- Keep UI polish minimal but effective
- Prioritize demo readiness
- Document everything for judges
