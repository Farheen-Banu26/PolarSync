"""
Cargo Schemas
"""
from typing import List, Optional
from pydantic import BaseModel


class CargoModel(BaseModel):
    id: str
    name: str
    category: str
    weight_kg: float
    origin_id: str
    destination_id: str
    lifecycle_stage: str
    current_temp_c: float
    min_temp_c: float
    max_temp_c: float
    cooling_active: bool
    condition: str
    assigned_vehicle_id: Optional[str] = None


class CargoListResponse(BaseModel):
    scenario_id: int
    cargo: List[CargoModel]
