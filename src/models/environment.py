from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional


class LocationType(str, Enum):
    RESEARCH_BASE = "RESEARCH_BASE"
    EXPEDITION_CAMP = "EXPEDITION_CAMP"
    FIELD_CAMP = "FIELD_CAMP"
    EMERGENCY_STATION = "EMERGENCY_STATION"


class DangerZoneType(str, Enum):
    CREVASSE_FIELD = "CREVASSE_FIELD"
    BLIZZARD_CORRIDOR = "BLIZZARD_CORRIDOR"
    ICE_SHELF_RIFT = "ICE_SHELF_RIFT"
    WHITEOUT_PASS = "WHITEOUT_PASS"


class DangerSeverity(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    EXTREME = "EXTREME"


@dataclass
class Location:
    id: str
    name: str
    location_type: LocationType
    coordinates: Tuple[float, float]  # (latitude, longitude)
    elevation_m: float = 0.0
    facilities: List[str] = field(default_factory=list)


@dataclass
class DangerZone:
    id: str
    name: str
    zone_type: DangerZoneType
    center_coordinates: Tuple[float, float]
    radius_km: float
    severity: DangerSeverity = DangerSeverity.MODERATE
    passable_by_air_only: bool = False


@dataclass
class Route:
    id: str
    name: str
    origin_id: str
    destination_id: str
    waypoints: List[Tuple[float, float]]  # Sequence of (lat, lon)
    distance_km: float
    terrain_difficulty: float = 1.0  # Multiplier for speed / fuel drag


@dataclass
class WeatherState:
    ambient_temp_c: float = -25.0
    wind_speed_kmh: float = 15.0
    visibility_km: float = 10.0
    storm_active: bool = False
    condition_summary: str = "Clear Polar Conditions"
