# APOGEE — Product Requirements Document

**Tagline:** *Mission awareness at every altitude — from spacecraft health to orbital risk to scientific discovery.*

**Context:** Built for the AI Builders Challenge with IBM Bob — August Theme: "Advance Space Exploration with AI." Target: turn data-heavy space operations into insight-driven decisions.

**Why this name:** Apogee is the point in an orbit farthest from Earth — the moment of maximum perspective. The app's job is to give a mission operator that same maximum-perspective view across three normally-siloed concerns: subsystem health, collision risk, and scientific signal.

---

## 0. Eligibility Requirement — Read This Before Writing Any Code

Per the Official Rules of the AI Builders Challenge: **"IBM Bob will be the core component of all project submissions."** This is a Project Submission Requirement, not a scoring preference — a submission that doesn't use IBM Bob as its core build tool can be disqualified regardless of code quality. "Building with AI agents" for this contest means building inside IBM Bob specifically (a Roo Code-based IDE agent tied to watsonx/Granite), not an arbitrary coding agent.

Additionally, judging explicitly scores **"Effective use of IBM Bob and additional technologies"** under Technical Execution, and there is a dedicated **"Best Technical Use of IBM Bob"** prize ($750) separate from "Most Innovative." Other IBM technologies — watsonx, Granite, LangFlow, Docling — are sanctioned optional additions on top of Bob, not substitutes for it.

**Action required before Phase 0:** confirm the build environment is IBM Bob (get access via the university signup, referenced on the challenge site). If the actual tooling is a non-IBM agent, resolve this now — it is the single highest-priority open item in this document, above every technical decision below.

---

## 1. Product Summary

Apogee is a single-spacecraft mission dashboard tracking one real, currently-active satellite (default: ISS, NORAD ID 25544) across three integrated views:

1. **Health Monitor** — simulated telemetry + ML-based anomaly detection (not fixed thresholds)
2. **Debris Risk** — real orbital data (CelesTrak TLEs) + SGP4 propagation to score collision risk against the tracked spacecraft
3. **Discovery Module** — TESS light-curve transit detection, presented as a clearly-separate science tool (no false integration claims)

**Core integration principle (do not violate):** Health Monitor and Debris Risk share a `spacecraft_id` and a unified alerts feed — a high-risk conjunction from Debris Risk appears as an alert inside Health Monitor. Discovery Module is intentionally NOT integrated into the alerts feed — it operates on a different object (a star, not the spacecraft) and forcing an integration there would be dishonest. Keep it as a separately labeled module.

---

## 2. Non-Negotiable Constraints (read before writing any code)

