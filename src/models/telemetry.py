from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class VehicleTelemetry:
    vehicle_id: str
    timestamp_tick: int
    gps_lat: float
    gps_lon: float
    speed_kmh: float
    heading_deg: float
    fuel_level_l: float
    fuel_pct: float
    battery_pct: float
    engine_temp_c: float
    status: str
    connectivity: str


@dataclass
class CargoTelemetry:
    cargo_id: str
    timestamp_tick: int
    stage: str
    temperature_c: float
    condition: str
    location_lat: float
    location_lon: float


@dataclass
class TelemetryFrame:
    tick: int
    sim_time_minutes: int
    sim_time_formatted: str
    ambient_temp_c: float
    wind_speed_kmh: float
    vehicles: List[VehicleTelemetry] = field(default_factory=list)
    cargo: List[CargoTelemetry] = field(default_factory=list)
    active_alerts_count: int = 0
    readiness_status: str = "NOMINAL"
    connectivity_online: bool = True
