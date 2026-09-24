"""
PolarSync Audit Log Service
Records operator interventions, automated triggers, SAR actions, and synchronization events.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger("polarsync.audit")


class AuditService:
    def __init__(self):
        self._memory_logs: List[Dict[str, Any]] = [
            {
                "id": 1,
                "operator": "SYSTEM",
                "role": "Smart Automation",
                "action": "ENGINE_INITIALIZED",
                "entity_type": "KERNEL",
                "entity_id": "SYS-INIT",
                "details": {"status": "Deterministic Simulation Kernel Active", "scenarios_ready": 5},
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "operator": "COMMANDER (Dr. Sharma)",
                "role": "Expedition Commander",
                "action": "EXPEDITION_MONITOR_START",
                "entity_type": "EXPEDITION",
                "entity_id": "EXP-2026-M2",
                "details": {"mission": "Maitri-II to Camp Alpha Logistics Resupply", "sector": "Queen Maud Land"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
        self._next_id = 3

    def log_action(
        self,
        operator: str,
        role: str,
        action: str,
        entity_type: str,
        entity_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        entry = {
            "id": self._next_id,
            "operator": operator,
            "role": role,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self._next_id += 1
        self._memory_logs.insert(0, entry)  # Prepend newest
        logger.info(f"[AUDIT] {role} '{operator}' -> {action} on {entity_type}:{entity_id}")
        return entry

    def get_logs(self, limit: int = 50, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        if entity_type:
            filtered = [log for log in self._memory_logs if log["entity_type"].upper() == entity_type.upper()]
            return filtered[:limit]
        return self._memory_logs[:limit]


audit_service = AuditService()
