"""
Personnel API Endpoints
SIH Problem Statement: SIH26062
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from app.services.simulation_service import simulation_service
from app.services.audit_service import audit_service
from app.schemas.personnel import PersonnelResponse, PersonnelModel, MusterSummaryModel
from app.api.v1.endpoints.auth import require_permission, UserProfile

router = APIRouter()

PERSONNEL_OVERRIDES: Dict[str, Dict[str, Any]] = {}


class MusterCheckInRequest(BaseModel):
    status: str = "CHECKED_IN"  # CHECKED_IN, ON_PATROL, REST_PERIOD, EVACUATED
    operator: Optional[str] = None
    notes: Optional[str] = None


@router.get("", response_model=PersonnelResponse)
def get_personnel(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get expedition personnel roster, muster status, and GPS coordinates.
    """
    try:
        data = simulation_service.get_personnel(scenario_id)
        
        # Handle dict or list returned by simulation service
        if isinstance(data, dict):
            raw_personnel = data.get("personnel", [])
            muster_data = data.get("muster_summary")
        else:
            raw_personnel = data
            muster_data = None

        merged_personnel = []
        for p in raw_personnel:
            p_copy = dict(p)
            if p["id"] in PERSONNEL_OVERRIDES:
                p_copy.update(PERSONNEL_OVERRIDES[p["id"]])
            merged_personnel.append(PersonnelModel(**p_copy))

        muster_model = MusterSummaryModel(**muster_data) if muster_data else None

        return PersonnelResponse(
            scenario_id=scenario_id,
            personnel=merged_personnel,
            muster_summary=muster_model
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch personnel: {str(e)}")


@router.post("/{personnel_id}/check-in")
def check_in_personnel(
    personnel_id: str,
    req: MusterCheckInRequest,
    current_user: UserProfile = Depends(require_permission("MUSTER_CHECKIN"))
):
    """
    Field / Safety action: Record muster check-in or safety confirmation for a team member.
    Protected by RBAC: requires MUSTER_CHECKIN permission (Field Operator, Safety Officer, Commander, Admin).
    """
    valid_statuses = ["CHECKED_IN", "ON_PATROL", "REST_PERIOD", "EVACUATED", "ACCOUNTED"]
    st_val = req.status.upper()
    if st_val not in valid_statuses:
        st_val = "CHECKED_IN"

    PERSONNEL_OVERRIDES[personnel_id] = {
        "status": st_val,
        "heartbeat_active": True
    }

    operator_name = req.operator or current_user.full_name

    audit_service.log_action(
        operator=operator_name,
        role=current_user.role,
        action="PERSONNEL_MUSTER_CHECKIN",
        entity_type="PERSONNEL",
        entity_id=personnel_id,
        details={"status": st_val, "notes": req.notes}
    )

    return {
        "status": "success",
        "personnel_id": personnel_id,
        "status_value": st_val,
        "message": f"Personnel {personnel_id} status updated to {st_val}"
    }