- **No live external API calls during a demo/judging path.** CelesTrak and MAST calls happen at build-time or on an explicit manual "Refresh" action — never automatically blocking page load or a live walkthrough. Cache everything.
- **No fabricated "probability of collision."** Debris Risk outputs a relative risk score (see §5.2) with a visible disclaimer about TLE positional uncertainty. Never present it as a precise probability.
- **No claim that data is "sent to Earth."** This app is the ground-side receiver/analyzer. Copy anywhere in the UI must reflect that framing.
- **Telemetry is explicitly labeled as simulated** in the UI (small persistent badge: "Simulated Telemetry"). Do not let the demo imply this is live real spacecraft data.
- **Anomaly detection must not be a hardcoded if/else threshold set, and must not fall back to bare rolling z-score.** Minimum bar: `scikit-learn` IsolationForest fit on a rolling window. This is a judged criterion (Technical Execution / Innovation) — do not cut this corner, and do not leave it as a team-discretion decision (see §8, decision 2 — resolved: IsolationForest is mandatory).
- **Transit detection must include an ML vetting step, not bare BLS.** BLS alone is a classical signal-processing algorithm with zero learned component — real exoplanet pipelines (e.g. NASA's Astronet) pair BLS candidate-finding with an ML classifier that vets candidates against features like transit depth, duration, and SNR to reject false positives (eclipsing binaries, noise). Apogee's Discovery Module must do the same, even if the classifier is a simple scikit-learn model trained on a small feature set.

---

## 3. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React (Vite) + Tailwind | Fast iteration, team likely already knows it |
| Backend | FastAPI (Python) | Same language as the science/orbital stack (sgp4, lightkurve, sklearn) — avoids a second language for the team to context-switch into |
| Live updates | WebSocket (FastAPI native) | Only Health Monitor needs push updates |
| Database | SQLite | Zero-ops for a hackathon; upgrade to Postgres only if the team already knows it |
| Orbital mechanics | `sgp4` (Python lib) | Do not hand-roll propagation |
| Anomaly detection | `scikit-learn` IsolationForest (mandatory — no z-score fallback) | Genuine ML is a scored requirement, not a nice-to-have — see §0 |
| Transit vetting | `scikit-learn` classifier on BLS-derived features (depth, duration, SNR) | Turns BLS from a bare classical algorithm into an ML-vetted pipeline — mirrors real exoplanet vetting (BLS finds candidates, ML vets them) |
| LLM alert summarization | IBM watsonx / Granite (sanctioned add-on per contest rules) | Natural-language explanation of anomalies/risk scores — cheapest way to get visible LLM-based AI into the runtime product, not just the build tool |
| UI polish | KokonutUI, Motion, Bklit, Anime.js | See §6.1 — scoped narrowly, Phase 4 only |

**Note on build approach:** implementation is being done via AI coding agents rather than a fixed human team roster. This removes *build-capacity* as a constraint but does not remove *defensibility* as one — whoever presents to judges still needs to be able to answer a follow-up question about how each pipeline works, regardless of who/what wrote the code. Budget time for the presenter(s) to actually understand each pipeline before demo day, not just to have working code.

---

## 4. Architecture

```
React Frontend
      │
      ▼
FastAPI Gateway (single app, routed)
      │
      ├── /api/health/*     → in-memory/SQLite state + WebSocket push
      ├── /api/debris/*     → SQLite (precomputed on refresh, not per-request)
      └── /api/discovery/*  → SQLite (precomputed at build time from cached TESS data)

Shared table: `alerts`
  - id, spacecraft_id, source ("health"|"debris"), severity, message, timestamp
  - Health Monitor UI reads this table AND its own live WebSocket stream
  - Debris Service writes to this table when it finds a high-risk conjunction
```

**Why one alerts table matters:** this is the entire technical justification for calling Apogee "one system" instead of "three demos in a trenchcoat." Do not skip it, do not defer it to a stretch goal — it is cheap to build and is load-bearing for the pitch.

---

## 5. Feature Specs

### 5.1 Health Monitor

**Data model**
```
telemetry_reading:
  spacecraft_id, timestamp, metric_name, value
  metrics to simulate: battery_voltage, internal_temp_c, attitude_deviation_deg, signal_strength_db
```

**Simulator behavior**
- Background task emits a reading per metric every 2–5 seconds
- Baseline: normal random walk around a realistic setpoint per metric
- Inject synthetic fault patterns on a timer or button trigger (for demo control): e.g. battery voltage drift, temperature spike — so the demo can reliably show detection working, not hope randomness cooperates on stage

**Anomaly detection**
- Maintain rolling window (last N readings) per metric
- Score new readings against the window (z-score threshold, or IsolationForest fit periodically on the window)
- Severity bands: nominal / drifting / critical — same three-tier scale used everywhere else in the app (§8)

**API**
- `GET /api/health/status` — current snapshot, all metrics + severity
- `WS /api/health/stream` — push new readings + anomaly flags
- `GET /api/health/alerts` — merged feed: anomaly flags + debris conjunction alerts (reads shared `alerts` table)
- `POST /api/health/inject-fault` — demo control, manually trigger a fault pattern

### 5.1a Shared Alerts Table — Response Category (fixes operational realism)

A thermal anomaly needs an engineering response; a conjunction alert needs a flight-dynamics/maneuver response. Merging both into one undifferentiated stream is operationally unrealistic even though the merge itself is the core integration proof. Fix: tag every alert with its owning response domain and render it as a visible badge — keep the unified feed (real mission control common-operating-picture displays do surface cross-domain alerts to a flight director even though different sub-teams action them), but stop implying they're the same kind of event.

```
alerts table addition:
  response_category: "engineering" | "flight_dynamics"
```

HealthPanel's unified feed renders both alert types together, sorted by severity, each with a category badge — proves integration without pretending the two alert types are operationally interchangeable.

### 5.2 Debris Risk

**Data model**
```
tracked_object:
  norad_id, name, tle_line1, tle_line2, last_updated
conjunction_risk:
  spacecraft_id, object_norad_id, closest_approach_km, relative_velocity_kmps,
  risk_score (0-100), computed_at
```

**Pipeline**
1. On manual refresh: fetch spacecraft TLE + catalog subset from CelesTrak GP query (JSON format)
2. **Mandatory pre-filter before propagation:** the full tracked-object catalog runs to roughly 16,000+ active satellites and ~45,000 objects including debris and rocket bodies — running SGP4 across the full set synchronously will cause a compute spike and risk a request timeout during a live demo. Filter to objects whose apogee/perigee altitude band overlaps the tracked spacecraft's orbital shell (with a reasonable buffer) before propagating anything. This mirrors real conjunction-screening methodology (coarse altitude filter, then fine-grained propagation on the reduced set).
3. **Run as a background task, not inline in the request handler**, regardless of filtering — filtering reduces object count, it does not guarantee the computation finishes within a single request/response cycle. Expose a `/api/debris/refresh` (trigger) + status check, not a blocking call.
4. SGP4-propagate spacecraft and the filtered candidate set over a lookahead window (start with 24–48h, tune for demo)
5. Compute minimum separation distance per object pair
6. Risk score = function of (inverse distance, relative velocity) — document the formula in-code, keep it simple and explainable, not a black box
7. Any object above a risk threshold → write row to `conjunction_risk` AND insert a row into shared `alerts` table (tagged `response_category: "flight_dynamics"` — see §5.1a)

**Required disclaimer, verbatim intent, placed in UI near the risk table:**
> "Risk scores are derived from public two-line element (TLE) data, which carries inherent positional uncertainty. This is a relative risk indicator, not a collision probability."

**API**
- `POST /api/debris/refresh` — triggers the pipeline above (manual, not automatic)
- `GET /api/debris/risks` — sorted risk table for the tracked spacecraft

### 5.3 Discovery Module (Transit Detection)

**Data model**
```
transit_candidate:
  tic_id, target_name, period_days, transit_depth, bls_power, flagged_at
```

**Pipeline (build-time, cached — not live during demo)**
1. Pre-select 5–10 known TIC IDs (mix of confirmed exoplanet hosts + a couple of clean negatives, for demo contrast)
2. Download light curves via `lightkurve`, cache locally
3. Detrend PDCSAP flux
4. Run BLS periodogram, extract best period/depth/power
5. **ML vetting step (mandatory, not optional):** feed BLS-derived features (depth, duration, SNR, odd-even transit depth mismatch) into a lightweight scikit-learn classifier trained to distinguish likely-planet signals from false positives (eclipsing binaries, instrumental noise). This is what makes Discovery Module an ML pipeline rather than a bare classical-algorithm demo — BLS alone has no learned component and will read as "no AI" to a technical judge.
6. Store BLS + vetting results in `transit_candidate` table

**API**
- `GET /api/discovery/candidates` — precomputed list
- `GET /api/discovery/candidates/{tic_id}/lightcurve` — folded light curve data for charting

**UI requirement:** visually and label-wise distinct section — do not place it inside the same alert feed as Health/Debris. Header copy should say something like "Science Module — independent of spacecraft telemetry" so nobody mistakes it for an integrated alert source.

### 5.4 Alert Explainer (watsonx/Granite — sanctioned add-on)

Per contest rules, IBM technologies beyond Bob (watsonx, Granite) are explicitly permitted additions. The cheapest, most judge-visible way to use one: a natural-language summarizer that takes a raw alert (anomaly metric + severity, or conjunction risk score + object name) and generates a plain-English mission-ops explanation — e.g. "Battery voltage has dropped 12% below baseline over the last 6 readings, consistent with a discharge fault rather than normal load variation."

**API**
- `POST /api/health/alerts/{id}/explain` — sends alert data to Granite, returns generated explanation, cache the result (don't regenerate on every view)

**Why this belongs in the MVP, not Phase 4 polish:** it directly serves the "effective use of...additional technologies" judging language, is low build cost (single API call + prompt), and gives judges a concrete answer when they ask "where's the AI" beyond the classifiers already in Health Monitor and Discovery Module.

---

## 6. Frontend Structure

```
App Shell
  ├── Header (spacecraft selector — hardcoded to ISS for MVP, dropdown is a stretch goal)
  ├── HealthPanel
  │     - live metric gauges (4 metrics)
  │     - unified alert feed (health anomalies + debris conjunctions, same severity colors)
  │     - "Inject Fault" demo button
  ├── DebrisPanel
  │     - sortable risk table
  │     - "Refresh Risk Data" button
  │     - disclaimer text (§5.2)
  └── DiscoveryPanel (visually separated, different header treatment)
        - candidate list
        - folded light-curve chart on selection
```

**Shared severity scale (use identical colors/labels everywhere):**
- 🟢 Nominal
- 🟡 Watch
- 🔴 Critical

### 6.1 UI Polish Layer — scoped narrowly, do not let this expand

These are visual libraries layered onto real, already-working data components. They are not a substitute for the data pipelines and must not be started before the corresponding pipeline (Phase 1/2/3) is functional. Each entry below maps to a specific component, not "make the app look nice" in general.

| Library | Apply to | Purpose |
|---|---|---|
| **KokonutUI** | Health Panel unified alert feed cards; Debris Panel risk table container | Liquid-glass card component wrapping the alert feed — this is the component judges will look at longest since it's the visual proof of the health+debris integration. Highest-priority polish item. |
| **Motion** | Severity state transitions (nominal → watch → critical) across all panels | Spring-based transition on state change, so a triggered fault or a new conjunction alert is visibly, physically reactive — not just a repaint. |
| **Bklit** | Debris risk table visualization; telemetry trend gauges | Replace default chart library output for risk-score and telemetry-trend views. Only worth doing once real data is flowing (post Phase 1–2). |
| **Anime.js** | Discovery Module: light-curve chart draw-in on candidate selection | Lightweight reveal animation for the folded light curve. Lowest priority — cosmetic layer on the least-integrated feature. |

**Explicitly excluded, with reasons (do not revisit without new justification):**
- **Magic UI (Globe / Animated Beam):** no component in Apogee's data model is a globe or a connected-logos diagram. No data to visualize this way — would be decoration with nothing behind it.
- **React Bits (WebGL shaders):** Apogee is an operations dashboard with no marketing hero page. There is no section for a shader background to live in.
- **Rive:** cursor-reactive/interactive mascot animation has no functional mapping to telemetry or risk data — nothing in the data model for it to react to.
- **Limora:** generates on-brand illustrative art/mockups. Apogee's visual need is accurate charts of real data, not generated imagery — wrong category of tool for this product.

---

## 7. Build Order — Implement in This Sequence

This order is deliberate: it front-loads the feature with the cleanest data and clearest payoff, defers the riskiest/most compute-heavy piece, and ensures there's always a demoable product at the end of each phase.

**Phase 0 — Scaffolding (do first, small)**
- FastAPI app skeleton, SQLite schema (all three tables + shared `alerts`), React app skeleton, basic routing/panels with placeholder data

**Phase 1 — Debris Risk (cleanest data, clearest win)**
- CelesTrak fetch → SGP4 propagation → risk scoring → `/api/debris/risks`
- DebrisPanel UI with real data
- Milestone check: can you show a real risk table for ISS against real catalog objects? If not, do not proceed to Phase 2.

**Phase 2 — Health Monitor (builds on Phase 1's spacecraft_id)**
- Telemetry simulator + rolling anomaly detection
- WebSocket live stream + HealthPanel UI
- Wire the shared `alerts` table both directions (anomalies AND debris conjunctions render together)
- Milestone check: trigger a fault via the demo button and confirm it appears as a Critical alert alongside a debris alert in the same feed. This is the proof that Apogee is one system, not three. Do not skip this check.

**Phase 3 — Discovery Module (only if team bandwidth allows — see open question below)**
- Pre-download and cache TESS light curves for chosen TIC IDs
- BLS pipeline, store results
- DiscoveryPanel UI, clearly separated

**Phase 4 — Polish (time-permitting)**
- UI Polish Layer (§6.1): KokonutUI on alert feed first, Motion on state transitions second, Bklit on charts third, Anime.js on Discovery Module last — in that priority order, stop wherever time runs out
- Spacecraft selector dropdown (multiple real satellites)
- Historical charting for telemetry trends
- Export/share view for judges

---

## 8. Open Decisions Requiring Team Input Before Phase 1 Starts

1. **RESOLVED — anomaly detection method:** IsolationForest is mandatory, z-score fallback removed (see §0, §2). Not a discretionary choice.
2. **Debris propagation lookahead window** (24h vs 48h vs 72h) — affects both realism and how many conjunctions you'll find to demo. Test this empirically once Phase 1 data is flowing; don't guess in advance.
3. **Build environment confirmation (§0):** verify the actual coding agent in use is IBM Bob, not a substitute. This is an eligibility requirement, resolve before Phase 0.
4. **Presenter defensibility:** whoever demos must be able to explain IsolationForest, the BLS+ML vetting pipeline, and the debris risk formula if a judge asks — independent of which AI agent wrote the code.

---

## 9. Explicit Non-Goals (state these in the pitch to preempt judge questions)

- Not a replacement for real ground station / DSN infrastructure — this is an analysis and decision-support layer on top of data that's already been received.
- Not claiming precise collision probability — relative risk scoring only, with stated uncertainty.
- Not using live spacecraft telemetry — simulated, clearly labeled.
- Discovery Module is not claimed to be architecturally integrated with the other two features — it is a separate science tool sharing the same dashboard shell.
