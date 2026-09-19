from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from ..models.personnel import Personnel, PersonnelStatus, MovementStatus


@dataclass
class MusterReport:
    total_expected: int
    checked_in_count: int
    field_count: int
    unconfirmed_count: int
    affected_count: int
    checked_in_personnel: List[str] = field(default_factory=list)
    field_personnel: List[str] = field(default_factory=list)
    unconfirmed_personnel: List[Dict[str, str]] = field(default_factory=list)
    affected_personnel: List[str] = field(default_factory=list)

    def summary_text(self) -> str:
        lines = [
            "=" * 60,
            "AUTOMATIC MUSTER ROLL-CALL REPORT",
            "=" * 60,
            f"Total Personnel Expected : {self.total_expected}",
            f"Base / Checked-in       : {self.checked_in_count}",
            f"Field Operations         : {self.field_count}",
            f"Unconfirmed / Missing    : {self.unconfirmed_count}",
            f"Directly Affected        : {self.affected_count}",
            "-" * 60,
        ]
        if self.unconfirmed_personnel:
            lines.append("UNCONFIRMED PERSONNEL DETAILS:")
            for item in self.unconfirmed_personnel:
                lines.append(
                    f" - {item['id']} ({item['name']} - {item['role']}): "
                    f"Last Loc {item['last_location']} | Last Check-in: Tick {item['last_checkin_tick']}"
                )
        else:
            lines.append("ALL PERSONNEL ACCOUNTED FOR.")
        lines.append("=" * 60)
        return "\n".join(lines)


class MusterManager:
    @staticmethod
    def perform_muster(personnel: Dict[str, Personnel], emergency_affected_ids: List[str] = None) -> MusterReport:
        if emergency_affected_ids is None:
            emergency_affected_ids = []

        total = len(personnel)
        checked_in = []
        field_team = []
        unconfirmed = []
        affected = []

        for p in personnel.values():
            if p.id in emergency_affected_ids or p.status == PersonnelStatus.AFFECTED_EMERGENCY:
                affected.append(p.id)
                # An affected person whose heartbeat is lost is also flagged in muster
                unconfirmed.append({
                    "id": p.id,
                    "name": p.name,
                    "role": p.role.value,
                    "last_location": f"({p.current_position[0]:.4f}, {p.current_position[1]:.4f})",
                    "last_checkin_tick": str(p.last_checkin_tick)
                })
            elif p.status == PersonnelStatus.UNCONFIRMED_DUE or not p.heartbeat_active:
                unconfirmed.append({
                    "id": p.id,
                    "name": p.name,
                    "role": p.role.value,
                    "last_location": f"({p.current_position[0]:.4f}, {p.current_position[1]:.4f})",
                    "last_checkin_tick": str(p.last_checkin_tick)
                })
            elif p.movement_status in (MovementStatus.ON_FOOT_TRANSIT, MovementStatus.IN_VEHICLE):
                field_team.append(p.id)
            else:
                checked_in.append(p.id)

        return MusterReport(
            total_expected=total,
            checked_in_count=len(checked_in),
            field_count=len(field_team),
            unconfirmed_count=len(unconfirmed),
            affected_count=len(affected),
            checked_in_personnel=checked_in,
            field_personnel=field_team,
            unconfirmed_personnel=unconfirmed,
            affected_personnel=affected
        )
