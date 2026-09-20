"""
Comprehensive System Audit & Determinism Validation Script for PolarSync (Stage 3.6)
"""
import os
import sys
import json
import numpy as np

# Ensure root and backend are in path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "polarsync-platform", "backend")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from src.scenario_runner import ScenarioRunner
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_determinism_audit():
    print("============================================================")
    print("1. DETERMINISM AUDIT: Comparing Dual-Run Outputs")
    print("============================================================")
    scenario_files = {
        1: "scenario_1_normal.json",
        2: "scenario_2_fuel_crisis.json",
        3: "scenario_3_emergency_sar.json",
        4: "scenario_4_cold_chain_breach.json",
        5: "scenario_5_connectivity_loss.json"
    }

    for s_id, sc_file in scenario_files.items():
        base_cfg = os.path.join(ROOT_DIR, "configs", "base_environment.json")
        sc_cfg = os.path.join(ROOT_DIR, "configs", "scenarios", sc_file)

        # Run 1
        r1 = ScenarioRunner(base_cfg, sc_cfg)
        out1 = r1.run(verbose=False)

        # Run 2
        r2 = ScenarioRunner(base_cfg, sc_cfg)
        out2 = r2.run(verbose=False)

        # Verify exact tick counts
        assert out1["total_ticks"] == out2["total_ticks"], f"Tick mismatch in scenario {s_id}"
        assert out1["final_readiness"].overall_status == out2["final_readiness"].overall_status

        # Verify vehicle telemetry matches
        df1 = r1.export_telemetry_dataframe()
        df2 = r2.export_telemetry_dataframe()
        assert len(df1) == len(df2), f"Telemetry row count mismatch in scenario {s_id}"
        assert (df1["speed_kmh"].values == df2["speed_kmh"].values).all()
        assert (df1["fuel_pct"].values == df2["fuel_pct"].values).all()
        assert (df1["battery_pct"].values == df2["battery_pct"].values).all()

        print(f"  [PASS] Scenario {s_id} ({sc_file}): 100% Deterministic across runs ({out1['total_ticks']} ticks, {len(df1)} telemetry frames)")

def run_telemetry_data_integrity_audit():
    print("\n============================================================")
    print("2. TELEMETRY & DATA INTEGRITY AUDIT")
    print("============================================================")
    scenario_files = {
        1: "scenario_1_normal.json",
        2: "scenario_2_fuel_crisis.json",
        3: "scenario_3_emergency_sar.json",
        4: "scenario_4_cold_chain_breach.json",
        5: "scenario_5_connectivity_loss.json"
    }

    for s_id, sc_file in scenario_files.items():
        base_cfg = os.path.join(ROOT_DIR, "configs", "base_environment.json")
        sc_cfg = os.path.join(ROOT_DIR, "configs", "scenarios", sc_file)

        r = ScenarioRunner(base_cfg, sc_cfg)
        out = r.run(verbose=False)
        df = r.export_telemetry_dataframe()

        # Bounds checks
        assert not df.isna().any().any(), f"NaN detected in telemetry for scenario {s_id}"
        assert (df["fuel_pct"] >= 0.0).all() and (df["fuel_pct"] <= 100.0).all(), "Fuel pct out of bounds"
        assert (df["battery_pct"] >= 0.0).all() and (df["battery_pct"] <= 100.0).all(), "Battery pct out of bounds"
        assert (df["speed_kmh"] >= 0.0).all(), "Negative speed detected"
        assert (df["lat"] >= -90.0).all() and (df["lat"] <= 90.0).all(), "Invalid latitude"
        assert (df["lon"] >= -180.0).all() and (df["lon"] <= 180.0).all(), "Invalid longitude"

        print(f"  [PASS] Scenario {s_id}: Telemetry values within verified bounds [Fuel: 0-100%, Battery: 0-100%, No NaNs]")

def run_api_endpoints_matrix():
    print("\n============================================================")
    print("3. FASTAPI ENDPOINTS MATRIX (ALL SCENARIOS 1-5)")
    print("============================================================")
    
    # Health check
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    print("  [PASS] GET /api/v1/health -> 200 OK")

    # Scenarios list
    res = client.get("/api/v1/scenarios")
    assert res.status_code == 200 and len(res.json()["scenarios"]) == 5
    print("  [PASS] GET /api/v1/scenarios -> 200 OK (5 scenarios)")

    core_endpoints = [
        "/api/v1/dashboard/summary",
        "/api/v1/assets",
        "/api/v1/personnel",
        "/api/v1/cargo",
        "/api/v1/inventory",
        "/api/v1/emergencies",
        "/api/v1/connectivity",
        "/api/v1/alerts",
        "/api/v1/map/topology"
    ]

    intel_endpoints = [
        "/api/v1/intelligence/summary",
        "/api/v1/intelligence/autonomy",
        "/api/v1/intelligence/resupply-risk",
        "/api/v1/intelligence/readiness",
        "/api/v1/intelligence/emergency",
        "/api/v1/intelligence/forecast"
    ]

    for s_id in range(1, 6):
        # Scenario summary
        res = client.get(f"/api/v1/scenarios/{s_id}/summary")
        assert res.status_code == 200, f"Failed summary for {s_id}"

        # Core APIs
        for ep in core_endpoints:
            res = client.get(f"{ep}?scenario_id={s_id}")
            assert res.status_code == 200, f"Failed {ep} for scenario {s_id}: {res.status_code}"

        # Intel APIs
        for ep in intel_endpoints:
            res = client.get(f"{ep}?scenario_id={s_id}")
            assert res.status_code == 200, f"Failed {ep} for scenario {s_id}: {res.status_code}"

        print(f"  [PASS] Scenario {s_id}: 16 endpoints verified -> 100% HTTP 200 OK")

