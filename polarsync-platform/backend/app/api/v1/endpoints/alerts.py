"""
Alerts API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.alerts import AlertListResponse, AlertModel

router = APIRouter()


@router.get("", response_model=AlertListResponse)
def get_alerts(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get operational alert log for selected scenario.
    """
    try:
        alerts_data = simulation_service.get_alerts(scenario_id)
        crit_count = sum(1 for a in alerts_data if a["severity"] == "CRITICAL")
        warn_count = sum(1 for a in alerts_data if a["severity"] == "WARNING")
        
        return AlertListResponse(
            scenario_id=scenario_id,
            total_alerts=len(alerts_data),
            critical_alerts=crit_count,
            warning_alerts=warn_count,
            alerts=[AlertModel(**a) for a in alerts_data]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch alerts: {str(e)}")
