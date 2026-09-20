"""
Dashboard API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter()


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get aggregated mission command center summary for selected scenario.
    """
    try:
        data = simulation_service.get_dashboard_summary(scenario_id)
        return DashboardSummaryResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard summary: {str(e)}")
