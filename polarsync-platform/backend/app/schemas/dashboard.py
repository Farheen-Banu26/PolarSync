"""
Dashboard Schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ReadinessInfo(BaseModel):
    status: str
    overall_score: str


class PersonnelSummary(BaseModel):
    total: int
    accounted: int
    unconfirmed: int


class AssetSummary(BaseModel):
    total: int
    active: int


class CargoSummary(BaseModel):
    total: int
    delivered: int
    in_transit: int
    cold_chain_health_pct: int


class AlertSummary(BaseModel):
    total: int
    critical: int
    warning: int


class ConnectivitySummary(BaseModel):
    status: str
    buffered_events: int
    synchronized: bool


class DashboardSummaryResponse(BaseModel):
    scenario_id: int
    scenario_name: str
    description: str
    readiness: ReadinessInfo
    personnel: PersonnelSummary
    assets: AssetSummary
    cargo: CargoSummary
    alerts: AlertSummary
    connectivity: ConnectivitySummary
    event_flow: List[str]
