from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, List, Set, Optional


class VehicleType(str, Enum):
    SNOWCAT = "SNOWCAT"
    SKIDOO = "SKIDOO"
    PISTON_BULLY = "PISTON_BULLY"
    HELICOPTER = "HELICOPTER"


class VehicleStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    IN_TRANSIT = "IN_TRANSIT"
    DISPATCHED_EMERGENCY = "DISPATCHED_EMERGENCY"
    MAINTENANCE = "MAINTENANCE"
    OFFLINE = "OFFLINE"


class ConnectivityStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class VehicleCapability(str, Enum):
    MEDICAL_TRANSPORT = "MEDICAL_TRANSPORT"
    HEAVY_CARGO = "HEAVY_CARGO"
    ALL_TERRAIN = "ALL_TERRAIN"
    RAPID_RESPONSE = "RAPID_RESPONSE"
    AERIAL = "AERIAL"
    LONG_RANGE = "LONG_RANGE"


@dataclass
class Vehicle:
    id: str
    name: str
    vehicle_type: VehicleType
    position: Tuple[float, float]  # (lat, lon)
    speed_kmh: float = 0.0
    heading_deg: float = 0.0
    fuel_level_l: float = 200.0
    fuel_capacity_l: float = 200.0
    fuel_burn_rate_l_per_km: float = 0.8
    battery_level_pct: float = 100.0
    engine_temp_c: float = 65.0
    status: VehicleStatus = VehicleStatus.AVAILABLE
    capabilities: Set[VehicleCapability] = field(default_factory=set)
    max_range_km: float = 250.0
    passenger_capacity: int = 4
    connectivity: ConnectivityStatus = ConnectivityStatus.ONLINE
    current_route_id: Optional[str] = None
    target_destination_id: Optional[str] = None
    route_progress_pct: float = 0.0
    active_emergency_id: Optional[str] = None

    @property
    def fuel_pct(self) -> float:
        if self.fuel_capacity_l <= 0:
            return 0.0
        return max(0.0, min(100.0, (self.fuel_level_l / self.fuel_capacity_l) * 100.0))

    def has_capability(self, capability: VehicleCapability) -> bool:
        return capability in self.capabilities

    def can_cover_distance(self, distance_km: float, safety_margin: float = 1.25) -> bool:
        required_fuel = distance_km * self.fuel_burn_rate_l_per_km * safety_margin
        return self.fuel_level_l >= required_fuel
