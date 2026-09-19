from typing import List, Dict, Any, Tuple
from ..models.vehicle import ConnectivityStatus
from ..core.events import EventBus, Event, EventType


class ConnectivitySubsystem:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus

    def buffer_event(
        self,
        local_queue: List[Dict[str, Any]],
        event_dict: Dict[str, Any]
    ):
        """
        Store an event locally when offline.
        """
        local_queue.append(event_dict)

    def set_connectivity(
        self,
        current_status: ConnectivityStatus,
        new_status: ConnectivityStatus,
        current_tick: int,
        local_queue: List[Dict[str, Any]]
    ) -> Tuple[ConnectivityStatus, List[Dict[str, Any]], List[str]]:
        """
        Handles state transitions between ONLINE and OFFLINE.
        Returns: (new_status, updated_queue, sync_logs)
        """
        sync_logs = []
        if current_status == ConnectivityStatus.ONLINE and new_status == ConnectivityStatus.OFFLINE:
            self.event_bus.publish(Event(
                event_type=EventType.CONNECTIVITY_LOST,
                tick=current_tick,
                payload={"message": "Network link severed. Switching to local offline event buffer."}
            ))
            sync_logs.append(f"[TICK {current_tick}] Link LOST: Entering OFFLINE mode. Local queue activated.")

        elif current_status == ConnectivityStatus.OFFLINE and new_status == ConnectivityStatus.ONLINE:
            queued_count = len(local_queue)
            sync_logs.append(f"[TICK {current_tick}] Link RESTORED: Reconnected. Synchronizing {queued_count} queued events...")
            
            # Replay / flush queue
            local_queue.clear()
            
            self.event_bus.publish(Event(
                event_type=EventType.SYNC_COMPLETED,
                tick=current_tick,
                payload={"synchronized_events_count": queued_count}
            ))
            sync_logs.append(f"[TICK {current_tick}] Synchronization COMPLETED. Local queue flushed (0 remaining).")

        return new_status, local_queue, sync_logs
