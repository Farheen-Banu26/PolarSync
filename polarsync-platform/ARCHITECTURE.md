# PolarSync Platform — System Architecture (Stage 3.5)

**Smart India Hackathon (SIH 2026)**  
**Problem Statement:** SIH26062 — Integrated Polar Expedition Logistics and Asset Management System

---

## 1. Multi-Tier System Topology

```
┌─────────────────────────────────────────────────────────────┐
│                 Python Simulation Kernel                    │
│      (src/core, models, decision_support, alerts)           │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Deterministic simulation state)
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
│       (/api/v1/intelligence/*, /sync, /dashboard, etc.)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                         Online API
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      React API Client                       │
│          (Transparent IndexedDB Cache Fallback Layer)       │
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

## 2. Explainable Intelligence Service Layer

The `IntelligenceService` is decoupled from both the simulation kernel and the frontend client. It derives actionable insights through deterministic domain models without external AI API dependencies:

### A. Winter Autonomy Intelligence
- Consumes real stock quantities and daily consumption burn-rates.
- Evaluates $Days\ of\ Autonomy = \frac{Current\ Stock}{Daily\ Burn\ Rate}$.
- Compares against dynamic thresholds:
  - $Critical = DoA < Safety\ Buffer$
  - $Watch / At\ Risk = DoA < (Safety\ Buffer + Resupply\ Window)$
  - $Safe = DoA \ge (Safety\ Buffer + Resupply\ Window)$

### B. Multi-Factor Expedition Readiness Methodology
Synthesizes 6 operational dimensions:
1. **Personnel**: Heartbeat telemetry, accounted count vs total roster, missing muster triage.
2. **Fleet**: Vehicle availability ratio, active mission status, fuel reserves.
3. **Inventory**: Minimum autonomy across consumables, safety buffer breaches.
4. **Cargo / Cold-Chain**: Thermal deviation logs, breached vs nominal package condition.
5. **Connectivity**: Satellite link status, local NVRAM store-and-forward queue state.
6. **Emergencies**: Active incident severity, triage status, and SAR progress.

### C. SAR Decision Support Engine
Exposes multi-criteria candidate evaluation:
$$\text{Score} = w_1 \cdot \text{TransitTime} + w_2 \cdot \text{FuelMargin} + w_3 \cdot \text{Capabilities} - \text{Penalties}$$
Provides full visibility into candidate distance, ETA, fuel post-mission, eligibility, and disqualification reasons.

### D. Resource Depletion Forecasting
- Projects future consumption using empirical daily burn rates over a 48-hour horizon.
- Clearly distinguishes historical telemetry points from projected estimates.
- Accompanied by confidence boundaries and domain explanations.

---

## 3. Operational Explainability Design (4 Pillars)

Every intelligence response and dashboard view presents structured explainability:
1. **WHAT HAPPENED**: Clear factual summary of observed telemetry or system state.
2. **WHY IT MATTERS**: Operational severity and risk to expedition personnel and habitat power.
3. **WHAT TO WATCH**: Key telemetry metrics and thresholds to monitor closely.
4. **RECOMMENDED OPERATOR ACTION**: Concrete, actionable guidance for decision-makers.

---

## 4. Offline-First Synchronization & Data Resilience

1. **IndexedDB Engine (`polarsync-offline`)**:
   - `operational_cache`: Stores scenario resource snapshots (`scenario:{id}:{resource}`).
   - `sync_queue`: Stores queued offline mutations (`PENDING` $\rightarrow$ `SYNCING` $\rightarrow$ `SYNCED` / `FAILED`).
   - `metadata`: Tracks synchronization timestamps and cache age.
2. **Opportunistic Sync API (`POST /api/v1/sync`)**:
   - Accepts batches of local offline mutations.
   - Validates operations against domain constraints.
   - Acknowledges accepted records and rejects unsupported actions with transparent reasons without claiming PostgreSQL persistence.
