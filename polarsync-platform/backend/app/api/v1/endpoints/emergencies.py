"""
Emergencies API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.emergency import EmergencyResponse, EmergencyIncidentModel, SarDecisionModel, SarEvaluationModel

router = APIRouter()


@router.get("", response_model=EmergencyResponse)
def get_emergencies(scenario_id: int = Query(3, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get active emergency incident details and SAR asset allocation matrix.
    """
    try:
        data = simulation_service.get_emergencies(scenario_id)
        
        emergency_model = EmergencyIncidentModel(**data["emergency"]) if data.get("emergency") else None
        
        sar_decision_model = None
        if data.get("sar_decision"):
            evals = [SarEvaluationModel(**ev) for ev in data["sar_decision"]["evaluations"]]
            sar_decision_model = SarDecisionModel(
                selected_vehicle_id=data["sar_decision"]["selected_vehicle_id"],
                selected_vehicle_name=data["sar_decision"]["selected_vehicle_name"],
                evaluations=evals
            )

        return EmergencyResponse(
            scenario_id=scenario_id,
            has_active_emergency=data["has_active_emergency"],
            emergency=emergency_model,
            sar_decision=sar_decision_model
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emergencies: {str(e)}")
