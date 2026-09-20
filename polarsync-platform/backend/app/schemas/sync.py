"""
Synchronization API Schemas (Stage 3.4 Offline-First Sync)
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SyncOperationModel(BaseModel):
    id: str = Field(..., description="Unique UUID or client-generated ID for the operation")
    resource: str = Field(..., description="Target domain resource: personnel, cargo, assets, etc.")
    operation: str = Field(..., description="Action: UPDATE_CHECKIN, UPDATE_STAGE, UPDATE_STATUS, etc.")
    payload: Dict[str, Any] = Field(..., description="Operational payload data")
    timestamp: str = Field(..., description="ISO 8601 client generation timestamp")
    retry_count: Optional[int] = Field(0, description="Number of sync retries")


class SyncRequest(BaseModel):
    operations: List[SyncOperationModel] = Field(default_factory=list, description="Batch of local offline operations to synchronize")


class SyncResultItem(BaseModel):
    id: str
    resource: str
    operation: str
    status: str  # ACCEPTED or REJECTED
    message: str


class SyncResponse(BaseModel):
    accepted: List[SyncResultItem] = Field(default_factory=list)
    rejected: List[SyncResultItem] = Field(default_factory=list)
    server_timestamp: str
