"""
PolarSync Expedition & Route Planning Endpoints
SIH Problem Statement: SIH26062
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field
from app.services.route_planning_service import route_planning_service
from app.services.simulation_service import simulation_service
from app.services.audit_service import audit_service
from app.api.v1.endpoints.auth import require_permission, UserProfile

router = APIRouter()

# In-memory planned and executed routes storage
PLANNED_ROUTES: Dict[str, Dict[str, Any]] = {}


class RoutePlanRequest(BaseModel):
    origin_id: str
    origin_coords: List[float] = Field(..., description="[Latitude, Longitude]")
    destination_id: str
    destination_coords: List[float] = Field(..., description="[Latitude, Longitude]")
    waypoints: List[List[float]] = Field(default=[], description="List of [Lat, Lon] points")
    vehicle_id: str
    vehicle_name: str
    avg_speed_kmh: float = 18.0
    fuel_consumption_l_per_km: float = 1.4
    vehicle_fuel_capacity_l: float = 450.0
    current_fuel_pct: float = 100.0


class RoutePlanResponse(BaseModel):
    origin_id: str
    destination_id: str
    vehicle_id: str
    total_distance_km: float
    estimated_travel_time_hours: float
    fuel_required_liters: float
    fuel_remaining_liters: float
    fuel_remaining_pct: float
    is_fuel_feasible: bool
    risk_level: str
    hazard_warnings: List[Dict[str, Any]]
    validation_status: str
    waypoints: List[List[float]]


class SaveRouteRequest(BaseModel):
    name: str
    origin_id: str
    destination_id: str
    vehicle_id: str
    total_distance_km: float
    estimated_travel_time_hours: float
    waypoints: List[List[float]]
    notes: Optional[str] = None


@router.post("/plan-route", response_model=RoutePlanResponse)
def plan_expedition_route(req: RoutePlanRequest, scenario_id: int = Query(1, ge=1, le=5)):
    """
    Evaluates traverse route feasibility: distance, speed-adjusted ETA, vehicle fuel margin, and danger zone intersections.
    Accessible to all operational roles.
    """
    try:
        map_topology = simulation_service.get_map_topology(scenario_id)
        danger_zones = map_topology.get("danger_zones", [])

        metrics = route_planning_service.calculate_route_metrics(
            origin_coords=req.origin_coords,
            destination_coords=req.destination_coords,
            waypoints=req.waypoints,
            avg_speed_kmh=req.avg_speed_kmh,
            fuel_consumption_l_per_km=req.fuel_consumption_l_per_km,
            vehicle_fuel_capacity_l=req.vehicle_fuel_capacity_l,
            current_fuel_pct=req.current_fuel_pct,
            danger_zones=danger_zones
        )

        return RoutePlanResponse(
            origin_id=req.origin_id,
            destination_id=req.destination_id,
            vehicle_id=req.vehicle_id,
            total_distance_km=metrics["total_distance_km"],
            estimated_travel_time_hours=metrics["estimated_travel_time_hours"],
            fuel_required_liters=metrics["fuel_required_liters"],
            fuel_remaining_liters=metrics["fuel_remaining_liters"],
            fuel_remaining_pct=metrics["fuel_remaining_pct"],
            is_fuel_feasible=metrics["is_fuel_feasible"],
            risk_level=metrics["risk_level"],
            hazard_warnings=metrics["hazard_warnings"],
            validation_status=metrics["validation_status"],
            waypoints=metrics["waypoints"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to plan route: {str(e)}")


@router.post("/save-route")
def save_expedition_route(
    req: SaveRouteRequest,
    current_user: UserProfile = Depends(require_permission("APPROVE_ROUTES"))
):
    """
    Saves an approved traverse route and logs the commander's planning action.
    Protected by RBAC: requires APPROVE_ROUTES permission (Commander, Administrator).
    """
    route_id = f"ROUTE-PLANNED-{len(PLANNED_ROUTES) + 1:03d}"
    route_record = {
        "id": route_id,
        "name": req.name,
        "origin_id": req.origin_id,
        "destination_id": req.destination_id,
        "vehicle_id": req.vehicle_id,
        "distance_km": req.total_distance_km,
        "estimated_time_hours": req.estimated_travel_time_hours,
        "waypoints": req.waypoints,
        "status": "APPROVED",
        "notes": req.notes
    }
    PLANNED_ROUTES[route_id] = route_record

    audit_service.log_action(
        operator=current_user.full_name,
        role=current_user.role,
        action="ROUTE_PLANNED_AND_APPROVED",
        entity_type="ROUTE",
        entity_id=route_id,
        details={
            "name": req.name,
            "corridor": f"{req.origin_id} -> {req.destination_id}",
            "vehicle": req.vehicle_id,
            "distance_km": req.total_distance_km
        }
    )

    return {"status": "success", "route_id": route_id, "route": route_record}


@router.get("/planned-routes")
def get_planned_routes():
    """
    Retrieve all custom planned traverse routes.
    """
    return list(PLANNED_ROUTES.values())
