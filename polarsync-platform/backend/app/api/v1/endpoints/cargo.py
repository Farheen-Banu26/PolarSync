"""
Cargo API Endpoints
SIH Problem Statement: SIH26062
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel
from app.services.simulation_service import simulation_service
from app.services.audit_service import audit_service
from app.schemas.cargo import CargoListResponse, CargoModel
from app.api.v1.endpoints.auth import require_permission, UserProfile

router = APIRouter()

# In-memory overrides for cargo state
CARGO_OVERRIDES: Dict[str, Dict[str, Any]] = {}


class UpdateCargoStageRequest(BaseModel):
    new_stage: str  # CREATED, PACKED, ASSIGNED, IN_TRANSIT, DELIVERED
    operator: Optional[str] = None
    notes: Optional[str] = None


@router.get("", response_model=CargoListResponse)
def get_cargo(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get cold-chain cargo lifecycle states and thermal telemetry.
    """
    try:
        cargo_data = simulation_service.get_cargo(scenario_id)
        
        # Apply any live overrides
        merged_cargo = []
        for c in cargo_data:
            c_copy = dict(c)
            if c["id"] in CARGO_OVERRIDES:
                c_copy.update(CARGO_OVERRIDES[c["id"]])
            merged_cargo.append(CargoModel(**c_copy))

        return CargoListResponse(
            scenario_id=scenario_id,
            cargo=merged_cargo
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cargo: {str(e)}")


@router.post("/{cargo_id}/update-stage")
def update_cargo_stage(
    cargo_id: str,
    req: UpdateCargoStageRequest,
    current_user: UserProfile = Depends(require_permission("UPDATE_CARGO"))
):
    """
    Operator action: Advance cargo lifecycle stage (e.g. IN_TRANSIT -> DELIVERED).
    Protected by RBAC: requires UPDATE_CARGO permission (Logistics, Field Operator, Commander, Admin).
    """
    valid_stages = ["CREATED", "PACKED", "ASSIGNED", "IN_TRANSIT", "DELIVERED"]
    if req.new_stage.upper() not in valid_stages:
        raise HTTPException(status_code=400, detail=f"Invalid stage '{req.new_stage}'. Allowed: {valid_stages}")

    stage_val = req.new_stage.upper()
    CARGO_OVERRIDES[cargo_id] = {
        "lifecycle_stage": stage_val,
        "status_notes": req.notes or f"Updated to {stage_val}"
    }

    operator_name = req.operator or current_user.full_name

    audit_service.log_action(
        operator=operator_name,
        role=current_user.role,
        action=f"CARGO_STAGE_UPDATED_TO_{stage_val}",
        entity_type="CARGO",
        entity_id=cargo_id,
        details={"new_stage": stage_val, "notes": req.notes}
    )

    return {
        "status": "success",
        "cargo_id": cargo_id,
        "lifecycle_stage": stage_val,
        "message": f"Cargo {cargo_id} transitioned to {stage_val}"
    }
