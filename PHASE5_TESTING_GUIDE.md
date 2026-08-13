# Phase 5 Testing Guide: Comprehensive System Testing

## Prerequisites

Before testing, ensure:
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ Database initialized (SQLite)
- ✅ All dependencies installed

## Quick Start Testing

```bash
# Terminal 1: Start Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python run.py

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Terminal 3: Monitor logs (optional)
cd backend
tail -f logs/apogee.log  # if logging to file
```

## Test Suite 1: Health Monitor Module

### Test 1.1: Live Telemetry Streaming ✅

**Steps:**
1. Open http://localhost:5173
2. Navigate to "Health Monitor" tab
3. Observe the four metric cards

**Expected Results:**
- ✅ Battery Voltage: 26.0-30.0V, updating every 2 seconds
- ✅ Internal Temperature: 18-26°C, updating every 2 seconds
- ✅ Attitude Deviation: 0-2 degrees, updating every 2 seconds
- ✅ Signal Strength: -95 to -75 dBm, updating every 2 seconds
- ✅ WebSocket status: "Connected" indicator
- ✅ Values change smoothly (random walk)
- ✅ Anomaly scores displayed (near 0 for normal)

**Pass Criteria:**
- All metrics update in real-time
- No connection errors
- Values within normal ranges
- Smooth transitions

### Test 1.2: Fault Injection - Battery Drift ✅

**Steps:**
1. In Health Monitor tab
2. Select "Battery Drift" from dropdown
3. Select "Battery Voltage" metric
4. Set duration to 60 seconds
5. Click "Inject Fault"

**Expected Results:**
- ✅ Battery voltage starts drifting downward
- ✅ After ~10-20 seconds, anomaly detected
- ✅ Alert appears in unified feed
- ✅ Alert severity: "CRITICAL" (red badge)
- ✅ Alert message includes anomaly score
- ✅ Metric card shows anomaly score < -0.3
- ✅ After 60 seconds, returns to normal

**Pass Criteria:**
- Fault injected successfully
- Anomaly detected by IsolationForest
- Alert created and visible
- Recovery after duration

### Test 1.3: Fault Injection - Temperature Spike ✅

**Steps:**
1. Select "Temperature Spike"
2. Select "Internal Temperature"
3. Set duration to 45 seconds
4. Click "Inject Fault"

**Expected Results:**
- ✅ Temperature spikes upward
- ✅ Anomaly detected within 15 seconds
- ✅ Alert appears with "WATCH" or "CRITICAL" severity
- ✅ Returns to normal after 45 seconds

### Test 1.4: Fault Injection - Attitude Oscillation ✅

**Steps:**
1. Select "Attitude Oscillation"
2. Select "Attitude Deviation"
3. Set duration to 30 seconds
4. Click "Inject Fault"

**Expected Results:**
- ✅ Attitude deviation oscillates
- ✅ Anomaly detected
- ✅ Alert created
- ✅ Stabilizes after 30 seconds

### Test 1.5: Fault Injection - Signal Degradation ✅

**Steps:**
1. Select "Signal Degradation"
2. Select "Signal Strength"
3. Set duration to 40 seconds
4. Click "Inject Fault"

**Expected Results:**
- ✅ Signal strength degrades
- ✅ Anomaly detected
- ✅ Alert created
- ✅ Recovers after 40 seconds

### Test 1.6: Unified Alerts Feed ✅

**Steps:**
1. After injecting multiple faults
2. Scroll through unified alerts feed

**Expected Results:**
- ✅ All health alerts visible
- ✅ Correct severity badges (CRITICAL/WATCH/NOMINAL)
- ✅ Correct timestamps
- ✅ Source indicator: "🏥 Health"
- ✅ Response category shown
- ✅ "🤖 Explain" button on each alert

**Pass Criteria:**
- All alerts displayed
- Correct metadata
- Chronological order (newest first)

## Test Suite 2: Debris Risk Module

### Test 2.1: Initial Risk Computation ✅

**Steps:**
1. Navigate to "Debris Risk" tab
2. Click "Compute Conjunction Risks" button
3. Wait for computation (15-30 seconds)

**Expected Results:**
- ✅ Button shows "Computing..." state
- ✅ Computation completes without errors
- ✅ Risk table populates with objects
- ✅ ~10-20 objects shown (altitude filtered)
- ✅ Risk scores between 0-100
- ✅ Distance in kilometers
- ✅ Time to closest approach in hours
- ✅ Relative velocity in km/s

