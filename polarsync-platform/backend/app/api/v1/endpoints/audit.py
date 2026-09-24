"""
PolarSync Audit Log Endpoints
SIH Problem Statement: SIH26062
"""
from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.audit_service import audit_service

router = APIRouter()


class AuditLogItem(BaseModel):
    id: int
    operator: str
    role: str
    action: str
    entity_type: str
    entity_id: str
    details: dict
    timestamp: str


@router.get("", response_model=List[AuditLogItem])
@router.get("/", response_model=List[AuditLogItem])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (CARGO, SAR, MUSTER, ASSET, AUTH, ROUTE)")
):
    """
    Fetch chronological audit logs of all operator actions and smart automation events.
    """
    logs = audit_service.get_logs(limit=limit, entity_type=entity_type)
    return [AuditLogItem(**log) for log in logs]
