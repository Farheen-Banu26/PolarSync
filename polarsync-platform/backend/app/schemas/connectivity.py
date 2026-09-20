"""
Connectivity Schemas
"""
from typing import Optional
from pydantic import BaseModel


class ConnectivityResponse(BaseModel):
    scenario_id: int
    network_status: str
    buffered_event_count: int
    synchronized_event_count: int
    sync_status: str
    is_outage_scenario: bool
    description: str