**Pass Criteria:**
- Computation completes successfully
- Table populated with data
- All columns have values
- No errors in console

### Test 2.2: Risk Table Sorting ✅

**Steps:**
1. After computation completes
2. Click "Risk Score" column header
3. Click "Distance" column header
4. Click "Time to Event" column header

**Expected Results:**
- ✅ Table sorts by clicked column
- ✅ Ascending/descending toggle works
- ✅ Sort indicator (↑/↓) visible
- ✅ Data reorders correctly

**Pass Criteria:**
- Sorting works for all columns
- Visual feedback provided
- Data accuracy maintained

### Test 2.3: High-Risk Conjunction Alert ✅

**Steps:**
1. After computation
2. Look for objects with Risk Score ≥ 70
3. Check unified alerts feed (Health Monitor tab)

**Expected Results:**
- ✅ Alert created for high-risk conjunction
- ✅ Severity: "CRITICAL" (red badge)
- ✅ Message includes object ID, risk score, distance, time
- ✅ Source indicator: "🛰️ Debris"
- ✅ Response category: "collision_avoidance"

**Pass Criteria:**
- High-risk conjunctions generate alerts
- Alerts appear in unified feed
- Correct severity and metadata

### Test 2.4: TLE Disclaimer Visibility ✅

**Steps:**
1. In Debris Risk tab
2. Scroll to bottom of page

**Expected Results:**
- ✅ Disclaimer box visible
- ✅ Text: "relative risk indicator, not collision probability"
- ✅ Mentions TLE limitations
- ✅ Yellow/warning styling

**Pass Criteria:**
- Disclaimer prominently displayed
- Clear warning about limitations

### Test 2.5: Background Computation ✅

**Steps:**
1. Click "Compute Conjunction Risks"
2. Immediately switch to Health Monitor tab
3. Switch back to Debris Risk tab

**Expected Results:**
- ✅ Computation continues in background
- ✅ UI remains responsive
- ✅ Can interact with other tabs
- ✅ Results appear when ready

**Pass Criteria:**
- Non-blocking computation
- UI responsiveness maintained

## Test Suite 3: Discovery Module

### Test 3.1: Initial Candidates Display ✅

**Steps:**
1. Navigate to "Discovery Module" tab
2. Observe initial state

**Expected Results:**
- ✅ Statistics panel shows counts
- ✅ Candidates table visible
- ✅ Some candidates may already exist (from previous searches)
- ✅ Columns: TIC ID, Period, Confidence, SNR, Depth, Duration

**Pass Criteria:**
- UI loads without errors
- Statistics accurate
- Table functional

### Test 3.2: Transit Search ✅

**Steps:**
1. In Discovery Module tab
2. Enter Sector: 1
3. Enter Camera: 1
4. Enter CCD: 1
5. Click "Search for Transits"
6. Wait for completion (10-20 seconds)

**Expected Results:**
- ✅ Button shows "Searching..." state
- ✅ Search completes without errors
- ✅ New candidates appear in table
- ✅ Statistics update
- ✅ Confidence scores between 0-1
- ✅ ML vetting applied (Random Forest)

**Pass Criteria:**
- Search completes successfully
- Candidates added to database
- ML vetting working
- Statistics accurate

### Test 3.3: Candidate Filtering ✅

**Steps:**
1. After search completes
2. Adjust "Min Confidence" slider
3. Observe table updates

**Expected Results:**
- ✅ Table filters in real-time
- ✅ Only candidates above threshold shown
- ✅ Count updates
- ✅ Smooth filtering

**Pass Criteria:**
- Filtering works correctly
- UI responsive
- Accurate results

### Test 3.4: Statistics Accuracy ✅

**Steps:**
1. Note statistics before search
2. Perform search
3. Compare statistics after

**Expected Results:**
- ✅ Total candidates increases
- ✅ High confidence count accurate (≥0.7)
- ✅ Average confidence calculated correctly
- ✅ Latest search timestamp updated

**Pass Criteria:**
- All statistics accurate
- Updates in real-time

### Test 3.5: ML Vetting Verification ✅

**Steps:**
1. Examine candidate confidence scores
2. Check for variety in scores

**Expected Results:**
- ✅ Confidence scores vary (not all 1.0 or 0.0)
- ✅ Some high confidence (≥0.7)
- ✅ Some medium confidence (0.4-0.7)
- ✅ Some low confidence (<0.4)
- ✅ Random Forest classifier working

