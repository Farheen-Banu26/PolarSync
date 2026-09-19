from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List


class EventType(str, Enum):
    TICK_COMPLETED = "TICK_COMPLETED"
    VEHICLE_DISPATCHED = "VEHICLE_DISPATCHED"
    VEHICLE_ARRIVED = "VEHICLE_ARRIVED"
    EMERGENCY_TRIGGERED = "EMERGENCY_TRIGGERED"
    MUSTER_CALLED = "MUSTER_CALLED"
    ALERT_GENERATED = "ALERT_GENERATED"
    CARGO_STAGE_CHANGED = "CARGO_STAGE_CHANGED"
    CARGO_BREACH_DETECTED = "CARGO_BREACH_DETECTED"
    CONNECTIVITY_LOST = "CONNECTIVITY_LOST"
    CONNECTIVITY_RESTORED = "CONNECTIVITY_RESTORED"
    SYNC_COMPLETED = "SYNC_COMPLETED"


@dataclass
class Event:
    event_type: EventType
    tick: int
    payload: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable[[Event], None]]] = {
            et: [] for et in EventType
        }
        self.history: List[Event] = []

    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        if event_type in self._listeners:
            self._listeners[event_type].append(callback)

    def publish(self, event: Event):
        self.history.append(event)
        for callback in self._listeners.get(event.event_type, []):
            try:
                callback(event)
            except Exception as e:
                # Log or handle listener error gracefully
                pass

    def clear(self):
        self.history.clear()
