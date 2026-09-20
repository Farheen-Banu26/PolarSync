"""
Inventory Schemas
"""
from typing import List, Optional
from pydantic import BaseModel


class InventoryItemModel(BaseModel):
    category: str
    location_id: str
    location_name: str
    current_stock: float
    unit: str
    daily_consumption_rate: float
    days_of_autonomy: float
    next_resupply_window_days: float
    safety_buffer_days: float
    resupply_risk: str


class InventoryListResponse(BaseModel):
    scenario_id: int
    inventory: List[InventoryItemModel]
