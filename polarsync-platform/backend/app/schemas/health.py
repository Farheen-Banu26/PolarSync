"""
PolarSync Health Check Schemas
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: Optional[str] = None
    database: Optional[Dict[str, Any]] = None
    simulation_engine: Optional[str] = None
