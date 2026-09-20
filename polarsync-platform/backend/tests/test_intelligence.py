import os
import sys
import pytest

# Ensure backend root is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_autonomy_intelligence_scenario_1():
    """Scenario 1 should show nominal/safe autonomy across all categories."""
    response = client.get("/api/v1/intelligence/autonomy?scenario_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    categories = [item["category"].upper() for item in data]
    assert "FUEL" in categories
    assert all(item["days_of_autonomy"] > 0 for item in data)


def test_autonomy_and_resupply_scenario_2_fuel_crisis():
    """Scenario 2 must produce CRITICAL fuel risk with days_of_autonomy < safety buffer."""
    response = client.get("/api/v1/intelligence/autonomy?scenario_id=2")
    assert response.status_code == 200
    data = response.json()
    fuel_items = [item for item in data if item["category"].upper() == "FUEL"]
    assert len(fuel_items) > 0
    fuel = fuel_items[0]
    assert fuel["risk"] == "CRITICAL"
    assert fuel["days_of_autonomy"] < fuel["safety_buffer_days"]
    assert "below the required safety buffer" in fuel["explanation"]

    # Resupply risk test
    resupply_res = client.get("/api/v1/intelligence/resupply-risk?scenario_id=2")
    assert resupply_res.status_code == 200
    res_data = resupply_res.json()
    fuel_risk = next(item for item in res_data if item["category"].upper() == "FUEL")
    assert fuel_risk["risk_level"] == "CRITICAL"
    assert "emergency" in fuel_risk["recommended_action"].lower() or "resupply" in fuel_risk["recommended_action"].lower()


@pytest.mark.parametrize("scenario_id, expected_state", [
    (1, "NOMINAL"),
    (2, "CRITICAL"),
    (3, "NOMINAL"),
    (4, "DEGRADED"),
    (5, "NOMINAL"),
])
def test_readiness_intelligence_all_scenarios(scenario_id, expected_state):
    """Readiness intelligence should accurately synthesize operational state for all 5 scenarios."""
    response = client.get(f"/api/v1/intelligence/readiness?scenario_id={scenario_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == scenario_id
    assert data["overall_state"] == expected_state
    assert len(data["factors"]) == 6
    factor_names = [f["name"] for f in data["factors"]]
    assert "Personnel" in factor_names
    assert "Fleet" in factor_names
    assert "Inventory" in factor_names
    assert "Cargo" in factor_names
    assert "Connectivity" in factor_names
    assert "Emergencies" in factor_names
    
    # Check explainability block
    exp = data["explainability"]
    assert exp["what_happened"]
    assert exp["why_it_matters"]
    assert exp["what_to_watch"]
    assert exp["recommended_operator_action"]


def test_emergency_intelligence_scenario_3():
    """Scenario 3 must expose the active emergency incident, SAR candidate matrix, and selected asset."""
    response = client.get("/api/v1/intelligence/emergency?scenario_id=3")
    assert response.status_code == 200
    data = response.json()
    assert data["has_active_emergency"] is True
    assert "CREVASSE_FALL" in data["incident"]["incident_type"]
    assert data["selected_asset_id"] is not None
    assert len(data["candidate_assets"]) > 0
    assert len(data["selection_reasons"]) > 0
    assert data["estimated_eta_min"] is not None


def test_resource_forecast_scenario_2():
    """Resource forecast should return projected depletion trajectory."""
    response = client.get("/api/v1/intelligence/forecast?scenario_id=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    fuel_fc = next(item for item in data if "Fuel" in item["resource"])
    assert fuel_fc["forecast_available"] is True
    assert len(fuel_fc["historical_points"]) > 0
    assert len(fuel_fc["projected_points"]) > 0
    assert any(p["is_projected"] for p in fuel_fc["projected_points"])
    assert "Projected based on current consumption trend" in fuel_fc["confidence_note"]


def test_intelligence_summary_all_scenarios():
    """Centralized intelligence summary endpoint must return for all scenarios 1-5."""
    for s_id in range(1, 6):
        res = client.get(f"/api/v1/intelligence/summary?scenario_id={s_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["scenario_id"] == s_id
        assert "overall_readiness" in data
        assert "highest_risk" in data
        assert len(data["autonomy"]) > 0
        assert len(data["resupply_risk"]) > 0
        assert data["readiness"] is not None
        assert data["emergency"] is not None
        assert data["explainability"]["what_happened"] is not None
