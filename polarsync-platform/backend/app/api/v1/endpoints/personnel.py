"""
Personnel API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.personnel import PersonnelResponse, PersonnelModel, MusterSummaryModel

router = APIRouter()


@router.get("", response_model=PersonnelResponse)
def get_personnel(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get personnel roster and muster accountability status.
    """
    try:
        data = simulation_service.get_personnel(scenario_id)
        muster_summary = MusterSummaryModel(**data["muster_summary"]) if data.get("muster_summary") else None
        return PersonnelResponse(
            scenario_id=scenario_id,
            personnel=[PersonnelModel(**p) for p in data["personnel"]],
            muster_summary=muster_summary
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch personnel: {str(e)}")
