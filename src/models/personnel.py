from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional


class PersonnelRole(str, Enum):
    STATION_COMMANDER = "STATION_COMMANDER"
    EXPEDITION_LEADER = "EXPEDITION_LEADER"
    FIELD_SCIENTIST = "FIELD_SCIENTIST"
    MEDIC = "MEDIC"
    LOGISTICS_OFFICER = "LOGISTICS_OFFICER"
    VEHICLE_OPERATOR = "VEHICLE_OPERATOR"
    MAINTENANCE_ENGINEER = "MAINTENANCE_ENGINEER"


class PersonnelStatus(str, Enum):
    ACTIVE_NORMAL = "ACTIVE_NORMAL"
    CHECKED_IN = "CHECKED_IN"
    UNCONFIRMED_DUE = "UNCONFIRMED_DUE"
    AFFECTED_EMERGENCY = "AFFECTED_EMERGENCY"
    EVACUATED = "EVACUATED"


class MovementStatus(str, Enum):
    STATIONARY = "STATIONARY"
    ON_FOOT_TRANSIT = "ON_FOOT_TRANSIT"
    IN_VEHICLE = "IN_VEHICLE"
    SHELTERED = "SHELTERED"


@dataclass
class Personnel:
    id: str
    name: str
    role: PersonnelRole
    assigned_location_id: str
    current_position: Tuple[float, float]
    movement_status: MovementStatus = MovementStatus.STATIONARY
    status: PersonnelStatus = PersonnelStatus.ACTIVE_NORMAL
    last_checkin_tick: int = 0
    checkin_interval_ticks: int = 30  # expected check-in every 30 simulated minutes
    assigned_vehicle_id: Optional[str] = None
    heartbeat_active: bool = True

    def is_checkin_overdue(self, current_tick: int, tolerance_ticks: int = 15) -> bool:
        return (current_tick - self.last_checkin_tick) > (self.checkin_interval_ticks + tolerance_ticks)
