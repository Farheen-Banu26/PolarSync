"""
GIS Map Topology Schemas
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from app.schemas.assets import AssetModel
from app.schemas.personnel import PersonnelModel
from app.schemas.emergency import EmergencyIncidentModel


class MapLocationModel(BaseModel):
    id: str
    name: str
    type: str
    latitude: float
    longitude: float
    elevation_m: float
    facilities: List[str]


class DangerZoneModel(BaseModel):
    id: str
    name: str
    type: str
    center_lat: float
    center_lon: float
    radius_km: float
    severity: str
    passable_by_air_only: bool


class RouteModel(BaseModel):
    id: str
    name: str
    origin_id: str
    destination_id: str
    waypoints: List[List[float]]
    distance_km: float


class MapTopologyResponse(BaseModel):
    scenario_id: int
    locations: List[MapLocationModel]
    danger_zones: List[DangerZoneModel]
    routes: List[RouteModel]
    assets: List[AssetModel]
    personnel: List[PersonnelModel] = []
    emergency: Optional[EmergencyIncidentModel] = None
