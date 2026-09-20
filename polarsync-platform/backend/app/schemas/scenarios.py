"""
Scenario Schemas
"""
from typing import List, Optional
from pydantic import BaseModel


class ScenarioModel(BaseModel):
    id: int
    name: str
    file: str
    description: str


# Alias for compatibility
ScenarioItem = ScenarioModel


class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioModel]
    total_count: Optional[int] = None


class ScenarioSummaryResponse(BaseModel):
    scenario_id: int
    name: str
    description: str
    total_ticks: int
    minutes_simulated: int
    random_seed: int
    readiness_status: str
    network_status: str
    alerts_count: int
    vehicles_count: int
    personnel_count: int
    cargo_count: int
