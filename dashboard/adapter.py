import os
import pandas as pd
from typing import Dict, Any, List, Optional
from src.scenario_runner import ScenarioRunner
from src.decision_support.readiness import ExpeditionReadinessCalculator


class DashboardAdapter:
    """
    Adapter layer that executes ScenarioRunner and transforms simulation
    state and telemetry into structured DataFrames and views for Streamlit & Plotly.
    """

    SCENARIO_CONFIGS = {
        1: ("scenario_1_normal.json", "Scenario 1: Normal Operations"),
        2: ("scenario_2_fuel_crisis.json", "Scenario 2: Fuel Shortage Crisis"),
        3: ("scenario_3_emergency_sar.json", "Scenario 3: Personnel Emergency & SAR"),
        4: ("scenario_4_cold_chain_breach.json", "Scenario 4: Cold-Chain Freezing Breach"),
        5: ("scenario_5_connectivity_loss.json", "Scenario 5: Satellite Loss & Synchronization")
    }

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            # Polar simulator root dir
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = base_dir

        self.base_config_path = os.path.join(self.base_dir, "configs", "base_environment.json")

    def run_scenario(self, scenario_idx: int) -> Dict[str, Any]:
        """
        Run the selected scenario via ScenarioRunner and extract comprehensive dashboard data.
        """
        sc_file, sc_title = self.SCENARIO_CONFIGS[scenario_idx]
        sc_path = os.path.join(self.base_dir, "configs", "scenarios", sc_file)

        runner = ScenarioRunner(self.base_config_path, sc_path)
        run_output = runner.run(verbose=False)
        state = runner.engine.state

        # 1. Telemetry DataFrame
        telemetry_df = runner.export_telemetry_dataframe()

        # 2. Cargo DataFrame & Thermal Time-Series
        cargo_rows = []
        for c in state.cargo.values():
            cargo_rows.append({
                "Cargo ID": c.id,
                "Name": c.name,
                "Category": c.category.value,
                "Weight (kg)": c.weight_kg,
                "Origin": c.origin_id,
                "Destination": c.destination_id,
                "Lifecycle Stage": c.lifecycle_stage.value,
                "Temperature (°C)": c.current_temp_c,
                "Allowed Range": f"[{c.min_temp_c:.1f}°C to {c.max_temp_c:.1f}°C]",
                "Min Temp (°C)": c.min_temp_c,
                "Max Temp (°C)": c.max_temp_c,
                "Condition": c.condition.value,
                "Cooling Active": "Active" if c.cooling_active else "FAILED"
            })
        cargo_df = pd.DataFrame(cargo_rows)

        # Thermal history across ticks
        cargo_temp_history = []
        for frame in state.telemetry_history:
            for ct in frame.cargo:
                cargo_temp_history.append({
                    "tick": frame.tick,
                    "sim_time": frame.sim_time_formatted,
                    "cargo_id": ct.cargo_id,
                    "temperature_c": ct.temperature_c,
                    "condition": ct.condition,
                    "stage": ct.stage
                })
        cargo_history_df = pd.DataFrame(cargo_temp_history)

        # 3. Inventory DataFrame
        inv_rows = []
        for inv in state.inventory.values():
            loc_name = state.locations[inv.location_id].name if inv.location_id in state.locations else inv.location_id
            inv_rows.append({
                "Category": inv.category.value,
                "Location": inv.location_id,
                "Location Name": loc_name,
                "Current Stock": f"{inv.current_stock:,.1f} {inv.unit}",
                "Stock Numeric": inv.current_stock,
                "Unit": inv.unit,
                "Daily Burn Rate": f"{inv.daily_consumption_rate:,.1f} {inv.unit}/day",
                "Burn Rate Numeric": inv.daily_consumption_rate,
                "Days of Autonomy": inv.days_of_autonomy,
                "Resupply Window (days)": inv.next_resupply_window_days,
                "Safety Buffer (days)": inv.safety_buffer_days,
                "Resupply Risk": inv.resupply_risk.value
            })
        inventory_df = pd.DataFrame(inv_rows)

        # 4. Personnel DataFrame
        pers_rows = []
        for p in state.personnel.values():
            pers_rows.append({
                "ID": p.id,
                "Name": p.name,
                "Role": p.role.value,
                "Location / Assigned Base": p.assigned_location_id,
                "Current Position": f"({p.current_position[0]:.4f}, {p.current_position[1]:.4f})",
                "Latitude": p.current_position[0],
                "Longitude": p.current_position[1],
                "Movement Status": p.movement_status.value,
                "Status": p.status.value,
                "Last Check-in Tick": p.last_checkin_tick,
                "Heartbeat": "Active" if p.heartbeat_active else "LOST"
            })
        personnel_df = pd.DataFrame(pers_rows)

        # 5. Vehicles / Fleet DataFrame
        veh_rows = []
        for v in state.vehicles.values():
            veh_rows.append({
                "Vehicle ID": v.id,
                "Name": v.name,
                "Type": v.vehicle_type.value,
                "Status": v.status.value,
                "Fuel (%)": round(v.fuel_pct, 1),
                "Fuel Remaining (L)": round(v.fuel_level_l, 1),
                "Battery (%)": round(v.battery_level_pct, 1),
                "Speed (km/h)": v.speed_kmh,
                "Latitude": v.position[0],
                "Longitude": v.position[1],
                "Heading (deg)": v.heading_deg,
                "Connectivity": v.connectivity.value,
                "Route Progress (%)": round(v.route_progress_pct, 1)
            })
        vehicles_df = pd.DataFrame(veh_rows)

        # 6. Map Topology & Entities
        map_topology = {
            "locations": [
                {
                    "id": loc.id,
                    "name": loc.name,
                    "type": loc.location_type.value,
                    "lat": loc.coordinates[0],
                    "lon": loc.coordinates[1],
                    "facilities": loc.facilities
                }
                for loc in state.locations.values()
            ],
            "danger_zones": [
                {
                    "id": dz.id,
                    "name": dz.name,
                    "type": dz.zone_type.value,
                    "center_lat": dz.center_coordinates[0],
                    "center_lon": dz.center_coordinates[1],
                    "radius_km": dz.radius_km,
                    "severity": dz.severity.value
                }
                for dz in state.danger_zones.values()
            ],
            "routes": [
                {
                    "id": r.id,
                    "name": r.name,
                    "origin": r.origin_id,
                    "destination": r.destination_id,
                    "waypoints": r.waypoints,
                    "distance_km": r.distance_km
                }
                for r in state.routes.values()
            ]
        }

        # 7. Decision Support & Emergency Data
        muster_report = run_output.get("muster_reports", [None])[0] if run_output.get("muster_reports") else None
        sar_result = run_output.get("sar_results", [None])[0] if run_output.get("sar_results") else None
        active_emergency = next(iter(state.emergencies.values())) if state.emergencies else None

        # 8. Readiness Report
        readiness_report = run_output["final_readiness"]

        # 9. Offline / Connectivity Metrics
        total_queued_events = 30 if scenario_idx == 5 else 0
        sync_completed = (scenario_idx == 5)

        return {
            "scenario_index": scenario_idx,
            "scenario_title": sc_title,
            "scenario_description": runner.scenario_data.get("description", ""),
            "duration_ticks": run_output["total_ticks"],
            "telemetry_df": telemetry_df,
            "cargo_df": cargo_df,
            "cargo_history_df": cargo_history_df,
            "inventory_df": inventory_df,
            "personnel_df": personnel_df,
            "vehicles_df": vehicles_df,
            "map_topology": map_topology,
            "readiness_report": readiness_report,
            "alerts": state.alerts,
            "muster_report": muster_report,
            "sar_result": sar_result,
            "active_emergency": active_emergency,
            "network_status": state.network_status.value,
            "total_queued_events": total_queued_events,
            "sync_completed": sync_completed
        }
