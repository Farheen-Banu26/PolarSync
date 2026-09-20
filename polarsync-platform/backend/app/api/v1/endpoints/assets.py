"""
Assets API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.assets import AssetListResponse, AssetModel

router = APIRouter()


@router.get("", response_model=AssetListResponse)
def get_assets(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get vehicle fleet telemetry and operational status.
    """
    try:
        assets_data = simulation_service.get_assets(scenario_id)
        return AssetListResponse(
            scenario_id=scenario_id,
            assets=[AssetModel(**a) for a in assets_data]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")
