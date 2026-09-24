"""
API v1 Router Aggregator
SIH Problem Statement: SIH26062
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    auth,
    scenarios,
    expeditions,
    dashboard,
    assets,
    personnel,
    cargo,
    inventory,
    emergencies,
    connectivity,
    alerts,
    map as map_endpoints,
    sync,
    intelligence,
    audit
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(expeditions.router, prefix="/expeditions", tags=["Expedition Planning"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(personnel.router, prefix="/personnel", tags=["Personnel"])
api_router.include_router(cargo.router, prefix="/cargo", tags=["Cargo"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(emergencies.router, prefix="/emergencies", tags=["Emergencies"])
api_router.include_router(connectivity.router, prefix="/connectivity", tags=["Connectivity"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(map_endpoints.router, prefix="/map", tags=["GIS Map"])
api_router.include_router(sync.router, prefix="/sync", tags=["Offline Sync"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Operational Intelligence"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["Audit Logs"])
