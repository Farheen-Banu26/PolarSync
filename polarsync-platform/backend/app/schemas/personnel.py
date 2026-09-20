"""
Personnel Schemas
"""
from typing import List, Optional
from pydantic import BaseModel


class PersonnelModel(BaseModel):
    id: str
    name: str
    role: str
    assigned_location_id: str
    latitude: float
    longitude: float
    movement_status: str
    status: str
    heartbeat_active: bool
    assigned_vehicle_id: Optional[str] = None
    last_checkin_tick: int


class MusterSummaryModel(BaseModel):
    total_expected: int
    checked_in_count: int
    field_count: int
    unconfirmed_count: int
    unconfirmed_ids: List[str]
    status: str


class PersonnelResponse(BaseModel):
    scenario_id: int
    personnel: List[PersonnelModel]
    muster_summary: Optional[MusterSummaryModel] = None
