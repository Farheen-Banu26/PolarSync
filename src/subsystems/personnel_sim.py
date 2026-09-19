from typing import Dict
from ..models.personnel import Personnel, PersonnelStatus, MovementStatus
from ..models.vehicle import Vehicle


class PersonnelSubsystem:
    def step(
        self,
        personnel: Dict[str, Personnel],
        vehicles: Dict[str, Vehicle],
        current_tick: int
    ):
        for p in personnel.values():
            # If personnel is inside an assigned vehicle, mirror vehicle position & movement
            if p.assigned_vehicle_id and p.assigned_vehicle_id in vehicles:
                veh = vehicles[p.assigned_vehicle_id]
                p.current_position = veh.position
                if veh.status.value in ("IN_TRANSIT", "DISPATCHED_EMERGENCY"):
                    p.movement_status = MovementStatus.IN_VEHICLE
                else:
                    p.movement_status = MovementStatus.STATIONARY

            # If heartbeat is active and not affected by emergency, maintain periodic checkin
            if p.heartbeat_active and p.status != PersonnelStatus.AFFECTED_EMERGENCY:
                if (current_tick - p.last_checkin_tick) >= p.checkin_interval_ticks:
                    p.last_checkin_tick = current_tick
                    p.status = PersonnelStatus.CHECKED_IN
            else:
                # Check if overdue
                if p.is_checkin_overdue(current_tick) and p.status not in (
                    PersonnelStatus.AFFECTED_EMERGENCY,
                    PersonnelStatus.EVACUATED
                ):
                    p.status = PersonnelStatus.UNCONFIRMED_DUE
