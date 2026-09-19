from __future__ import annotations
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .clock import SimulationClock
from .events import EventBus, Event, EventType
from .state import WorldState
from ..models.telemetry import TelemetryFrame, VehicleTelemetry, CargoTelemetry
from ..models.alert import Alert, AlertCategory, AlertSeverity
from ..models.vehicle import ConnectivityStatus, VehicleStatus
from ..models.emergency import EmergencyIncident, EmergencyStatus
from ..models.personnel import PersonnelStatus
from ..subsystems.environment_sim import EnvironmentSubsystem
from ..subsystems.movement_sim import MovementSubsystem
from ..subsystems.personnel_sim import PersonnelSubsystem
from ..subsystems.cargo_sim import CargoSubsystem
from ..subsystems.inventory_sim import InventorySubsystem
from ..subsystems.connectivity_sim import ConnectivitySubsystem
from ..decision_support.muster_manager import MusterManager, MusterReport
from ..decision_support.sar_selector import SARAssetSelector, SARSelectionResult
from ..decision_support.route_planner import RoutePlanner
from ..decision_support.readiness import ExpeditionReadinessCalculator, ReadinessReport
from ..alerts.alert_engine import AlertEngine


class SimulationEngine:
    def __init__(self, seed: int = 42, minutes_per_tick: int = 1):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.clock = SimulationClock(minutes_per_tick=minutes_per_tick)
        self.event_bus = EventBus()
        self.state = WorldState()

        # Initialize Subsystems
        self.env_subsystem = EnvironmentSubsystem(self.rng)
        self.movement_subsystem = MovementSubsystem(self.rng)
        self.personnel_subsystem = PersonnelSubsystem()
        self.cargo_subsystem = CargoSubsystem(self.rng)
        self.inventory_subsystem = InventorySubsystem()
        self.connectivity_subsystem = ConnectivitySubsystem(self.event_bus)

        # Decision & Alert Engines
        self.alert_engine = AlertEngine()

    def set_network_status(self, new_status: ConnectivityStatus, current_tick: Optional[int] = None) -> List[str]:
        """
        Manually toggle network status (ONLINE / OFFLINE) and handle queue reconciliation.
        """
        old_status = self.state.network_status
        tick_to_use = current_tick if current_tick is not None else self.clock.current_tick
        new_status, self.state.local_event_queue, sync_logs = self.connectivity_subsystem.set_connectivity(
            current_status=old_status,
            new_status=new_status,
            current_tick=tick_to_use,
            local_queue=self.state.local_event_queue
        )
        self.state.network_status = new_status
        
        # Update vehicles connectivity to match base station uplink
        for v in self.state.vehicles.values():
            v.connectivity = new_status

        # If reconnected, generate a synchronization alert
        if old_status == ConnectivityStatus.OFFLINE and new_status == ConnectivityStatus.ONLINE:
            self.state.add_alert(Alert(
                id=f"ALT-SYNC-{tick_to_use}",
                tick=tick_to_use,
                category=AlertCategory.CONNECTIVITY,
                severity=AlertSeverity.INFO,
                title="NETWORK RESTORED & SYNCHRONIZED",
                message="Connectivity restored. Local telemetry and event queues synchronized with central expedition registry.",
                source_entity_id="BASE-SAT-UPLINK"
            ))
        elif old_status == ConnectivityStatus.ONLINE and new_status == ConnectivityStatus.OFFLINE:
            self.state.add_alert(Alert(
                id=f"ALT-NET-LOST-{tick_to_use}",
                tick=tick_to_use,
                category=AlertCategory.CONNECTIVITY,
                severity=AlertSeverity.WARNING,
                title="NETWORK UPLINK SEVERED",
                message="Satellite connection lost. Switching local assets to store-and-forward offline buffer.",
                source_entity_id="BASE-SAT-UPLINK"
            ))

        return sync_logs

    def trigger_emergency(self, emergency: EmergencyIncident, current_tick: Optional[int] = None) -> Tuple[MusterReport, SARSelectionResult, Optional[str]]:
        """
        Full Emergency Workflow:
        EMERGENCY DETECTED -> LOCATION IDENTIFIED -> PERSONNEL IDENTIFIED ->
        AUTOMATIC MUSTER -> AVAILABLE ASSETS CHECKED -> RESOURCE SUITABILITY ->
        RESPONSE ASSET SELECTED -> ROUTE GENERATED -> DISPATCHED
        """
        self.state.emergencies[emergency.id] = emergency
        tick_to_use = current_tick if current_tick is not None else self.clock.current_tick
        emergency.timestamp_tick = tick_to_use
        emergency.status = EmergencyStatus.DETECTED

        # 1. Automatic Muster Roll-Call
        muster_report = MusterManager.perform_muster(
            self.state.personnel,
            emergency_affected_ids=emergency.affected_personnel_ids
        )
        emergency.status = EmergencyStatus.MUSTER_COMPLETED

        # 2. Evaluate available assets and select optimal SAR response asset
        sar_result = SARAssetSelector.evaluate_and_select(emergency, self.state.vehicles)
        emergency.status = EmergencyStatus.ASSET_EVALUATED
        emergency.selection_rationale = [e.decision_summary for e in [sar_result]]

        dispatch_log = None
        if sar_result.selected_vehicle_id:
            assigned_veh = self.state.vehicles[sar_result.selected_vehicle_id]
            emergency.assigned_asset_id = assigned_veh.id
            emergency.status = EmergencyStatus.DISPATCHED
            emergency.dispatched_tick = current_tick

            # 3. Route Generation
            is_aerial = (assigned_veh.vehicle_type.value == "HELICOPTER")
            sar_route = RoutePlanner.generate_emergency_route(
                origin_coords=assigned_veh.position,
                destination_coords=emergency.location,
                danger_zones=self.state.danger_zones,
                is_aerial=is_aerial
            )
            self.state.routes[sar_route.id] = sar_route

            # 4. Dispatch Asset
            assigned_veh.status = VehicleStatus.DISPATCHED_EMERGENCY
            assigned_veh.current_route_id = sar_route.id
            assigned_veh.route_progress_pct = 0.0
            assigned_veh.active_emergency_id = emergency.id

            dispatch_log = (
                f"[TICK {tick_to_use}] DISPATCHED {assigned_veh.name} ({assigned_veh.id}) to {emergency.nearest_landmark} "
                f"via route {sar_route.id} ({sar_route.distance_km:.1f} km)."
            )

            # Publish Event & Alert
            self.event_bus.publish(Event(
                event_type=EventType.VEHICLE_DISPATCHED,
                tick=tick_to_use,
                payload={"vehicle_id": assigned_veh.id, "emergency_id": emergency.id}
            ))
            self.state.add_alert(Alert(
                id=f"ALT-DISPATCH-{emergency.id}",
                tick=tick_to_use,
                category=AlertCategory.EMERGENCY,
                severity=AlertSeverity.CRITICAL,
                title=f"SAR ASSET DISPATCHED: {assigned_veh.name}",
                message=f"{assigned_veh.name} dispatched to {emergency.nearest_landmark} for emergency response {emergency.id}.",
                source_entity_id=assigned_veh.id
            ))

        return muster_report, sar_result, dispatch_log

    def step(self) -> TelemetryFrame:
        """
        Execute a single simulation timestep.
        """
        current_tick = self.clock.tick()
        delta_hours = self.clock.delta_hours
        delta_days = self.clock.delta_days

        # 1. Environment simulation
        self.env_subsystem.step(self.state.weather, delta_hours)

        # 2. Vehicle kinematics & fuel/battery decay
        self.movement_subsystem.step(
            self.state.vehicles,
            self.state.routes,
            self.state.weather,
            delta_hours
        )

        # 3. Personnel movements & check-ins
        self.personnel_subsystem.step(
            self.state.personnel,
            self.state.vehicles,
            current_tick
        )

        # 4. Cargo thermal state & position updates
        self.cargo_subsystem.step(
            self.state.cargo,
            self.state.vehicles,
            self.state.weather,
            delta_hours
        )

        # 5. Inventory consumption
        self.inventory_subsystem.step(
            self.state.inventory,
            delta_days
        )

        # 6. Check active emergencies lifecycle (DISPATCHED -> ON_SCENE -> RESOLVED)
        for emg in self.state.emergencies.values():
            if emg.status in (EmergencyStatus.DISPATCHED, EmergencyStatus.EN_ROUTE):
                if emg.assigned_asset_id and emg.assigned_asset_id in self.state.vehicles:
                    veh = self.state.vehicles[emg.assigned_asset_id]
                    if veh.route_progress_pct >= 100.0:
                        emg.status = EmergencyStatus.ON_SCENE
                        emg.on_scene_tick = current_tick
                        self.state.add_alert(Alert(
                            id=f"ALT-ONSCENE-{emg.id}",
                            tick=current_tick,
                            category=AlertCategory.EMERGENCY,
                            severity=AlertSeverity.INFO,
                            title=f"SAR ASSET ON SCENE: {veh.name}",
                            message=f"{veh.name} reached emergency site at {emg.nearest_landmark}. Medical triage and field stabilization in progress.",
                            source_entity_id=veh.id
                        ))
            elif emg.status == EmergencyStatus.ON_SCENE:
                if emg.on_scene_tick is not None and (current_tick - emg.on_scene_tick) >= emg.triage_duration_ticks:
                    emg.status = EmergencyStatus.RESOLVED
                    emg.resolution_tick = current_tick
                    
                    # Update affected personnel status to EVACUATED / recovered
                    for pid in emg.affected_personnel_ids:
                        if pid in self.state.personnel:
                            p = self.state.personnel[pid]
                            p.status = PersonnelStatus.EVACUATED
                            p.heartbeat_active = True
                            p.last_checkin_tick = current_tick
                    
                    # Release response asset
                    if emg.assigned_asset_id and emg.assigned_asset_id in self.state.vehicles:
                        veh = self.state.vehicles[emg.assigned_asset_id]
                        veh.status = VehicleStatus.AVAILABLE
                        veh.active_emergency_id = None
                        veh.current_route_id = None
                    
                    self.state.add_alert(Alert(
                        id=f"ALT-RESOLVED-{emg.id}",
                        tick=current_tick,
                        category=AlertCategory.EMERGENCY,
                        severity=AlertSeverity.INFO,
                        title=f"EMERGENCY RESOLVED: {emg.incident_type}",
                        message=f"Casualties stabilized and evacuated from {emg.nearest_landmark}. Incident {emg.id} successfully resolved.",
                        source_entity_id=emg.id
                    ))

        # 7. Rule evaluation & Alert generation
        new_alerts = self.alert_engine.evaluate_state(self.state, current_tick)

        # 8. Expedition Readiness Assessment
        readiness_report = ExpeditionReadinessCalculator.calculate(self.state)
        self.state.readiness_status = readiness_report.overall_status
        self.state.readiness_summary = readiness_report.summary_dict

        # 9. Synthesize Telemetry Frame
        vehicle_telemetries = [
            VehicleTelemetry(
                vehicle_id=v.id,
                timestamp_tick=current_tick,
                gps_lat=v.position[0],
                gps_lon=v.position[1],
                speed_kmh=v.speed_kmh,
                heading_deg=v.heading_deg,
                fuel_level_l=v.fuel_level_l,
                fuel_pct=v.fuel_pct,
                battery_pct=v.battery_level_pct,
                engine_temp_c=v.engine_temp_c,
                status=v.status.value,
                connectivity=v.connectivity.value
            )
            for v in self.state.vehicles.values()
        ]

        cargo_telemetries = [
            CargoTelemetry(
                cargo_id=c.id,
                timestamp_tick=current_tick,
                stage=c.lifecycle_stage.value,
                temperature_c=c.current_temp_c,
                condition=c.condition.value,
                location_lat=c.current_coordinates[0],
                location_lon=c.current_coordinates[1]
            )
            for c in self.state.cargo.values()
        ]

        frame = TelemetryFrame(
            tick=current_tick,
            sim_time_minutes=self.clock.total_elapsed_minutes,
            sim_time_formatted=self.clock.formatted_sim_time,
            ambient_temp_c=self.state.weather.ambient_temp_c,
            wind_speed_kmh=self.state.weather.wind_speed_kmh,
            vehicles=vehicle_telemetries,
            cargo=cargo_telemetries,
            active_alerts_count=len(self.state.alerts),
            readiness_status=self.state.readiness_status,
            connectivity_online=(self.state.network_status == ConnectivityStatus.ONLINE)
        )

        # Store telemetry in history
        self.state.telemetry_history.append(frame)

        # 9. Offline buffering if offline
        if self.state.network_status == ConnectivityStatus.OFFLINE:
            self.connectivity_subsystem.buffer_event(
                self.state.local_event_queue,
                {
                    "tick": current_tick,
                    "sim_time": frame.sim_time_formatted,
                    "active_vehicles": len(vehicle_telemetries),
                    "alerts_generated": [a.id for a in new_alerts]
                }
            )

        # Publish tick completion
        self.event_bus.publish(Event(
            event_type=EventType.TICK_COMPLETED,
            tick=current_tick,
            payload={"frame": frame}
        ))

        return frame
