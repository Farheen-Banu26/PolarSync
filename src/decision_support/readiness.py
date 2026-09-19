from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, TYPE_CHECKING
from ..models.personnel import PersonnelStatus
from ..models.cargo import CargoCondition
from ..models.inventory import InventoryCategory, ResupplyRisk
from ..models.vehicle import VehicleStatus, VehicleCapability

if TYPE_CHECKING:
    from ..core.state import WorldState


@dataclass
class ReadinessReport:
    personnel_ratio_str: str
    cargo_nominal_pct: float
    fuel_autonomy_days: float
    medical_stock_pct: float
    vehicles_ratio_str: str
    emergency_capability_status: str
    overall_status: str  # NOMINAL, CONDITIONAL, DEGRADED, CRITICAL
    summary_dict: Dict[str, str] = field(default_factory=dict)

    def formatted_text(self) -> str:
        return (
            f"========================================\n"
            f"EXPEDITION READINESS\n"
            f"----------------------------------------\n"
            f"Personnel : {self.personnel_ratio_str}\n"
            f"Cargo     : {self.cargo_nominal_pct:.0f}%\n"
            f"Fuel      : {self.fuel_autonomy_days:.0f} days\n"
            f"Medical   : {self.medical_stock_pct:.0f}%\n"
            f"Vehicles  : {self.vehicles_ratio_str}\n"
            f"Emergency : {self.emergency_capability_status}\n"
            f"----------------------------------------\n"
            f"STATUS    : {self.overall_status}\n"
            f"========================================"
        )


class ExpeditionReadinessCalculator:
    @staticmethod
    def calculate(state: WorldState) -> ReadinessReport:
        # 1. Personnel readiness
        total_p = len(state.personnel)
        active_p = sum(
            1 for p in state.personnel.values()
            if p.status not in (PersonnelStatus.UNCONFIRMED_DUE, PersonnelStatus.AFFECTED_EMERGENCY)
        )
        p_str = f"{active_p}/{total_p}" if total_p > 0 else "N/A"
        p_score = (active_p / total_p) if total_p > 0 else 1.0

        # 2. Cargo readiness (% of items not breached)
        total_c = len(state.cargo)
        nominal_c = sum(1 for c in state.cargo.values() if c.condition != CargoCondition.BREACHED_DAMAGED)
        cargo_pct = (nominal_c / total_c) * 100.0 if total_c > 0 else 100.0

        # 3. Fuel autonomy (minimum days across all locations)
        fuel_items = [
            item for item in state.inventory.values()
            if item.category == InventoryCategory.FUEL
        ]
        min_fuel_days = min((item.days_of_autonomy for item in fuel_items), default=999.0)

        # 4. Medical supplies stock ratio
        med_items = [
            item for item in state.inventory.values()
            if item.category == InventoryCategory.MEDICAL_SUPPLIES
        ]
        med_pct = 100.0
        if med_items:
            # Ratio of current to expected safety buffer equivalent
            item = med_items[0]
            target_stock = item.daily_consumption_rate * (item.safety_buffer_days + item.next_resupply_window_days)
            if target_stock > 0:
                med_pct = min(100.0, (item.current_stock / target_stock) * 100.0)

        # 5. Vehicle availability
        total_v = len(state.vehicles)
        available_v = sum(1 for v in state.vehicles.values() if v.status == VehicleStatus.AVAILABLE)
        v_str = f"{available_v}/{total_v}" if total_v > 0 else "N/A"
        v_ratio = (available_v / total_v) if total_v > 0 else 1.0

        # 6. Emergency capability
        has_medical_asset = any(
            v.has_capability(VehicleCapability.MEDICAL_TRANSPORT) and v.status == VehicleStatus.AVAILABLE
            for v in state.vehicles.values()
        )
        has_aerial_asset = any(
            v.has_capability(VehicleCapability.AERIAL) and v.status == VehicleStatus.AVAILABLE
            for v in state.vehicles.values()
        )
        if has_medical_asset and has_aerial_asset:
            emg_status = "READY"
        elif has_medical_asset or has_aerial_asset:
            emg_status = "LIMITED"
        else:
            emg_status = "DEGRADED"

        # Overall synthesis
        if (
            p_score == 1.0 and
            cargo_pct >= 95.0 and
            min_fuel_days > 20.0 and
            med_pct >= 85.0 and
            v_ratio >= 0.75 and
            emg_status == "READY"
        ):
            overall = "NOMINAL"
        elif (
            p_score >= 0.85 and
            cargo_pct >= 75.0 and
            min_fuel_days >= 10.0 and
            med_pct >= 60.0 and
            emg_status in ("READY", "LIMITED")
        ):
            overall = "CONDITIONAL"
        elif min_fuel_days < 5.0 or p_score < 0.70 or emg_status == "DEGRADED":
            overall = "CRITICAL"
        else:
            overall = "DEGRADED"

        summary = {
            "Personnel": p_str,
            "Cargo": f"{cargo_pct:.0f}%",
            "Fuel": f"{min_fuel_days:.0f} days",
            "Medical": f"{med_pct:.0f}%",
            "Vehicles": v_str,
            "Emergency": emg_status,
            "Status": overall
        }

        return ReadinessReport(
            personnel_ratio_str=p_str,
            cargo_nominal_pct=round(cargo_pct, 1),
            fuel_autonomy_days=round(min_fuel_days, 1),
            medical_stock_pct=round(med_pct, 1),
            vehicles_ratio_str=v_str,
            emergency_capability_status=emg_status,
            overall_status=overall,
            summary_dict=summary
        )
