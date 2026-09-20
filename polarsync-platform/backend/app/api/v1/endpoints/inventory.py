"""
Inventory API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.inventory import InventoryListResponse, InventoryItemModel

router = APIRouter()


@router.get("", response_model=InventoryListResponse)
def get_inventory(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get inventory stock levels and Days of Autonomy calculations.
    """
    try:
        inv_data = simulation_service.get_inventory(scenario_id)
        return InventoryListResponse(
            scenario_id=scenario_id,
            inventory=[InventoryItemModel(**item) for item in inv_data]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch inventory: {str(e)}")
