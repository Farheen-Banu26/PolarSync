import pytest
from src.models.cargo import CargoItem, CargoCategory, CargoLifecycleStage, CargoCondition


def test_cargo_stage_progression():
    cargo = CargoItem(
        id="CRG-01",
        name="Seismic Logger",
        category=CargoCategory.SCIENTIFIC_EQUIPMENT,
        weight_kg=50.0,
        origin_id="BASE-MAITRI",
        destination_id="CAMP-ALPHA",
        lifecycle_stage=CargoLifecycleStage.PACKED
    )
    assert cargo.lifecycle_stage == CargoLifecycleStage.PACKED
    
    cargo.advance_stage()
    assert cargo.lifecycle_stage == CargoLifecycleStage.QC

    cargo.advance_stage()
    assert cargo.lifecycle_stage == CargoLifecycleStage.LOADED

    cargo.advance_stage()
    assert cargo.lifecycle_stage == CargoLifecycleStage.IN_TRANSIT

    cargo.advance_stage()
    assert cargo.lifecycle_stage == CargoLifecycleStage.ARRIVED

    cargo.advance_stage()
    assert cargo.lifecycle_stage == CargoLifecycleStage.INSPECTED

    cargo.advance_stage()
    assert cargo.lifecycle_stage == CargoLifecycleStage.DELIVERED


def test_cargo_thermal_breach_detection():
    cargo = CargoItem(
        id="CRG-BIO",
        name="Microbial Culture",
        category=CargoCategory.MEDICAL_SAMPLES,
        weight_kg=10.0,
        origin_id="CAMP-ZULU",
        destination_id="BASE-MAITRI",
        is_temperature_sensitive=True,
        min_temp_c=-25.0,
        max_temp_c=-15.0,
        current_temp_c=-20.0
    )
    assert cargo.check_thermal_status() == CargoCondition.NOMINAL

    # Warning drift near threshold
    cargo.current_temp_c = -14.5
    assert cargo.check_thermal_status() == CargoCondition.BREACHED_DAMAGED

    cargo.current_temp_c = -16.0
    assert cargo.check_thermal_status() == CargoCondition.WARNING_DRIFT
