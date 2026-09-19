import uuid
from typing import List, Set
from ..core.state import WorldState
from ..models.alert import Alert, AlertCategory, AlertSeverity
from ..models.inventory import ResupplyRisk, InventoryCategory
from ..models.cargo import CargoCondition
from ..models.personnel import PersonnelStatus
from ..models.emergency import EmergencyStatus


class AlertEngine:
    def __init__(self):
        # Keep track of active deduplication keys to avoid flooding same alert every tick
        self._active_alert_keys: Set[str] = set()

    def evaluate_state(self, state: WorldState, current_tick: int) -> List[Alert]:
        new_alerts: List[Alert] = []

        # 1. Inventory & Fuel Resupply Risk
        for key, item in state.inventory.items():
            risk = item.resupply_risk
            alert_key = f"inv_{key}_{risk.value}"
            if risk == ResupplyRisk.CRITICAL and alert_key not in self._active_alert_keys:
                alert = Alert(
                    id=f"ALT-INV-{uuid.uuid4().hex[:6].upper()}",
                    tick=current_tick,
                    category=AlertCategory.INVENTORY,
                    severity=AlertSeverity.CRITICAL,
                    title=f"CRITICAL RESUPPLY RISK: {item.category.value}",
                    message=f"{item.category.value} at {item.location_id} has only {item.days_of_autonomy:.1f} days of autonomy remaining. Resupply window is in {item.next_resupply_window_days:.0f} days!",
                    source_entity_id=key
                )
                new_alerts.append(alert)
                self._active_alert_keys.add(alert_key)
            elif risk == ResupplyRisk.HIGH and alert_key not in self._active_alert_keys:
                alert = Alert(
                    id=f"ALT-INV-{uuid.uuid4().hex[:6].upper()}",
                    tick=current_tick,
                    category=AlertCategory.INVENTORY,
                    severity=AlertSeverity.WARNING,
                    title=f"HIGH RESUPPLY RISK: {item.category.value}",
                    message=f"{item.category.value} at {item.location_id} has {item.days_of_autonomy:.1f} days of autonomy remaining (Safety buffer breached).",
                    source_entity_id=key
                )
                new_alerts.append(alert)
                self._active_alert_keys.add(alert_key)

        # 2. Cargo Temperature Warnings & Breaches
        for cargo in state.cargo.values():
            if cargo.is_temperature_sensitive:
                if cargo.condition == CargoCondition.BREACHED_DAMAGED:
                    if cargo.current_temp_c < cargo.min_temp_c:
                        alert_key = f"cargo_breach_freezing_{cargo.id}"
                        title = f"COLD-CHAIN BREACH (FREEZING RISK): {cargo.name}"
                        msg = f"Cargo {cargo.id} temperature {cargo.current_temp_c:.1f} C dropped below allowable minimum limit {cargo.min_temp_c:.1f} C (Allowed: [{cargo.min_temp_c:.1f} C to {cargo.max_temp_c:.1f} C]). Sub-zero freezing damage risk!"
                    else:
                        alert_key = f"cargo_breach_overheating_{cargo.id}"
                        title = f"COLD-CHAIN BREACH (OVERHEATING RISK): {cargo.name}"
                        msg = f"Cargo {cargo.id} temperature {cargo.current_temp_c:.1f} C exceeded allowable maximum limit {cargo.max_temp_c:.1f} C (Allowed: [{cargo.min_temp_c:.1f} C to {cargo.max_temp_c:.1f} C]). Thawing and sample loss risk!"

                    if alert_key not in self._active_alert_keys:
                        alert = Alert(
                            id=f"ALT-CRG-{uuid.uuid4().hex[:6].upper()}",
                            tick=current_tick,
                            category=AlertCategory.CARGO,
                            severity=AlertSeverity.CRITICAL,
                            title=title,
                            message=msg,
                            source_entity_id=cargo.id
                        )
                        new_alerts.append(alert)
                        self._active_alert_keys.add(alert_key)

                elif cargo.condition == CargoCondition.WARNING_DRIFT:
                    if cargo.current_temp_c < cargo.min_temp_c + 2.0:
                        alert_key = f"cargo_drift_low_{cargo.id}"
                        title = f"TEMPERATURE DRIFT WARNING (FREEZING RISK): {cargo.name}"
                        msg = f"Cargo {cargo.id} temperature drifting lower ({cargo.current_temp_c:.1f} C), approaching minimum limit {cargo.min_temp_c:.1f} C."
                    else:
                        alert_key = f"cargo_drift_high_{cargo.id}"
                        title = f"TEMPERATURE DRIFT WARNING (OVERHEATING RISK): {cargo.name}"
                        msg = f"Cargo {cargo.id} temperature drifting higher ({cargo.current_temp_c:.1f} C), approaching maximum limit {cargo.max_temp_c:.1f} C."

                    if alert_key not in self._active_alert_keys:
                        alert = Alert(
                            id=f"ALT-CRG-{uuid.uuid4().hex[:6].upper()}",
                            tick=current_tick,
                            category=AlertCategory.CARGO,
                            severity=AlertSeverity.WARNING,
                            title=title,
                            message=msg,
                            source_entity_id=cargo.id
                        )
                        new_alerts.append(alert)
                        self._active_alert_keys.add(alert_key)

        # 3. Personnel Unconfirmed
        for p in state.personnel.values():
            if p.status == PersonnelStatus.UNCONFIRMED_DUE:
                alert_key = f"pers_unconfirmed_{p.id}"
                if alert_key not in self._active_alert_keys:
                    alert = Alert(
                        id=f"ALT-PERS-{uuid.uuid4().hex[:6].upper()}",
                        tick=current_tick,
                        category=AlertCategory.PERSONNEL,
                        severity=AlertSeverity.WARNING,
                        title=f"PERSONNEL CHECK-IN OVERDUE: {p.name}",
                        message=f"{p.name} ({p.role.value}) missed periodic check-in. Last confirmed tick: {p.last_checkin_tick} at {p.current_position}.",
                        source_entity_id=p.id
                    )
                    new_alerts.append(alert)
                    self._active_alert_keys.add(alert_key)

        # 4. Emergency Incidents
        for emg in state.emergencies.values():
            alert_key = f"emg_detected_{emg.id}"
            if emg.status == EmergencyStatus.DETECTED and alert_key not in self._active_alert_keys:
                alert = Alert(
                    id=f"ALT-EMG-{uuid.uuid4().hex[:6].upper()}",
                    tick=current_tick,
                    category=AlertCategory.EMERGENCY,
                    severity=AlertSeverity.CRITICAL,
                    title=f"EMERGENCY INCIDENT DETECTED: {emg.incident_type}",
                    message=f"{emg.severity.value} severity incident at {emg.nearest_landmark} affecting {emg.affected_count} personnel. Automatic muster and response asset selection initiated.",
                    source_entity_id=emg.id
                )
                new_alerts.append(alert)
                self._active_alert_keys.add(alert_key)

        # Record generated alerts to world state
        for alert in new_alerts:
            state.add_alert(alert)

        return new_alerts
