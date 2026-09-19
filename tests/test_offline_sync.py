import pytest
from src.core.events import EventBus
from src.models.vehicle import ConnectivityStatus
from src.subsystems.connectivity_sim import ConnectivitySubsystem


def test_offline_queue_buffering_and_reconciliation():
    bus = EventBus()
    subsystem = ConnectivitySubsystem(bus)
    local_queue = []

    # 1. Switch to OFFLINE
    status, local_queue, logs = subsystem.set_connectivity(
        current_status=ConnectivityStatus.ONLINE,
        new_status=ConnectivityStatus.OFFLINE,
        current_tick=10,
        local_queue=local_queue
    )
    assert status == ConnectivityStatus.OFFLINE
    assert len(logs) == 1

    # 2. Buffer 5 events during offline operation
    for i in range(5):
        subsystem.buffer_event(local_queue, {"tick": 10 + i, "data": f"telemetry_{i}"})
    
    assert len(local_queue) == 5

    # 3. Restore to ONLINE
    status, local_queue, logs = subsystem.set_connectivity(
        current_status=ConnectivityStatus.OFFLINE,
        new_status=ConnectivityStatus.ONLINE,
        current_tick=25,
        local_queue=local_queue
    )
    assert status == ConnectivityStatus.ONLINE
    assert len(local_queue) == 0  # Queue flushed / reconciled
    assert any("Synchronizing 5 queued events" in log for log in logs)
