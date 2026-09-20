"""
Asset Schemas
"""
from typing import List, Optional
from pydantic import BaseModel


class AssetModel(BaseModel):
    id: str
    name: str
    type: str
    latitude: float
    longitude: float
    heading: float
    speed_kmh: float
    fuel_pct: float
    fuel_liters: float
    battery_pct: float
    status: str
    capabilities: List[str]
    connectivity: str
    route_id: Optional[str] = None
    route_progress_pct: float = 0.0


class AssetListResponse(BaseModel):
    scenario_id: int
    assets: List[AssetModel]
