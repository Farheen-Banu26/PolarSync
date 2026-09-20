"""
Connectivity API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.connectivity import ConnectivityResponse

router = APIRouter()


@router.get("", response_model=ConnectivityResponse)
def get_connectivity(scenario_id: int = Query(5, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get satellite link status and store-and-forward sync metrics.
    """
    try:
        data = simulation_service.get_connectivity(scenario_id)
        return ConnectivityResponse(**data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch connectivity: {str(e)}")
