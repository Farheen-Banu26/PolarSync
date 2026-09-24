"""
Emergencies & Search and Rescue (SAR) API Endpoints
SIH Problem Statement: SIH26062
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from app.services.simulation_service import simulation_service
from app.services.audit_service import audit_service
from app.schemas.emergency import EmergencyResponse, EmergencyIncidentModel, SarDecisionModel, SarEvaluationModel
from app.api.v1.endpoints.auth import require_permission, UserProfile

router = APIRouter()

EMERGENCY_OVERRIDES: Dict[str, Dict[str, Any]] = {}


class DispatchSarRequest(BaseModel):
    selected_vehicle_id: str
    operator: Optional[str] = None
    reason: Optional[str] = "Optimal SAR score based on ETA and fuel margin"


class ResolveEmergencyRequest(BaseModel):
    operator: Optional[str] = None
    outcome_notes: Optional[str] = "Casualty extracted safely to Maitri-II medical bay"


@router.get("", response_model=EmergencyResponse)
def get_emergencies(scenario_id: int = Query(3, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get active emergency incident details and SAR asset allocation matrix.
    """
    try:
        data = simulation_service.get_emergencies(scenario_id)
        
        emergency_dict = data.get("emergency")
        if emergency_dict:
            e_id = emergency_dict.get("id")
            if e_id in EMERGENCY_OVERRIDES:
                emergency_dict = {**emergency_dict, **EMERGENCY_OVERRIDES[e_id]}

        emergency_model = EmergencyIncidentModel(**emergency_dict) if emergency_dict else None
        
        sar_decision_model = None
        if data.get("sar_decision"):
            evals = [SarEvaluationModel(**ev) for ev in data["sar_decision"]["evaluations"]]
            
            selected_v_id = data["sar_decision"]["selected_vehicle_id"]
            if emergency_dict and emergency_dict.get("assigned_vehicle_id"):
                selected_v_id = emergency_dict["assigned_vehicle_id"]

            sar_decision_model = SarDecisionModel(
                selected_vehicle_id=selected_v_id,
                selected_vehicle_name=data["sar_decision"]["selected_vehicle_name"],
                evaluations=evals
            )

        has_active = data.get("has_active_emergency", emergency_model is not None)
        if emergency_dict and emergency_dict.get("id") in EMERGENCY_OVERRIDES:
            if EMERGENCY_OVERRIDES[emergency_dict["id"]].get("status") == "RESOLVED":
                has_active = False

        return EmergencyResponse(
            scenario_id=scenario_id,
            has_active_emergency=has_active,
            emergency=emergency_model,
            sar_decision=sar_decision_model
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emergencies: {str(e)}")


@router.post("/{incident_id}/dispatch-sar")
def dispatch_sar_team(
    incident_id: str,
    req: DispatchSarRequest,
    current_user: UserProfile = Depends(require_permission("DISPATCH_SAR"))
):
    """
    Commander / Safety action: Authorize and dispatch selected SAR vehicle team.
    Protected by RBAC: requires DISPATCH_SAR permission (Commander, Safety Officer, Admin).
    """
    EMERGENCY_OVERRIDES[incident_id] = {
        "status": "DISPATCHED",
        "assigned_vehicle_id": req.selected_vehicle_id
    }

    operator_name = req.operator or current_user.full_name

    audit_service.log_action(
        operator=operator_name,
        role=current_user.role,
        action="SAR_VEHICLE_DISPATCHED",
        entity_type="SAR",
        entity_id=incident_id,
        details={"vehicle_id": req.selected_vehicle_id, "reason": req.reason}
    )

    return {
        "status": "success",
        "incident_id": incident_id,
        "assigned_vehicle_id": req.selected_vehicle_id,
        "emergency_status": "DISPATCHED",
        "message": f"SAR team dispatched with vehicle {req.selected_vehicle_id}"
    }


@router.post("/{incident_id}/resolve")
def resolve_emergency(
    incident_id: str,
    req: ResolveEmergencyRequest,
    current_user: UserProfile = Depends(require_permission("RESOLVE_EMERGENCY"))
):
    """
    Safety / Commander action: Mark emergency incident as resolved after casualty recovery.
    Protected by RBAC: requires RESOLVE_EMERGENCY permission (Safety Officer, Commander, Admin).
    """
    EMERGENCY_OVERRIDES[incident_id] = {
        "status": "RESOLVED",
        "resolution_notes": req.outcome_notes
    }

    operator_name = req.operator or current_user.full_name

    audit_service.log_action(
        operator=operator_name,
        role=current_user.role,
        action="EMERGENCY_INCIDENT_RESOLVED",
        entity_type="SAR",
        entity_id=incident_id,
        details={"notes": req.outcome_notes}
    )

    return {
        "status": "success",
        "incident_id": incident_id,
        "emergency_status": "RESOLVED",
        "message": f"Emergency incident {incident_id} successfully closed and archived"
    }


@router.post("/{incident_id}/reset")
def reset_emergency(incident_id: str):
    """
    Reset emergency incident back to initial DETECTED state for live demonstrations.
    """
    if incident_id in EMERGENCY_OVERRIDES:
        del EMERGENCY_OVERRIDES[incident_id]

    return {
        "status": "success",
        "incident_id": incident_id,
        "emergency_status": "DETECTED",
        "message": f"Emergency incident {incident_id} reset to initial DETECTED state."
    }
