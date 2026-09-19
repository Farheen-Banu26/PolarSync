from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertCategory(str, Enum):
    INVENTORY = "INVENTORY"
    CARGO = "CARGO"
    PERSONNEL = "PERSONNEL"
    EMERGENCY = "EMERGENCY"
    CONNECTIVITY = "CONNECTIVITY"
    FLEET = "FLEET"


@dataclass
class Alert:
    id: str
    tick: int
    category: AlertCategory
    severity: AlertSeverity
    title: str
    message: str
    source_entity_id: str
    acknowledged: bool = False
