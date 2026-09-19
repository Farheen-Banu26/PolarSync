from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from ..models.vehicle import Vehicle, VehicleStatus, VehicleCapability, VehicleType
from ..models.emergency import EmergencyIncident, EmergencySeverity
from ..utils.geo import haversine_distance_km


@dataclass
class AssetEvaluation:
    vehicle_id: str
    vehicle_name: str
    vehicle_type: str
    is_eligible: bool
    disqualification_reasons: List[str] = field(default_factory=list)
    distance_km: float = 0.0
    estimated_transit_time_min: float = 0.0
    fuel_remaining_pct: float = 0.0
    fuel_after_mission_pct: float = 0.0
    matched_capabilities: List[str] = field(default_factory=list)
    score: float = 0.0
    explanation_points: List[str] = field(default_factory=list)


@dataclass
class SARSelectionResult:
    emergency_id: str
    selected_vehicle_id: Optional[str]
    selected_vehicle_name: Optional[str]
    evaluations: List[AssetEvaluation] = field(default_factory=list)
    decision_summary: str = ""

    def formatted_explanation(self) -> str:
        lines = [
            "=" * 60,
            f"DECISION SUPPORT: EMERGENCY RESPONSE ASSET SELECTION",
            f"Emergency ID : {self.emergency_id}",
            "=" * 60,
        ]
        if not self.selected_vehicle_id:
            lines.append("NO ELIGIBLE ASSET FOUND FOR DISPATCH.")
            for ev in self.evaluations:
                lines.append(f" - {ev.vehicle_name} ({ev.vehicle_id}): DISQUALIFIED -> {', '.join(ev.disqualification_reasons)}")
            lines.append("=" * 60)
            return "\n".join(lines)

        lines.append(f"RECOMMENDED ASSET: {self.selected_vehicle_name} ({self.selected_vehicle_id})")
        lines.append("SELECTION RATIONALE:")
        
        # Find winning eval
        winning_eval = next((e for e in self.evaluations if e.vehicle_id == self.selected_vehicle_id), None)
        if winning_eval:
            for pt in winning_eval.explanation_points:
                lines.append(f"  [OK] {pt}")
        
        lines.append("-" * 60)
        lines.append("FLEET EVALUATION COMPARISON:")
        for ev in self.evaluations:
            status_str = f"Score {ev.score:.1f}/100" if ev.is_eligible else f"DISQUALIFIED ({', '.join(ev.disqualification_reasons)})"
            lines.append(f" - {ev.vehicle_name:18s} | Dist: {ev.distance_km:5.1f}km | ETA: {ev.estimated_transit_time_min:4.0f}m | Fuel: {ev.fuel_remaining_pct:3.0f}% | {status_str}")
        lines.append("=" * 60)
        return "\n".join(lines)


class SARAssetSelector:
    @staticmethod
    def evaluate_and_select(
        emergency: EmergencyIncident,
        vehicles: Dict[str, Vehicle]
    ) -> SARSelectionResult:
        evaluations: List[AssetEvaluation] = []

        nominal_speed = {
            VehicleType.HELICOPTER: 180.0,
            VehicleType.SKIDOO: 45.0,
            VehicleType.SNOWCAT: 25.0,
            VehicleType.PISTON_BULLY: 20.0
        }

        for veh in vehicles.values():
            dist_km = haversine_distance_km(veh.position, emergency.location)
            speed = nominal_speed.get(veh.vehicle_type, 30.0)
            eta_mins = (dist_km / speed) * 60.0
            
            # Fuel required for round trip + 25% safety buffer
            round_trip_km = dist_km * 2.0
            fuel_needed_l = round_trip_km * veh.fuel_burn_rate_l_per_km * 1.25
            fuel_remaining_after_l = veh.fuel_level_l - fuel_needed_l
            fuel_after_pct = (fuel_remaining_after_l / veh.fuel_capacity_l) * 100.0 if veh.fuel_capacity_l > 0 else 0.0

            disqualifications = []
            
            # 1. Availability check
            if veh.status != VehicleStatus.AVAILABLE:
                disqualifications.append(f"Status is {veh.status.value}")

            # 2. Connectivity check
            if veh.connectivity.value == "OFFLINE":
                disqualifications.append("Vehicle offline")

            # 3. Capability match check
            matched_caps = []
            for req_cap in emergency.required_capabilities:
                if veh.has_capability(req_cap):
                    matched_caps.append(req_cap.value)
                else:
                    disqualifications.append(f"Lacks capability {req_cap.value}")

            # 4. Fuel & range check
            if veh.fuel_level_l < fuel_needed_l:
                disqualifications.append(f"Insufficient fuel for round trip ({veh.fuel_level_l:.1f}L < {fuel_needed_l:.1f}L needed)")

            is_eligible = (len(disqualifications) == 0)

            # Scoring formula for eligible assets
            # Higher score for faster ETA, higher remaining fuel, capability match
            score = 0.0
            explanation_points = []
            if is_eligible:
                # ETA component (0 - 40 pts)
                eta_score = max(0.0, 40.0 * (1.0 - min(1.0, eta_mins / 120.0)))
                # Fuel reserve component (0 - 30 pts)
                fuel_score = 30.0 * (max(0.0, fuel_after_pct) / 100.0)
                # Capability / Readiness component (30 pts)
                cap_score = 30.0
                score = round(eta_score + fuel_score + cap_score, 1)

                explanation_points.append(f"Required capabilities matched: {', '.join(matched_caps) if matched_caps else 'General Transport'}")
                explanation_points.append(f"Sufficient fuel reserve: {veh.fuel_pct:.1f}% currently -> {fuel_after_pct:.1f}% estimated post-mission")
                explanation_points.append(f"Asset is available on standby at distance {dist_km:.1f} km")
                explanation_points.append(f"Estimated response transit time (ETA): {eta_mins:.0f} minutes")
                if emergency.severity == EmergencySeverity.CRITICAL and veh.vehicle_type == VehicleType.HELICOPTER:
                    explanation_points.append("Helicopter prioritised for CRITICAL severity rapid aerial evacuation")

            evaluations.append(AssetEvaluation(
                vehicle_id=veh.id,
                vehicle_name=veh.name,
                vehicle_type=veh.vehicle_type.value,
                is_eligible=is_eligible,
                disqualification_reasons=disqualifications,
                distance_km=round(dist_km, 2),
                estimated_transit_time_min=round(eta_mins, 1),
                fuel_remaining_pct=round(veh.fuel_pct, 1),
                fuel_after_mission_pct=round(max(0.0, fuel_after_pct), 1),
                matched_capabilities=matched_caps,
                score=score,
                explanation_points=explanation_points
            ))

        # Select highest scoring eligible asset
        eligible = [e for e in evaluations if e.is_eligible]
        if eligible:
            eligible.sort(key=lambda x: x.score, reverse=True)
            winner = eligible[0]
            return SARSelectionResult(
                emergency_id=emergency.id,
                selected_vehicle_id=winner.vehicle_id,
                selected_vehicle_name=winner.vehicle_name,
                evaluations=evaluations,
                decision_summary=f"Selected {winner.vehicle_name} ({winner.vehicle_id}) with composite suitability score {winner.score:.1f}/100"
            )
        else:
            return SARSelectionResult(
                emergency_id=emergency.id,
                selected_vehicle_id=None,
                selected_vehicle_name=None,
                evaluations=evaluations,
                decision_summary="No available asset meets the range and capability criteria."
            )
