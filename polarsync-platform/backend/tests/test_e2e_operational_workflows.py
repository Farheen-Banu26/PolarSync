"""
PolarSync End-to-End Operational Workflows Test Suite
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
    """Reset any runtime overrides before and after each test for strict isolation."""
    EMERGENCY_OVERRIDES.clear()
    CARGO_OVERRIDES.clear()
    PERSONNEL_OVERRIDES.clear()
    ALERT_OVERRIDES.clear()
    yield
    EMERGENCY_OVERRIDES.clear()
    CARGO_OVERRIDES.clear()
    PERSONNEL_OVERRIDES.clear()
    ALERT_OVERRIDES.clear()


def test_phase3_rbac_authorization_enforcement():
    """Verify RBAC: Viewer role is rejected with 403 on mutations, authorized roles succeed."""
    # 1. Login as Viewer
    viewer_login = client.post("/api/v1/auth/login", json={"username": "viewer", "password": "polar2026"})
    assert viewer_login.status_code == 200
    viewer_token = viewer_login.json()["access_token"]
    viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

    # 2. Login as Commander
    cmd_login = client.post("/api/v1/auth/login", json={"username": "commander", "password": "polar2026"})
    assert cmd_login.status_code == 200
    cmd_token = cmd_login.json()["access_token"]
    cmd_headers = {"Authorization": f"Bearer {cmd_token}"}

    # 3. Viewer attempts to dispatch SAR -> MUST FAIL (403)
    sar_payload = {"selected_vehicle_id": "PB-300-01", "reason": "Viewer unauthorized attempt"}
    viewer_sar = client.post("/api/v1/emergencies/INC-001/dispatch-sar", json=sar_payload, headers=viewer_headers)
    assert viewer_sar.status_code == 403

    # 4. Viewer attempts to approve route -> MUST FAIL (403)
    route_payload = {
        "name": "Unauthorized Route",
        "origin_id": "MAITRI_II",
        "destination_id": "CAMP_ALPHA",
        "vehicle_id": "TV-01",
        "total_distance_km": 40.0,
        "estimated_travel_time_hours": 2.0,
        "waypoints": [[-70.80, 11.74]]
    }
    viewer_route = client.post("/api/v1/expeditions/save-route", json=route_payload, headers=viewer_headers)
    assert viewer_route.status_code == 403

    # 5. Commander dispatches SAR -> MUST SUCCEED (200)
    cmd_sar = client.post("/api/v1/emergencies/INC-001/dispatch-sar", json=sar_payload, headers=cmd_headers)
    assert cmd_sar.status_code == 200
    assert cmd_sar.json()["emergency_status"] == "DISPATCHED"


def test_phase4_route_planning_and_hazard_detection():
    """Verify route planning calculates metrics and detects danger zone proximities."""
    # Unsafe / Crevasse proximity traverse
    unsafe_payload = {
        "origin_id": "MAITRI_II",
        "origin_coords": [-70.7667, 11.7333],
        "destination_id": "DEPOT_ZULU",
        "destination_coords": [-71.1500, 11.6000],
        "waypoints": [[-70.8500, 11.7800]],  # Passes through crevasse field
        "vehicle_id": "SKIDOO-01",
        "vehicle_name": "Skidoo Scout-1",
        "avg_speed_kmh": 25.0,
        "fuel_consumption_l_per_km": 0.8,
        "vehicle_fuel_capacity_l": 60.0,
        "current_fuel_pct": 30.0  # Low fuel intentionally
    }
    res = client.post("/api/v1/expeditions/plan-route", json=unsafe_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_distance_km"] > 0
    # Should flag critical risk due to insufficient fuel
    assert data["is_fuel_feasible"] is False
    assert data["risk_level"] == "CRITICAL"
    assert data["validation_status"] == "REQUIRES_OVERRIDE"


def test_phase5_cargo_lifecycle_transitions():
    """Verify cargo transitions and rejection of invalid states."""
    cmd_login = client.post("/api/v1/auth/login", json={"username": "logistics", "password": "polar2026"})
    headers = {"Authorization": f"Bearer {cmd_login.json()['access_token']}"}

    # Valid transition to PACKED
    res1 = client.post("/api/v1/cargo/CARGO-002/update-stage", json={"new_stage": "PACKED"}, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["lifecycle_stage"] == "PACKED"

    # Valid transition to IN_TRANSIT
    res2 = client.post("/api/v1/cargo/CARGO-002/update-stage", json={"new_stage": "IN_TRANSIT"}, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["lifecycle_stage"] == "IN_TRANSIT"

    # Invalid stage rejection (400)
    res_bad = client.post("/api/v1/cargo/CARGO-002/update-stage", json={"new_stage": "INVALID_STATE"}, headers=headers)
    assert res_bad.status_code == 400


def test_phase9_emergency_sar_decision_scoring():
    """Verify SAR decision support multi-criteria ranking."""
    res = client.get("/api/v1/emergencies?scenario_id=3")
    assert res.status_code == 200
    data = res.json()
    assert data["has_active_emergency"] is True
    assert "CREVASSE_FALL" in data["emergency"]["incident_type"]
    assert data["sar_decision"] is not None
    assert len(data["sar_decision"]["evaluations"]) >= 3


def test_phase11_smart_automation_triggers():
    """Verify deterministic intelligence for all 5 scenarios."""
    # Scenario 2: Fuel Crisis
    res_auto = client.get("/api/v1/intelligence/autonomy?scenario_id=2")
    assert res_auto.status_code == 200
    items = res_auto.json()
    fuel_item = next((i for i in items if i["category"].upper() == "FUEL"), None)
    assert fuel_item is not None
    assert fuel_item["risk"] == "CRITICAL"
    assert fuel_item["days_of_autonomy"] < 7.0

    # Scenario 4: Cold-Chain Breach
    res_readiness = client.get("/api/v1/intelligence/readiness?scenario_id=4")
    assert res_readiness.status_code == 200
    r_data = res_readiness.json()
    assert r_data["overall_state"] == "DEGRADED"


def test_phase13_sync_persistence_and_audit():
    """Verify offline sync request mutates state and creates audit records."""
    sync_payload = {
        "operations": [
            {
                "id": "SYNC-TEST-001",
                "resource": "personnel",
                "operation": "UPDATE_CHECKIN",
                "payload": {"personnel_id": "P-04", "muster_status": "ACCOUNTED"},
                "timestamp": "2026-09-23T12:00:00Z"
            },
            {
                "id": "SYNC-TEST-002",
                "resource": "cargo",
                "operation": "UPDATE_STAGE",
                "payload": {"cargo_id": "CARGO-003", "lifecycle_stage": "DELIVERED"},
                "timestamp": "2026-09-23T12:00:01Z"
            }
        ]
    }
    sync_res = client.post("/api/v1/sync", json=sync_payload)
    assert sync_res.status_code == 200
    data = sync_res.json()
    assert len(data["accepted"]) == 2
    assert len(data["rejected"]) == 0

    # Verify audit log recorded both sync actions
    audit_res = client.get("/api/v1/audit-logs?limit=10")
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert any(log["action"] == "OFFLINE_SYNC_PERSONNEL_CHECKIN" for log in logs)
    assert any(log["action"] == "OFFLINE_SYNC_CARGO_UPDATE" for log in logs)
