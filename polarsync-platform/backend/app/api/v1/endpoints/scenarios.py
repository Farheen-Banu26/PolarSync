"""
Scenarios API Endpoints
"""
from fastapi import APIRouter, HTTPException
from app.services.simulation_service import simulation_service
from app.schemas.scenarios import ScenarioListResponse, ScenarioSummaryResponse, ScenarioModel

router = APIRouter()


@router.get("", response_model=ScenarioListResponse)
def get_scenarios():
    """
    Get all available polar operational scenarios.
    """
    try:
        scenarios_data = simulation_service.list_available_scenarios()
        return ScenarioListResponse(
            scenarios=[ScenarioModel(**s) for s in scenarios_data],
            total_count=len(scenarios_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load scenarios: {str(e)}")


@router.get("/{scenario_id}/summary", response_model=ScenarioSummaryResponse)
def get_scenario_summary(scenario_id: int):
    """
    Get high-level execution summary for a specific scenario.
    """
    try:
        data = simulation_service.get_scenario_summary(scenario_id)
        return ScenarioSummaryResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation execution error: {str(e)}")
