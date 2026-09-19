# PolarSync — Integrated Polar Expedition Simulation Engine

**SIH Problem Statement:** SIH26062  
**Component:** Software-Only Polar Expedition Environment & IoT Telemetry Simulator  
**Core Pipeline:**  
$$\text{SIMULATION} \longrightarrow \text{DETECTION} \longrightarrow \text{PREDICTION} \longrightarrow \text{DECISION} \longrightarrow \text{ALERT} \longrightarrow \text{RESPONSE}$$

---

## ❄️ 1. Overview

PolarSync's simulation engine is a deterministic, modular, Python-based simulator modeling real-world polar expedition dynamics in Antarctica. It synthetically generates IoT telemetry, tracks fleet kinematics, monitors cold-chain cargo integrity, predicts inventory autonomy burn-rates, triggers automated personnel muster roll-calls during emergencies, and provides multi-attribute decision-support for Search and Rescue (SAR) dispatch.

---

## 📐 2. Key Features

- **Polar Environment Topology**: Multi-station hierarchy (Research Base, Expedition Camps, Field Camps, Evacuation Stations, and Danger Zones such as Crevasses and Blizzard Corridors).
- **Vehicle & Helicopter Kinematics**: Waypoint-based trajectory interpolation, heading calculation, fuel burn rates, battery depletion, and engine thermal curves.
- **Personnel & Muster Roll-Call**: Continuous heartbeat and check-in intervals with automatic triage of active, field, unconfirmed, and affected personnel.
- **7-Stage Cold-Chain Cargo Tracking**:
  $$\text{PACKED} \longrightarrow \text{QC} \longrightarrow \text{LOADED} \longrightarrow \text{IN\_TRANSIT} \longrightarrow \text{ARRIVED} \longrightarrow \text{INSPECTED} \longrightarrow \text{DELIVERED}$$
  With thermal degradation curves and breach detection.
- **Inventory Autonomy & Resupply Risk**:
  $$\text{Days of Autonomy} = \frac{\text{Current Stock}}{\text{Daily Consumption Rate}}$$
  Automated multi-tier risk evaluation (`SAFE`, `MODERATE`, `HIGH`, `CRITICAL`).
- **Explainable Decision Support (SAR Dispatch)**: Multi-attribute scoring evaluating range, ETA, fuel reserve margins ($+25\%$ reserve), and capability matching (`MEDICAL_TRANSPORT`, `AERIAL`, etc.) with transparent, human-readable justification.
- **Offline Store-and-Forward Sync**: Resilient local event buffering during communication blackouts with bulk queue reconciliation upon link recovery.
- **Composite Expedition Readiness Index**: Real-time evaluation of personnel, cargo, fuel, medical supplies, vehicles, and emergency capability.

---

## 🖥️ 3. Launching PolarSync Command Center (Dashboard)

To launch the interactive **PolarSync Command Center** visualization:

```bash
streamlit run dashboard/app.py
```

### Dashboard Features:
- **Interactive Polar Operations Map**: Live display of Maitri-II Base, Field Camps, Danger Zones (Crevasse Field C-3, Blizzard Corridor), and moving vehicle/helicopter tracks.
- **Dynamic KPI Status Cards**: Real-time Expedition Readiness, Satellite Uplink status, Muster roll-call headcounts, Active Fleet ratios, and Cold-Chain integrity.
- **Cold-Chain & Cargo Pipeline**: Visual 7-stage state machine tracker (`PACKED` $\to$ `QC` $\to$ `LOADED` $\to$ `IN_TRANSIT` $\to$ `ARRIVED` $\to$ `INSPECTED` $\to$ `DELIVERED`) with thermal envelope tracking.
- **Predictive Inventory & Autonomy**: Days of Autonomy ($DoA = \frac{\text{Current Stock}}{\text{Daily Consumption}}$) vs scheduled resupply window and multi-tier risk evaluations (`SAFE`, `MODERATE`, `HIGH`, `CRITICAL`).
- **Emergency & SAR Decision Support**: Explainable asset scoring matrix, transparent justification checklist, and incident lifecycle progress (`DISPATCHED` $\to$ `ON_SCENE` $\to$ `RESOLVED`).
- **Satellite Uplink & Store-and-Forward**: Visual offline queue buffering and reconciliation stepper.
- **Interactive Telemetry Charts**: Fuel burn rates, battery profiles, velocity curves, and thermal bounds.

---

## 🚀 4. Running CLI Scenarios & Telemetry Export

### Run Individual Scenarios
```bash
python run_simulation.py --scenario 1  # Normal Expedition Operations
python run_simulation.py --scenario 2  # Fuel Shortage Crisis
python run_simulation.py --scenario 3  # Personnel Emergency & SAR Response
python run_simulation.py --scenario 4  # Cold-Chain Freezing Breach
python run_simulation.py --scenario 5  # Satellite Loss & Store-and-Forward Sync
```

### Run All Scenarios & Export Telemetry CSVs
```bash
python run_simulation.py --all --export-csv polar_telemetry.csv
```

---

## 🧪 5. Running Automated Tests

```bash
pytest
```

---

## 📂 6. Project Directory Structure

```text
polar simulator/
├── configs/
│   ├── base_environment.json         # Base coordinates, camps, danger zones, routes, fleet, personnel
│   └── scenarios/
│       ├── scenario_1_normal.json    # Nominal operations
│       ├── scenario_2_fuel_crisis.json # Fuel shortage & autonomy crash
│       ├── scenario_3_emergency_sar.json # Personnel emergency & SAR dispatch
│       ├── scenario_4_cold_chain_breach.json # Thermal insulation failure
│       └── scenario_5_connectivity_loss.json # Satellite loss & store-and-forward sync
├── dashboard/                        # Visualization Layer (Streamlit + Plotly)
│   ├── app.py                        # Main Streamlit Command Center entry point
│   ├── adapter.py                    # DashboardAdapter connecting to ScenarioRunner
│   ├── components/                   # KPI cards, Cargo, Inventory, Muster, SAR, Connectivity panels
│   ├── charts/                       # Telemetry time-series & autonomy charts
│   ├── map/                          # Plotly Polar Operations Theatre Map
│   └── utils/                        # Custom Dark Polar CSS theme
├── src/
│   ├── alerts/                       # Alert engine and alert box formatters
│   ├── core/                         # SimulationClock, EventBus, WorldState, SimulationEngine
│   ├── decision_support/             # MusterManager, SARAssetSelector, RoutePlanner, Readiness
│   ├── models/                       # Dataclasses for vehicles, cargo, inventory, personnel, alerts
│   ├── subsystems/                   # Kinematics, weather, thermal, inventory, connectivity
│   ├── utils/                        # Geospatial geodesy (Haversine, bearings) and logging
│   └── scenario_runner.py            # High-level scenario loader and runner
├── tests/                            # Pytest suite for calculations & decision logic
├── run_simulation.py                 # CLI entry point
├── requirements.txt                  # Minimal dependencies (numpy, pandas, pytest, streamlit, plotly)
└── pytest.ini
```
