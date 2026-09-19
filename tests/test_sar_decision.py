import pytest
from src.models.vehicle import Vehicle, VehicleType, VehicleStatus, VehicleCapability, ConnectivityStatus
from src.models.emergency import EmergencyIncident, EmergencySeverity
from src.decision_support.sar_selector import SARAssetSelector


def test_sar_asset_selection_eligibility_and_explanation():
    # Base location: -69.75, 39.58
    # Emergency location: -69.95, 39.70 (~22.7 km away)
    emergency = EmergencyIncident(
        id="EMG-TEST-01",
        incident_type="CREVASSE_FALL",
        location=(-69.9500, 39.7000),
        nearest_landmark="Crevasse Field C-3",
        severity=EmergencySeverity.CRITICAL,
        affected_personnel_ids=["PERS-003"],
        timestamp_tick=10,
        required_capabilities=[VehicleCapability.MEDICAL_TRANSPORT, VehicleCapability.AERIAL]
    )

    vehicles = {
        # Eligible helicopter
        "HELI-01": Vehicle(
            id="HELI-01",
            name="Bell-412 Polar Air",
            vehicle_type=VehicleType.HELICOPTER,
            position=(-69.7500, 39.5800),
            fuel_level_l=600.0,
            fuel_capacity_l=700.0,
            fuel_burn_rate_l_per_km=1.8,
            status=VehicleStatus.AVAILABLE,
            capabilities={VehicleCapability.AERIAL, VehicleCapability.MEDICAL_TRANSPORT, VehicleCapability.RAPID_RESPONSE}
        ),
        # Lacks AERIAL capability
        "VEH-01": Vehicle(
            id="VEH-01",
            name="Snowcat Alpha",
            vehicle_type=VehicleType.SNOWCAT,
            position=(-69.7500, 39.5800),
            fuel_level_l=200.0,
            fuel_capacity_l=250.0,
            fuel_burn_rate_l_per_km=0.85,
            status=VehicleStatus.AVAILABLE,
            capabilities={VehicleCapability.MEDICAL_TRANSPORT}
        ),
        # Has capability but is already in maintenance
        "HELI-02": Vehicle(
            id="HELI-02",
            name="Helicopter Bravo",
            vehicle_type=VehicleType.HELICOPTER,
            position=(-69.7500, 39.5800),
            fuel_level_l=500.0,
            fuel_capacity_l=700.0,
            fuel_burn_rate_l_per_km=1.8,
            status=VehicleStatus.MAINTENANCE,
            capabilities={VehicleCapability.AERIAL, VehicleCapability.MEDICAL_TRANSPORT}
        )
    }

    result = SARAssetSelector.evaluate_and_select(emergency, vehicles)
    assert result.selected_vehicle_id == "HELI-01"
    assert "Selected" in result.decision_summary
    
    # Check explanations
    eval_map = {e.vehicle_id: e for e in result.evaluations}
    assert eval_map["HELI-01"].is_eligible is True
    assert eval_map["VEH-01"].is_eligible is False
    assert any("Lacks capability AERIAL" in r for r in eval_map["VEH-01"].disqualification_reasons)
    assert eval_map["HELI-02"].is_eligible is False
    assert any("Status is MAINTENANCE" in r for r in eval_map["HELI-02"].disqualification_reasons)