**Pass Criteria:**
- Realistic confidence distribution
- ML model functioning
- Not all candidates accepted/rejected

## Test Suite 4: IBM Granite LLM Integration

### Test 4.1: Explain Health Anomaly ✅

**Steps:**
1. Inject a fault (battery_drift)
2. Wait for anomaly alert
3. Click "🤖 Explain" button on health alert
4. Wait for explanation generation

**Expected Results:**
- ✅ Modal opens immediately
- ✅ Loading spinner appears
- ✅ Explanation generates within 1-2 seconds
- ✅ Explanation includes:
  - Context section
  - Detected Anomaly section
  - Detection Mechanism section
  - Severity Assessment section
  - Implications section
  - Recommended Actions section
  - Technical Details section
- ✅ "Powered by IBM Granite LLM" footer visible
- ✅ Close button works

**Pass Criteria:**
- Modal functional
- Explanation comprehensive
- IBM branding visible
- No errors

### Test 4.2: Explain Debris Conjunction ✅

**Steps:**
1. Compute conjunction risks
2. Find high-risk conjunction alert
3. Click "🤖 Explain" on debris alert
4. Wait for explanation

**Expected Results:**
- ✅ Modal opens
- ✅ Explanation generates
- ✅ Debris-specific content:
  - Event Overview
  - Risk Assessment
  - Orbital Mechanics Context
  - Physical Implications
  - Collision Probability Considerations
  - Recommended Response Actions
  - Technical Details
  - Historical Context
- ✅ TLE disclaimer included
- ✅ Severity-specific recommendations

**Pass Criteria:**
- Debris explanation different from health
- Orbital mechanics context present
- Actionable recommendations

### Test 4.3: Explanation Caching ✅

**Steps:**
1. Explain an alert (any type)
2. Close modal
3. Click "🤖 Explain" again on same alert

**Expected Results:**
- ✅ Explanation loads instantly
- ✅ No loading spinner
- ✅ Same content as before
- ✅ "cached: true" in response (check network tab)

**Pass Criteria:**
- Caching working
- No regeneration
- Instant load

### Test 4.4: Multiple Alert Explanations ✅

**Steps:**
1. Generate multiple alerts (health + debris)
2. Explain each one
3. Compare explanations

**Expected Results:**
- ✅ Each alert gets unique explanation
- ✅ Health explanations differ by metric
- ✅ Debris explanations differ by object
- ✅ Context-aware content
- ✅ All well-formatted

**Pass Criteria:**
- Unique explanations per alert
- Context-specific content
- Consistent formatting

### Test 4.5: Error Handling ✅

**Steps:**
1. Stop backend server
2. Try to explain an alert
3. Restart backend
4. Try again

**Expected Results:**
- ✅ Error message displayed
- ✅ "Retry" button appears
- ✅ After restart, retry works
- ✅ Graceful degradation

**Pass Criteria:**
- Error handling functional
- User-friendly messages
- Recovery possible

## Test Suite 5: Integration Testing

### Test 5.1: Unified Alerts Integration ✅

**Steps:**
1. Generate health anomaly
2. Generate debris conjunction
3. Check unified alerts feed

**Expected Results:**
- ✅ Both alert types visible
- ✅ Correct source indicators (🏥/🛰️)
- ✅ Correct severity badges
- ✅ Chronological order
- ✅ Both explainable

**Pass Criteria:**
- Multiple sources integrated
- Shared table working
- No conflicts

### Test 5.2: Database Persistence ✅

**Steps:**
1. Generate alerts and candidates
2. Stop backend
3. Restart backend
4. Check data

**Expected Results:**
- ✅ Alerts persist
- ✅ Candidates persist
- ✅ Explanations persist
- ✅ No data loss

**Pass Criteria:**
- Data survives restart
- Database integrity maintained

### Test 5.3: Concurrent Operations ✅

**Steps:**
1. Start debris computation
2. Inject health fault
3. Start transit search
4. All simultaneously

**Expected Results:**
- ✅ All operations complete
- ✅ No conflicts
- ✅ UI remains responsive
- ✅ Results accurate

**Pass Criteria:**
- Concurrent operations supported
- No race conditions
- Data integrity maintained

### Test 5.4: WebSocket Stability ✅

**Steps:**
1. Leave Health Monitor tab open
2. Wait 5 minutes
3. Observe telemetry updates

