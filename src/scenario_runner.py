import json
import os
from typing import Dict, Any, Optional, List
import pandas as pd
from .core.engine import SimulationEngine
from .models.environment import Location, LocationType, DangerZone, DangerZoneType, DangerSeverity, Route
from .models.vehicle import Vehicle, VehicleType, VehicleStatus, ConnectivityStatus, VehicleCapability
from .models.personnel import Personnel, PersonnelRole, PersonnelStatus, MovementStatus
from .models.cargo import CargoItem, CargoCategory, CargoLifecycleStage, CargoCondition
from .models.inventory import InventoryItem, InventoryCategory
from .models.emergency import EmergencyIncident, EmergencySeverity, EmergencyStatus
from .alerts.formatters import format_alert_box
from .decision_support.readiness import ExpeditionReadinessCalculator


class ScenarioRunner:
    def __init__(self, base_config_path: str, scenario_config_path: str):
        self.base_config_path = base_config_path
        self.scenario_config_path = scenario_config_path
        
        with open(base_config_path, "r", encoding="utf-8") as f:
            self.base_data = json.load(f)

        with open(scenario_config_path, "r", encoding="utf-8") as f:
            self.scenario_data = json.load(f)

        seed = self.scenario_data.get("random_seed", 42)
        mins_per_tick = self.scenario_data.get("minutes_per_tick", 1)
        self.engine = SimulationEngine(seed=seed, minutes_per_tick=mins_per_tick)
        self.muster_reports: List[Any] = []
        self.sar_results: List[Any] = []
        self._initialize_state()

    def _initialize_state(self):
        env_data = self.base_data.get("environment", {})
        state = self.engine.state

        # 1. Locations
        for loc_dict in env_data.get("locations", []):
            loc = Location(
                id=loc_dict["id"],
                name=loc_dict["name"],
                location_type=LocationType(loc_dict["location_type"]),
                coordinates=(loc_dict["coordinates"][0], loc_dict["coordinates"][1]),
                elevation_m=loc_dict.get("elevation_m", 0.0),
                facilities=loc_dict.get("facilities", [])
            )
            state.locations[loc.id] = loc

        # 2. Danger Zones
        for dz_dict in env_data.get("danger_zones", []):
            dz = DangerZone(
                id=dz_dict["id"],
                name=dz_dict["name"],
                zone_type=DangerZoneType(dz_dict["zone_type"]),
                center_coordinates=(dz_dict["center_coordinates"][0], dz_dict["center_coordinates"][1]),
                radius_km=dz_dict["radius_km"],
                severity=DangerSeverity(dz_dict.get("severity", "MODERATE")),
                passable_by_air_only=dz_dict.get("passable_by_air_only", False)
            )
            state.danger_zones[dz.id] = dz

        # 3. Routes
        for r_dict in env_data.get("routes", []):
            route = Route(
                id=r_dict["id"],
                name=r_dict["name"],
                origin_id=r_dict["origin_id"],
                destination_id=r_dict["destination_id"],
                waypoints=[(w[0], w[1]) for w in r_dict["waypoints"]],
                distance_km=r_dict["distance_km"],
                terrain_difficulty=r_dict.get("terrain_difficulty", 1.0)
            )
            state.routes[route.id] = route

        # 4. Vehicles
        for v_dict in self.base_data.get("vehicles", []):
            caps = {VehicleCapability(c) for c in v_dict.get("capabilities", [])}
            veh = Vehicle(
                id=v_dict["id"],
                name=v_dict["name"],
                vehicle_type=VehicleType(v_dict["vehicle_type"]),
                position=(v_dict["position"][0], v_dict["position"][1]),
                speed_kmh=v_dict.get("speed_kmh", 0.0),
                heading_deg=v_dict.get("heading_deg", 0.0),
                fuel_level_l=v_dict.get("fuel_level_l", 200.0),
                fuel_capacity_l=v_dict.get("fuel_capacity_l", 200.0),
                fuel_burn_rate_l_per_km=v_dict.get("fuel_burn_rate_l_per_km", 0.8),
                battery_level_pct=v_dict.get("battery_level_pct", 100.0),
                engine_temp_c=v_dict.get("engine_temp_c", 20.0),
                status=VehicleStatus(v_dict.get("status", "AVAILABLE")),
                capabilities=caps,
                max_range_km=v_dict.get("max_range_km", 250.0),
                passenger_capacity=v_dict.get("passenger_capacity", 4),
                connectivity=ConnectivityStatus(v_dict.get("connectivity", "ONLINE"))
            )
            state.vehicles[veh.id] = veh

        # 5. Personnel
        for p_dict in self.base_data.get("personnel", []):
            p = Personnel(
                id=p_dict["id"],
                name=p_dict["name"],
                role=PersonnelRole(p_dict["role"]),
                assigned_location_id=p_dict["assigned_location_id"],
                current_position=(p_dict["current_position"][0], p_dict["current_position"][1]),
                movement_status=MovementStatus(p_dict.get("movement_status", "STATIONARY")),
                status=PersonnelStatus(p_dict.get("status", "ACTIVE_NORMAL"))
            )
            state.personnel[p.id] = p

        # 6. Inventory
        for inv_dict in self.base_data.get("inventory", []):
            cat = InventoryCategory(inv_dict["category"])
            loc_id = inv_dict["location_id"]
            inv = InventoryItem(
                category=cat,
                location_id=loc_id,
                current_stock=inv_dict["current_stock"],
                unit=inv_dict["unit"],
                daily_consumption_rate=inv_dict["daily_consumption_rate"],
                safety_buffer_days=inv_dict.get("safety_buffer_days", 15.0),
                next_resupply_window_days=inv_dict.get("next_resupply_window_days", 14.0)
            )
            state.inventory[f"{loc_id}_{cat.value}"] = inv

        # 7. Cargo
        for c_dict in self.base_data.get("cargo", []):
            cargo = CargoItem(
                id=c_dict["id"],
                name=c_dict["name"],
                category=CargoCategory(c_dict["category"]),
                weight_kg=c_dict["weight_kg"],
                origin_id=c_dict["origin_id"],
                destination_id=c_dict["destination_id"],
                carrier_vehicle_id=c_dict.get("carrier_vehicle_id"),
                lifecycle_stage=CargoLifecycleStage(c_dict.get("lifecycle_stage", "PACKED")),
                is_temperature_sensitive=c_dict.get("is_temperature_sensitive", False),
                min_temp_c=c_dict.get("min_temp_c", -30.0),
                max_temp_c=c_dict.get("max_temp_c", -10.0),
                current_temp_c=c_dict.get("current_temp_c", -20.0),
                condition=CargoCondition(c_dict.get("condition", "NOMINAL"))
            )
            state.cargo[cargo.id] = cargo

    def run(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Execute full scenario duration and return results.
        """
        duration_ticks = self.scenario_data.get("duration_ticks", 60)
        events_schedule = self.scenario_data.get("events", [])

        if verbose:
            print("=" * 70)
            print(f"POLARSYNC SIMULATION ENGINE: {self.scenario_data.get('title')}")
            print(f"{self.scenario_data.get('description')}")
            print(f"Duration: {duration_ticks} ticks | Seed: {self.scenario_data.get('random_seed', 42)}")
            print("=" * 70)

        for tick in range(1, duration_ticks + 1):
            # Check for scheduled scenario injection events
            self._process_scheduled_events(tick, events_schedule, verbose)

            # Advance simulation step
            frame = self.engine.step()

            # Optional per-interval verbosity
            if verbose and (tick == 1 or tick % 15 == 0 or tick == duration_ticks):
                print(f"\n[SIM TIME: {frame.sim_time_formatted} | Tick {tick:02d}] Ambient Temp: {frame.ambient_temp_c:.1f} C | Wind: {frame.wind_speed_kmh:.1f} km/h | Readiness: {frame.readiness_status} | Online: {frame.connectivity_online}")

        # Final Summary
        final_readiness = ExpeditionReadinessCalculator.calculate(self.engine.state)
        if verbose:
            print("\n" + final_readiness.formatted_text())

        return {
            "scenario_id": self.scenario_data.get("scenario_id"),
            "total_ticks": duration_ticks,
            "final_readiness": final_readiness,
            "alerts": self.engine.state.alerts,
            "telemetry_frames": self.engine.state.telemetry_history,
            "muster_reports": self.muster_reports,
            "sar_results": self.sar_results
        }

    def _process_scheduled_events(self, tick: int, events_schedule: List[Dict[str, Any]], verbose: bool):
        for ev in events_schedule:
            if ev.get("tick") == tick:
                ev_type = ev.get("type")
                if verbose:
                    print(f"\n>>> [SCENARIO EVENT AT TICK {tick}] {ev_type}")

                if ev_type == "DISPATCH_SUPPLY_CONVOY" or ev_type == "DISPATCH_PATROL":
                    v_id = ev["vehicle_id"]
                    r_id = ev["route_id"]
                    assigned_p_ids = ev.get("assigned_personnel_ids", [])
                    if v_id in self.engine.state.vehicles:
                        v = self.engine.state.vehicles[v_id]
                        v.status = VehicleStatus.IN_TRANSIT
                        v.current_route_id = r_id
                        v.route_progress_pct = 0.0
                        for pid in assigned_p_ids:
                            if pid in self.engine.state.personnel:
                                p = self.engine.state.personnel[pid]
                                p.assigned_vehicle_id = v.id
                                p.movement_status = MovementStatus.IN_VEHICLE
                        if verbose:
                            p_info = f" with personnel {', '.join(assigned_p_ids)}" if assigned_p_ids else ""
                            print(f"    Dispatched vehicle {v.name} ({v.id}) on route {r_id}{p_info}")

                elif ev_type == "FUEL_CONSUMPTION_SPIKE":
                    loc_id = ev["location_id"]
                    new_rate = ev["new_daily_rate"]
                    key = f"{loc_id}_FUEL"
                    if key in self.engine.state.inventory:
                        self.engine.state.inventory[key].daily_consumption_rate = new_rate
                        if verbose:
                            print(f"    Daily Fuel burn rate increased to {new_rate} L/day! ({ev.get('reason')})")

                elif ev_type == "FUEL_LEAK_EVENT":
                    loc_id = ev["location_id"]
                    loss = ev["loss_liters"]
                    key = f"{loc_id}_FUEL"
                    if key in self.engine.state.inventory:
                        self.engine.state.inventory[key].current_stock = max(0.0, self.engine.state.inventory[key].current_stock - loss)
                        if verbose:
                            print(f"    Fuel Loss Event: Deducted {loss} L. Current Stock: {self.engine.state.inventory[key].current_stock:.0f} L ({ev.get('reason')})")

                elif ev_type == "CARGO_COOLER_FAILURE":
                    c_id = ev["cargo_id"]
                    if c_id in self.engine.state.cargo:
                        cargo = self.engine.state.cargo[c_id]
                        cargo.cooling_active = False
                        cargo.insulation_factor = 0.05  # Severe insulation leak -> rapid freezing breach
                        if verbose:
                            print(f"    Cooling system failed on {cargo.name} ({cargo.id})! ({ev.get('reason')})")

                elif ev_type == "TRIGGER_EMERGENCY":
                    emg_dict = ev["emergency"]
                    req_caps = [VehicleCapability(c) for c in emg_dict.get("required_capabilities", [])]
                    incident = EmergencyIncident(
                        id=emg_dict["id"],
                        incident_type=emg_dict["incident_type"],
                        location=(emg_dict["location"][0], emg_dict["location"][1]),
                        nearest_landmark=emg_dict["nearest_landmark"],
                        severity=EmergencySeverity(emg_dict.get("severity", "CRITICAL")),
                        affected_personnel_ids=emg_dict.get("affected_personnel_ids", []),
                        timestamp_tick=tick,
                        required_capabilities=req_caps
                    )
                    
                    # Mark affected personnel as unconfirmed
                    for p_id in incident.affected_personnel_ids:
                        if p_id in self.engine.state.personnel:
                            self.engine.state.personnel[p_id].status = PersonnelStatus.AFFECTED_EMERGENCY
                            self.engine.state.personnel[p_id].heartbeat_active = False

                    muster_report, sar_result, dispatch_log = self.engine.trigger_emergency(incident, current_tick=tick)
                    self.muster_reports.append(muster_report)
                    self.sar_results.append(sar_result)
                    if verbose:
                        print(muster_report.summary_text())
                        print(sar_result.formatted_explanation())
                        if dispatch_log:
                            print(dispatch_log)

                elif ev_type == "NETWORK_SEVERED":
                    sync_logs = self.engine.set_network_status(ConnectivityStatus.OFFLINE, current_tick=tick)
                    if verbose:
                        for log in sync_logs:
                            print(f"    {log}")

                elif ev_type == "NETWORK_RESTORED":
                    sync_logs = self.engine.set_network_status(ConnectivityStatus.ONLINE, current_tick=tick)
                    if verbose:
                        for log in sync_logs:
                            print(f"    {log}")

    def export_telemetry_dataframe(self) -> pd.DataFrame:
        """
        Convert telemetry history into a flat pandas DataFrame for analysis/export.
        """
        rows = []
        for frame in self.engine.state.telemetry_history:
            for v in frame.vehicles:
                rows.append({
                    "tick": frame.tick,
                    "sim_time": frame.sim_time_formatted,
                    "ambient_temp_c": frame.ambient_temp_c,
                    "wind_speed_kmh": frame.wind_speed_kmh,
                    "readiness": frame.readiness_status,
                    "network_online": frame.connectivity_online,
                    "vehicle_id": v.vehicle_id,
                    "lat": v.gps_lat,
                    "lon": v.gps_lon,
                    "speed_kmh": v.speed_kmh,
                    "heading_deg": v.heading_deg,
                    "fuel_pct": v.fuel_pct,
                    "battery_pct": v.battery_pct,
                    "engine_temp_c": v.engine_temp_c,
                    "vehicle_status": v.status
                })
        return pd.DataFrame(rows)
