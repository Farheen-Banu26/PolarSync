"""
PolarSync Extended Operations & SIH Subsystems Test Suite
Tests authentication, route planning, audit logging, and operational mutations.
SIH Problem Statement: SIH26062
"""
import os
import sys
import pytest

# Ensure backend root is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.api.v1.endpoints.emergencies import EMERGENCY_OVERRIDES
from app.api.v1.endpoints.cargo import CARGO_OVERRIDES
from app.api.v1.endpoints.personnel import PERSONNEL_OVERRIDES
from app.api.v1.endpoints.alerts import ALERT_OVERRIDES

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_overrides():
    EMERGENCY_OVERRIDES.clear()
    CARGO_OVERRIDES.clear()
    PERSONNEL_OVERRIDES.clear()
    ALERT_OVERRIDES.clear()
    yield
    EMERGENCY_OVERRIDES.clear()
    CARGO_OVERRIDES.clear()
    PERSONNEL_OVERRIDES.clear()
    ALERT_OVERRIDES.clear()


def test_auth_roles_and_login():
    # 1. Fetch available roles
    res = client.get("/api/v1/auth/roles")
    assert res.status_code == 200
    roles = res.json()
    assert len(roles) >= 5
    role_names = [r["role"] for r in roles]
    assert "Expedition Commander" in role_names
    assert "Logistics Officer" in role_names
    assert "Medical/Safety Officer" in role_names

    # 2. Login as Commander
    login_res = client.post("/api/v1/auth/login", json={"username": "commander", "password": "polar2026"})
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "Expedition Commander"

    # 3. Invalid credentials
    bad_res = client.post("/api/v1/auth/login", json={"username": "commander", "password": "wrongpassword"})
    assert bad_res.status_code == 401


def test_route_planning_engine():
    # Plan traverse from Maitri-II (-70.7667, 11.7333) to Camp Alpha (-70.8333, 11.7500)
    payload = {
        "origin_id": "MAITRI_II",
        "origin_coords": [-70.7667, 11.7333],
        "destination_id": "CAMP_ALPHA",
        "destination_coords": [-70.8333, 11.7500],
        "waypoints": [[-70.8000, 11.7400]],
        "vehicle_id": "TV-01",
        "vehicle_name": "PistenBully 300 Polar",
        "avg_speed_kmh": 18.0,
        "fuel_consumption_l_per_km": 1.4,
        "vehicle_fuel_capacity_l": 450.0,
        "current_fuel_pct": 95.0
    }
    res = client.post("/api/v1/expeditions/plan-route", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_distance_km"] > 0
    assert data["estimated_travel_time_hours"] > 0
    assert data["fuel_required_liters"] > 0
    assert data["is_fuel_feasible"] is True
    assert data["validation_status"] in ["APPROVED", "REQUIRES_OVERRIDE"]

    # Save route
    save_payload = {
        "name": "Maitri to Alpha Standard Resupply",
        "origin_id": "MAITRI_II",
        "destination_id": "CAMP_ALPHA",
        "vehicle_id": "TV-01",
        "total_distance_km": data["total_distance_km"],
        "estimated_travel_time_hours": data["estimated_travel_time_hours"],
        "waypoints": data["waypoints"]
    }
    save_res = client.post("/api/v1/expeditions/save-route", json=save_payload)
    assert save_res.status_code == 200
    assert "route_id" in save_res.json()


def test_cargo_stage_update_and_audit():
    # Advance cargo stage
    res = client.post("/api/v1/cargo/CARGO-001/update-stage", json={"new_stage": "DELIVERED", "operator": "Logistics Officer"})
    assert res.status_code == 200
    assert res.json()["lifecycle_stage"] == "DELIVERED"

    # Verify audit log was recorded
    audit_res = client.get("/api/v1/audit-logs?entity_type=CARGO")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert any(log["entity_id"] == "CARGO-001" for log in logs)


def test_emergency_sar_dispatch_and_resolution():
    # Dispatch SAR
    dispatch_res = client.post("/api/v1/emergencies/INC-001/dispatch-sar", json={
        "selected_vehicle_id": "PB-300-01",
        "operator": "Expedition Commander",
        "reason": "Optimal score and equipped with winch"
    })
    assert dispatch_res.status_code == 200
    assert dispatch_res.json()["emergency_status"] == "DISPATCHED"

    # Resolve incident
    resolve_res = client.post("/api/v1/emergencies/INC-001/resolve", json={
        "operator": "Medical/Safety Officer",
        "outcome_notes": "Casualty treated and evacuated safely"
    })
    assert resolve_res.status_code == 200
    assert resolve_res.json()["emergency_status"] == "RESOLVED"
