from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Optional
from .vehicle import VehicleCapability


class EmergencySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmergencyStatus(str, Enum):
    DETECTED = "DETECTED"
    MUSTER_COMPLETED = "MUSTER_COMPLETED"
    ASSET_EVALUATED = "ASSET_EVALUATED"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    RESOLVED = "RESOLVED"


@dataclass
class EmergencyIncident:
    id: str
    incident_type: str
    location: Tuple[float, float]
    nearest_landmark: str
    severity: EmergencySeverity
    affected_personnel_ids: List[str]
    timestamp_tick: int
    required_capabilities: List[VehicleCapability] = field(default_factory=list)
    status: EmergencyStatus = EmergencyStatus.DETECTED
    assigned_asset_id: Optional[str] = None
    selection_rationale: List[str] = field(default_factory=list)
    dispatched_tick: Optional[int] = None
    on_scene_tick: Optional[int] = None
    triage_duration_ticks: int = 8
    resolution_tick: Optional[int] = None

    @property
    def affected_count(self) -> int:
        return len(self.affected_personnel_ids)
