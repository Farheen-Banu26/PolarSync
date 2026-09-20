"""
Alert Schemas
"""
from typing import List, Optional, Any
from pydantic import BaseModel


class AlertModel(BaseModel):
    id: str
    timestamp_tick: int
    severity: str
    category: str
    source_entity_id: Optional[str] = None
    message: str
    details: Optional[Any] = None


class AlertListResponse(BaseModel):
    scenario_id: int
    total_alerts: int
    critical_alerts: int
    warning_alerts: int
    alerts: List[AlertModel]