**Expected Results:**
- ✅ Connection remains stable
- ✅ No disconnections
- ✅ Continuous updates
- ✅ No memory leaks

**Pass Criteria:**
- Long-running stability
- No connection drops
- Consistent performance

## Test Suite 6: Performance Testing

### Test 6.1: API Response Times ✅

**Steps:**
1. Open browser DevTools (Network tab)
2. Trigger various API calls
3. Measure response times

**Expected Results:**
- ✅ Health status: < 100ms
- ✅ Alerts fetch: < 200ms
- ✅ Debris computation: 15-30 seconds (background)
- ✅ Transit search: 10-20 seconds (background)
- ✅ Explain alert: 1-2 seconds

**Pass Criteria:**
- Response times acceptable
- No timeouts
- Consistent performance

### Test 6.2: Frontend Load Time ✅

**Steps:**
1. Clear browser cache
2. Load http://localhost:5173
3. Measure load time

**Expected Results:**
- ✅ Initial load: < 2 seconds
- ✅ Time to interactive: < 3 seconds
- ✅ No render blocking

**Pass Criteria:**
- Fast initial load
- Responsive UI
- Good user experience

### Test 6.3: Memory Usage ✅

**Steps:**
1. Open browser DevTools (Performance tab)
2. Use application for 10 minutes
3. Check memory usage

**Expected Results:**
- ✅ No memory leaks
- ✅ Stable memory usage
- ✅ Garbage collection working

**Pass Criteria:**
- Memory usage stable
- No continuous growth
- No leaks detected

## Test Suite 7: User Experience Testing

### Test 7.1: Navigation ✅

**Steps:**
1. Click through all tabs
2. Use browser back/forward
3. Refresh page

**Expected Results:**
- ✅ Tab switching smooth
- ✅ State preserved
- ✅ No broken navigation
- ✅ Refresh works correctly

**Pass Criteria:**
- Smooth navigation
- No errors
- State management working

### Test 7.2: Responsive Design ✅

**Steps:**
1. Resize browser window
2. Test on different screen sizes
3. Check mobile view

**Expected Results:**
- ✅ Layout adapts
- ✅ No horizontal scroll
- ✅ Readable on all sizes
- ✅ Touch-friendly on mobile

**Pass Criteria:**
- Responsive layout
- Mobile-friendly
- No layout breaks

### Test 7.3: Error Messages ✅

**Steps:**
1. Trigger various errors
2. Check error messages

**Expected Results:**
- ✅ User-friendly messages
- ✅ Clear explanations
- ✅ Actionable guidance
- ✅ No technical jargon

**Pass Criteria:**
- Clear error messages
- Helpful guidance
- Good UX

## Bug Tracking Template

```markdown
### Bug #X: [Title]

**Severity:** Critical / High / Medium / Low
**Module:** Health / Debris / Discovery / Granite / Integration
**Status:** Open / In Progress / Fixed / Closed

**Description:**
[What happened]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happened]

**Screenshots/Logs:**
[If applicable]

**Fix:**
[How it was fixed]
```

## Test Results Summary

### Module Test Results
- [ ] Health Monitor: ___/6 tests passed
- [ ] Debris Risk: ___/5 tests passed
- [ ] Discovery Module: ___/5 tests passed
- [ ] IBM Granite LLM: ___/5 tests passed
- [ ] Integration: ___/4 tests passed
- [ ] Performance: ___/3 tests passed
- [ ] User Experience: ___/3 tests passed

### Overall Status
- **Total Tests:** 31
- **Passed:** ___
- **Failed:** ___
- **Blocked:** ___
- **Pass Rate:** ___%

### Critical Issues
1. [List any critical issues found]

### Known Limitations
1. Template-based Granite (not real API)
2. Mock TESS data (not real light curves)
3. Simulated telemetry (not real spacecraft)
4. Single spacecraft only (ISS)
5. SQLite (not production database)

### Ready for Demo?
- [ ] All critical tests passed
- [ ] No blocking issues
- [ ] Performance acceptable
- [ ] UX polished
- [ ] Documentation complete

## Next Steps After Testing

1. **Fix Critical Bugs** - Address any critical issues found
2. **Document Known Issues** - List limitations and workarounds
3. **Practice Demo** - Run through demo script multiple times
4. **Record Video** - Create demo video
5. **Final Documentation** - Polish all documentation
6. **Submission Prep** - Prepare submission materials
