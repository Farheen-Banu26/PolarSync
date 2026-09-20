"""
Cargo API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.cargo import CargoListResponse, CargoModel

router = APIRouter()


@router.get("", response_model=CargoListResponse)
def get_cargo(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get cold-chain cargo lifecycle states and thermal telemetry.
    """
    try:
        cargo_data = simulation_service.get_cargo(scenario_id)
        return CargoListResponse(
            scenario_id=scenario_id,
            cargo=[CargoModel(**c) for c in cargo_data]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cargo: {str(e)}")
