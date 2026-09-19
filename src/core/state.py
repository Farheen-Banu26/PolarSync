from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ..models.environment import Location, DangerZone, Route, WeatherState
from ..models.vehicle import Vehicle, ConnectivityStatus
from ..models.personnel import Personnel
from ..models.cargo import CargoItem
from ..models.inventory import InventoryItem, InventoryCategory
from ..models.emergency import EmergencyIncident
from ..models.alert import Alert
from ..models.telemetry import TelemetryFrame


@dataclass
class WorldState:
    locations: Dict[str, Location] = field(default_factory=dict)
    danger_zones: Dict[str, DangerZone] = field(default_factory=dict)
    routes: Dict[str, Route] = field(default_factory=dict)
    vehicles: Dict[str, Vehicle] = field(default_factory=dict)
    personnel: Dict[str, Personnel] = field(default_factory=dict)
    cargo: Dict[str, CargoItem] = field(default_factory=dict)
    inventory: Dict[str, InventoryItem] = field(default_factory=dict)  # Key: f"{location_id}_{category}"
    emergencies: Dict[str, EmergencyIncident] = field(default_factory=dict)
    weather: WeatherState = field(default_factory=WeatherState)
    alerts: List[Alert] = field(default_factory=list)
    telemetry_history: List[TelemetryFrame] = field(default_factory=list)
    
    # Offline Store-and-Forward Queue (for connectivity loss simulation)
    local_event_queue: List[Dict] = field(default_factory=list)
    network_status: ConnectivityStatus = ConnectivityStatus.ONLINE
    
    # Global metrics
    readiness_status: str = "NOMINAL"
    readiness_summary: Dict[str, str] = field(default_factory=dict)

    def get_inventory_for_location(self, location_id: str) -> List[InventoryItem]:
        return [item for item in self.inventory.values() if item.location_id == location_id]

    def get_inventory_item(self, location_id: str, category: InventoryCategory) -> Optional[InventoryItem]:
        return self.inventory.get(f"{location_id}_{category.value}")

    def add_alert(self, alert: Alert):
        self.alerts.append(alert)
