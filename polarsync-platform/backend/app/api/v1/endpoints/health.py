"""
PolarSync Health & Diagnostics Endpoints
"""
from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.core.config import settings
from app.db.session import check_db_connection
from app.services.simulation_service import simulation_service

router = APIRouter()


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse)
def get_v1_health() -> HealthResponse:
    """
    V1 API Health Check Endpoint.
    Returns service identification, database status, and simulator interface readiness.
    """
    db_status = check_db_connection()
    sim_status = simulation_service.get_simulation_status()

    return HealthResponse(
        status="ok",
        service="polarsync-api",
        version=settings.VERSION,
        database=db_status,
        simulation_engine="connected" if sim_status["available"] else "disconnected"
    )
