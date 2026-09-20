# PolarSync Platform — Full-Stack Web Application (Stage 3.5)

**Smart India Hackathon (SIH 2026)**  
**Problem Statement:** SIH26062 — Integrated Polar Expedition Logistics and Asset Management System

---

## ❄️ 1. Introduction

**PolarSync Platform** is the decoupled, full-stack web tier of the PolarSync Expedition Command System. Built to run alongside the validated Python simulation engine (`src/`), this platform provides a high-reliability command center with a React frontend, a FastAPI backend, Leaflet GIS mapping, **Offline-First Field Operations** with opportunistic IndexedDB synchronization, and **Explainable Operational Intelligence & Decision Support**.

---

## 🏗️ 2. Platform Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 Python Simulation Kernel                    │
│      (src/core, models, decision_support, alerts)           │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Deterministic state)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     SimulationService                       │
│             (In-memory scenario runner cache)               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    IntelligenceService                      │
│   (Autonomy, Resupply Risk, Readiness, Emergency, Forecast) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                       │
│               (/api/v1/intelligence, /sync, ...)            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                         Online API
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      React API Client                       │
│                  (Cache-First Fallback)                     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
      ┌─────────────────┐            ┌─────────────────┐
      │ IndexedDB Cache │            │   Sync Queue    │
      │(polarsync-offl.)│            │ (Offline Ops)   │
      └────────┬────────┘            └────────┬────────┘
               │                              │
               └──────────────┬───────────────┘
                              ▼
           ┌─────────────────────────────────────┐
           │ Explainable Intelligence & GIS Apps │
           └─────────────────────────────────────┘
```

---

## 🧠 3. Explainable Operational Intelligence Modules (Stage 3.5)

1. **Winter Autonomy Intelligence (`/api/v1/intelligence/autonomy`)**:
   - Analyzes real consumption burn-rates across all station inventory categories.
   - Evaluates Days of Autonomy against dynamic safety buffers and resupply windows.
2. **Resupply Risk Analysis (`/api/v1/intelligence/resupply-risk`)**:
   - Classifies risk levels (`SAFE`, `WATCH`, `AT_RISK`, `CRITICAL`) with explicit logistics actions.
3. **Expedition Readiness (`/api/v1/intelligence/readiness`)**:
   - Synthesizes 6 operational dimensions: Personnel, Fleet, Inventory, Cargo, Connectivity, Emergencies.
4. **Emergency Decision Support (`/api/v1/intelligence/emergency`)**:
   - Exposes candidate asset evaluation matrix (transit time, fuel reserve, capability match, eligibility, score).
   - Traceable selection explanation for dispatched SAR vehicle.
5. **Resource Depletion Forecasting (`/api/v1/intelligence/forecast`)**:
   - Generates deterministic linear consumption projections for fuel and mobile assets.
   - Distinguishes historical telemetry from projected depletion horizons with explicit confidence boundaries.
6. **4-Pillar Operational Explainability**:
   - **WHAT HAPPENED**: Clear synopsis of observed operational anomalies.
   - **WHY IT MATTERS**: Real-world expedition safety impact.
   - **WHAT TO WATCH**: Key telemetry metrics and thresholds to monitor.
   - **RECOMMENDED OPERATOR ACTION**: Actionable decision-support guidance.

---

## 📁 4. Directory Layout

```
polarsync-platform/
├── README.md               # Quickstart & setup documentation
├── ARCHITECTURE.md         # Component diagrams & data flows
│
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── main.py         # App factory & CORS
│   │   ├── core/           # Settings & Pydantic config
│   │   ├── api/v1/         # Operational, Sync & Intelligence routes
│   │   │   ├── endpoints/  # Scenarios, Dashboard, Assets, Personnel, Cargo,
│   │   │   │               # Inventory, Emergencies, Connectivity, Alerts, Map, Sync, Intelligence
│   │   │   └── api.py      # Router aggregation
│   │   ├── db/             # SQLAlchemy session & health probes
│   │   ├── schemas/        # Pydantic schemas (sync, intelligence, etc.)
│   │   └── services/       # SimulationService & IntelligenceService
│   ├── tests/              # Pytest test suite for intelligence & sync
│   ├── requirements.txt    # Python backend dependencies
│   └── run.py              # Server execution script
│
└── frontend/               # React 19 Single-Page Application
    ├── src/
    │   ├── App.jsx         # React Router v7 routes & Context providers
    │   ├── index.css       # Tailwind & Polar Dark Design System
    │   ├── context/        # ScenarioContext & ConnectivityContext
    │   ├── services/       # api.js & db.js (IndexedDB wrapper)
    │   ├── components/     # IntelligenceCard, RiskIndicator, ForecastChart, ExplanationPanel
    │   └── pages/          # 9 Operational module command pages
    ├── package.json        # Frontend dependencies
    └── vite.config.js      # Vite build configuration
```

---

## 📡 5. Operational API Endpoints (Stage 3.5)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/health` | `GET` | Service diagnostic probe |
| `/api/v1/scenarios` | `GET` | List 5 available polar expedition scenarios |
| `/api/v1/dashboard/summary` | `GET` | Aggregated 6-KPI command center mission status |
| `/api/v1/assets` | `GET` | Vehicle fleet kinematics and fuel reserves |
| `/api/v1/personnel` | `GET` | Personnel roster and muster roll-call state |
| `/api/v1/cargo` | `GET` | Cold-chain cargo telemetry and thermal envelopes |
| `/api/v1/inventory` | `GET` | Stock levels, burn rates, and Days of Autonomy |
| `/api/v1/emergencies` | `GET` | Active SAR incidents and multi-criteria decision matrix |
| `/api/v1/connectivity` | `GET` | Satellite status and store-and-forward metrics |
| `/api/v1/alerts` | `GET` | Operational rule engine alert stream |
| `/api/v1/map/topology` | `GET` | Stations, danger zones, routes, vehicles, and emergencies |
| `/api/v1/sync` | `POST` | Opportunistic batch synchronization for offline operations |
| `/api/v1/intelligence/summary` | `GET` | Comprehensive multi-factor intelligence summary |
| `/api/v1/intelligence/autonomy` | `GET` | Inventory winter autonomy and safety buffer intelligence |
| `/api/v1/intelligence/resupply-risk` | `GET` | Resupply risk classification and logistics guidance |
| `/api/v1/intelligence/readiness` | `GET` | 6-factor expedition readiness assessment |
| `/api/v1/intelligence/emergency` | `GET` | SAR asset selection evaluation matrix & justification |
| `/api/v1/intelligence/forecast` | `GET` | Deterministic resource depletion forecasts |

---

## 🧪 6. Testing & Validation

```bash
# 1. Run simulation kernel tests (7/7 pass)
python -m pytest tests

# 2. Run backend intelligence tests (10/10 pass)
python -m pytest polarsync-platform/backend/tests

# 3. Run frontend offline subsystem tests (5/5 pass)
node polarsync-platform/frontend/test_offline_subsystem.js

# 4. Build frontend production bundle (0 errors)
cd polarsync-platform/frontend && npm run build
```