def run_sync_api_audit():
    print("\n============================================================")
    print("4. SYNC API MATRIX: Valid, Invalid, Unsupported & Malformed")
    print("============================================================")

    # 1. Empty operations batch
    res = client.post("/api/v1/sync", json={"operations": []})
    assert res.status_code == 200
    assert len(res.json()["accepted"]) == 0
    print("  [PASS] Empty operations sync: 200 OK")

    # 2. Valid operations batch (Personnel, Cargo, Asset)
    valid_payload = {
        "operations": [
            {
                "id": "op-p1",
                "resource": "personnel",
                "operation": "UPDATE_CHECKIN",
                "payload": {"personnel_id": "PERS-003", "status": "UNCONFIRMED"},
                "timestamp": "2026-09-20T11:00:00Z"
            },
            {
                "id": "op-c1",
                "resource": "cargo",
                "operation": "UPDATE_STAGE",
                "payload": {"cargo_id": "CRG-BIO-01", "stage": "INSPECTED"},
                "timestamp": "2026-09-20T11:00:00Z"
            },
            {
                "id": "op-a1",
                "resource": "assets",
                "operation": "UPDATE_STATUS",
                "payload": {"asset_id": "VEH-01", "status": "IN_MISSION"},
                "timestamp": "2026-09-20T11:00:00Z"
            }
        ]
    }
    res = client.post("/api/v1/sync", json=valid_payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["accepted"]) == 3
    assert len(data["rejected"]) == 0
    print("  [PASS] Valid operations sync: 3 accepted, 0 rejected -> 200 OK")

    # 3. Unsupported resource & operation
    unsupported_payload = {
        "operations": [
            {
                "id": "op-bad1",
                "resource": "satellite_modem",
                "operation": "REBOOT",
                "payload": {},
                "timestamp": "2026-09-20T11:00:00Z"
            },
            {
                "id": "op-bad2",
                "resource": "personnel",
                "operation": "DELETE_USER",
                "payload": {"personnel_id": "PERS-001"},
                "timestamp": "2026-09-20T11:00:00Z"
            }
        ]
    }
    res = client.post("/api/v1/sync", json=unsupported_payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["accepted"]) == 0
    assert len(data["rejected"]) == 2
    assert "Unsupported resource" in data["rejected"][0]["message"]
    assert "Unsupported operation" in data["rejected"][1]["message"]
    print("  [PASS] Unsupported operations safely rejected -> 200 OK")

    # 4. Malformed missing payload fields
    missing_fields_payload = {
        "operations": [
            {
                "id": "op-bad3",
                "resource": "personnel",
                "operation": "UPDATE_CHECKIN",
                "payload": {},  # missing personnel_id
                "timestamp": "2026-09-20T11:00:00Z"
            }
        ]
    }
    res = client.post("/api/v1/sync", json=missing_fields_payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["rejected"]) == 1
    assert "missing required field" in data["rejected"][0]["message"].lower()
    print("  [PASS] Malformed payload safely rejected -> 200 OK")

def run_error_handling_audit():
    print("\n============================================================")
    print("5. ERROR HANDLING & BOUNDARY VALIDATION")
    print("============================================================")
    
    # Invalid scenario ID
    res = client.get("/api/v1/scenarios/99/summary")
    assert res.status_code in [400, 404, 422]
    print("  [PASS] Invalid scenario ID (99): Handled gracefully with error response")

    res = client.get("/api/v1/dashboard/summary?scenario_id=0")
    assert res.status_code == 422  # FastApi validation error (ge=1)
    print("  [PASS] Out of bounds scenario ID (0): Pydantic 422 validation error")

    res = client.get("/api/v1/intelligence/autonomy?scenario_id=6")
    assert res.status_code == 422  # Pydantic validation error (le=5)
    print("  [PASS] Out of bounds scenario ID (6): Pydantic 422 validation error")

if __name__ == "__main__":
    run_determinism_audit()
    run_telemetry_data_integrity_audit()
    run_api_endpoints_matrix()
    run_sync_api_audit()
    run_error_handling_audit()
    print("\n============================================================")
    print("ALL AUDITS & INTEGRATION CHECKS PASSED (100%)!")
    print("============================================================")
