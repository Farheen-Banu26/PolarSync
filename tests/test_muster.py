import pytest
from src.models.personnel import Personnel, PersonnelRole, PersonnelStatus, MovementStatus
from src.decision_support.muster_manager import MusterManager


def test_automatic_muster_triage():
    personnel = {
        "P1": Personnel(id="P1", name="Commander", role=PersonnelRole.STATION_COMMANDER, assigned_location_id="BASE", current_position=(-69.75, 39.58), movement_status=MovementStatus.STATIONARY),
        "P2": Personnel(id="P2", name="Medic", role=PersonnelRole.MEDIC, assigned_location_id="BASE", current_position=(-69.75, 39.58), movement_status=MovementStatus.STATIONARY),
        "P3": Personnel(id="P3", name="Field Geo", role=PersonnelRole.FIELD_SCIENTIST, assigned_location_id="CAMP-ZULU", current_position=(-70.12, 39.85), movement_status=MovementStatus.ON_FOOT_TRANSIT),
        "P4": Personnel(id="P4", name="Field Bio", role=PersonnelRole.FIELD_SCIENTIST, assigned_location_id="CAMP-ZULU", current_position=(-70.12, 39.85), movement_status=MovementStatus.ON_FOOT_TRANSIT)
    }

    # Routine muster
    report = MusterManager.perform_muster(personnel)
    assert report.total_expected == 4
    assert report.checked_in_count == 2
    assert report.field_count == 2
    assert report.unconfirmed_count == 0

    # Emergency muster affecting P3 and P4
    report_emg = MusterManager.perform_muster(personnel, emergency_affected_ids=["P3", "P4"])
    assert report_emg.total_expected == 4
    assert report_emg.affected_count == 2
    assert report_emg.unconfirmed_count == 2
    assert any(u["id"] == "P3" for u in report_emg.unconfirmed_personnel)
