"""
Emergency & SAR Schemas
"""
from typing import List, Optional
from pydantic import BaseModel


class EmergencyIncidentModel(BaseModel):
    id: str
    incident_type: str
    latitude: float
    longitude: float
    nearest_landmark: str
    severity: str
    status: str
    affected_personnel_ids: List[str]
    affected_count: int
    required_capabilities: List[str]
    timestamp_tick: int


class SAREvaluationModel(BaseModel):
    vehicle_id: str
    vehicle_name: str
    vehicle_type: str
    distance_km: float
    estimated_transit_time_min: float
    fuel_remaining_pct: float
    fuel_after_mission_pct: float
    is_eligible: bool
    score: float
    disqualification_reasons: List[str]
    explanation_points: List[str]


# Alias
SarEvaluationModel = SAREvaluationModel


class SARDecisionModel(BaseModel):
    selected_vehicle_id: Optional[str] = None
    selected_vehicle_name: Optional[str] = None
    evaluations: List[SAREvaluationModel] = []


# Alias
SarDecisionModel = SARDecisionModel


class EmergencyResponse(BaseModel):
    scenario_id: int
    has_active_emergency: bool
    emergency: Optional[EmergencyIncidentModel] = None
    sar_decision: Optional[SARDecisionModel] = None
