"""
Map Topology API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.simulation_service import simulation_service
from app.schemas.map import MapTopologyResponse, MapLocationModel, DangerZoneModel, RouteModel
from app.schemas.assets import AssetModel
from app.schemas.personnel import PersonnelModel
from app.schemas.emergency import EmergencyIncidentModel

router = APIRouter()


@router.get("/topology", response_model=MapTopologyResponse)
def get_map_topology(scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)")):
    """
    Get all map GIS topology including base stations, danger zones, routes, vehicles, personnel, and emergencies.
    """
    try:
        data = simulation_service.get_map_topology(scenario_id)
        
        emergency_model = EmergencyIncidentModel(**data["emergency"]) if data.get("emergency") else None

        return MapTopologyResponse(
            scenario_id=scenario_id,
            locations=[MapLocationModel(**loc) for loc in data["locations"]],
            danger_zones=[DangerZoneModel(**dz) for dz in data["danger_zones"]],
            routes=[RouteModel(**r) for r in data["routes"]],
            assets=[AssetModel(**a) for a in data["assets"]],
            personnel=[PersonnelModel(**p) for p in data.get("personnel", [])],
            emergency=emergency_model
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch map topology: {str(e)}")
