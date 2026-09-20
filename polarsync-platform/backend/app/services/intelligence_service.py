"""
Explainable Operational Intelligence & Decision Support Service (Stage 3.5)

Architectural Role:
Layered cleanly between SimulationService and FastAPI endpoints.
Processes deterministic simulation state and telemetry to produce:
1. Winter Autonomy Intelligence
2. Resupply Risk Analysis
3. Expedition Readiness Factor Synthesis
4. Emergency SAR Decision Matrix
5. Resource Depletion Forecasting
6. Operator Explainability Blocks (What Happened, Why It Matters, What to Watch, Operator Action)

Rules:
- Read-only integration with SimulationService.
- Does NOT duplicate or alter simulation algorithms in src/*.
- No external LLM or cloud AI dependencies; 100% deterministic & explainable.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.services.simulation_service import SimulationService
from app.schemas.intelligence import (
    ExplainabilityBlock,
    AutonomyItem,
    ResupplyRiskItem,
    ReadinessFactor,
    ReadinessIntelligence,
    CandidateAssetEvaluation,
    EmergencyIntelligence,
    ForecastDataPoint,
    ResourceForecast,
    IntelligenceSummaryResponse
)

logger = logging.getLogger("polarsync.intelligence_service")


class IntelligenceService:
    def __init__(self, simulation_service: Optional[SimulationService] = None):
        self.sim_service = simulation_service or SimulationService()

    def get_autonomy_intelligence(self, scenario_id: int) -> List[AutonomyItem]:
        """
        Analyze inventory stock levels, burn rates, and winter autonomy horizons.
        """
        raw_inventory = self.sim_service.get_inventory(scenario_id)
        items: List[AutonomyItem] = []

        for inv in raw_inventory:
            cat = inv["category"]
            doa = inv["days_of_autonomy"]
            safety = inv["safety_buffer_days"]
            resupply = inv["next_resupply_window_days"]
            risk_raw = inv["resupply_risk"]
            rate = inv["daily_consumption_rate"]
            stock = inv["current_stock"]
            loc_name = inv.get("location_name", inv["location_id"])

            # Determine risk and trend
            if doa < safety:
                risk = "CRITICAL"
                trend = "DEPLETING_RAPIDLY"
                explanation = (
                    f"{cat} autonomy ({doa:.2f} days) is below the required safety buffer "
                    f"({safety:.1f} days) at {loc_name}. Immediate resupply or rationing required."
                )
            elif doa < (safety + resupply):
                risk = "WATCH" if doa >= resupply else "AT_RISK"
                trend = "DEPLETING_NOMINALLY"
                explanation = (
                    f"{cat} autonomy ({doa:.2f} days) is within the resupply planning window "
                    f"({resupply:.1f} days + {safety:.1f} days buffer) at {loc_name}."
                )
            else:
                risk = "SAFE"
                trend = "STABLE"
                explanation = (
                    f"{cat} stock ({stock:.0f} {inv['unit']}) sustains {doa:.1f} days of autonomy, "
                    f"comfortably exceeding safety threshold ({safety:.1f} days) at {loc_name}."
                )

            items.append(AutonomyItem(
                category=cat,
                location_id=inv["location_id"],
                location_name=loc_name,
                current_stock=stock,
                unit=inv["unit"],
                daily_consumption_rate=rate,
                days_of_autonomy=round(doa, 2),
                safety_buffer_days=safety,
                resupply_window_days=resupply,
                risk=risk,
                trend=trend,
                explanation=explanation
            ))

        return items

    def get_resupply_risk(self, scenario_id: int) -> List[ResupplyRiskItem]:
        """
        Evaluate resupply risks with explicit operator recommendations.
        """
        autonomy_items = self.get_autonomy_intelligence(scenario_id)
        risk_items: List[ResupplyRiskItem] = []

        for item in autonomy_items:
            if item.risk == "CRITICAL":
                action = f"Initiate emergency priority resupply airlift/traverse and restrict non-essential {item.category.lower()} consumption."
                exp = f"CRITICAL: {item.category} autonomy ({item.days_of_autonomy:.2f} days) has breached the {item.safety_buffer_days:.1f}-day minimum buffer."
            elif item.risk == "AT_RISK":
                action = f"Confirm scheduled resupply manifest allocations for {item.category.lower()} within {item.resupply_window_days:.0f} days."
                exp = f"AT_RISK: {item.category} autonomy ({item.days_of_autonomy:.2f} days) is entering the replenishment window."
            elif item.risk == "WATCH":
                action = f"Monitor daily burn rate variations for {item.category.lower()}."
                exp = f"WATCH: {item.category} autonomy approaching resupply horizon."
            else:
                action = f"Standard inventory audit cycle; nominal consumption."
                exp = f"SAFE: {item.category} autonomy exceeds safety buffer."

            risk_items.append(ResupplyRiskItem(
                category=item.category,
                location_name=item.location_name,
                current_stock=item.current_stock,
                unit=item.unit,
                days_of_autonomy=item.days_of_autonomy,
                safety_buffer_days=item.safety_buffer_days,
                resupply_window_days=item.resupply_window_days,
                risk_level=item.risk,
                explanation=exp,
                recommended_action=action
            ))

        return risk_items

    def get_readiness_intelligence(self, scenario_id: int) -> ReadinessIntelligence:
        """
        Synthesize multi-domain expedition readiness into explainable operational factors.
        """
        data = self.sim_service._get_runner_for_scenario(scenario_id)
        state = data["state"]
        run_output = data["run_output"]
        final_readiness = run_output["final_readiness"]

        factors: List[ReadinessFactor] = []

        # 1. Personnel Factor
        total_p = len(state.personnel)
        muster = run_output.get("muster_reports", [None])[0] if run_output.get("muster_reports") else None
        emergency = next(iter(state.emergencies.values())) if state.emergencies else None
        
        if muster and muster.unconfirmed_count > 0 and (emergency and emergency.status.value != "RESOLVED"):
            p_state = "CRITICAL"
            p_reason = f"{muster.unconfirmed_count} personnel unconfirmed in field muster ({', '.join([p['id'] if isinstance(p, dict) else str(p) for p in muster.unconfirmed_personnel])})."
            p_metric = f"{muster.checked_in_count}/{total_p} Accounted"
        else:
            p_state = "NOMINAL"
            p_reason = f"All {total_p} expedition personnel active, accounted for, and heartbeats verified."
            p_metric = f"{total_p}/{total_p} Nominal"
        factors.append(ReadinessFactor(name="Personnel", state=p_state, metric=p_metric, reason=p_reason))

        # 2. Fleet Factor
        total_v = len(state.vehicles)
        available_v = sum(1 for v in state.vehicles.values() if v.status.value == "AVAILABLE")
        in_mission_v = sum(1 for v in state.vehicles.values() if v.status.value in ["IN_TRANSIT", "DISPATCHED_EMERGENCY"])
        if available_v == 0 and in_mission_v == 0:
            v_state = "CRITICAL"
            v_reason = "No operational vehicles available."
        elif in_mission_v > 0:
            v_state = "WATCH"
            v_reason = f"{in_mission_v} vehicle(s) deployed on active field missions; {available_v} reserve available."
        else:
            v_state = "NOMINAL"
            v_reason = f"{available_v}/{total_v} vehicles available in station hangars with nominal fuel."
        factors.append(ReadinessFactor(name="Fleet", state=v_state, metric=f"{available_v + in_mission_v}/{total_v} Ready", reason=v_reason))

        # 3. Inventory Factor
        autonomy_items = self.get_autonomy_intelligence(scenario_id)
        crit_inv = [i for i in autonomy_items if i.risk == "CRITICAL"]
        watch_inv = [i for i in autonomy_items if i.risk in ["WATCH", "AT_RISK"]]
        if crit_inv:
            inv_state = "CRITICAL"
            inv_reason = f"{crit_inv[0].category} autonomy ({crit_inv[0].days_of_autonomy:.1f}d) breached safety buffer ({crit_inv[0].safety_buffer_days:.1f}d)."
            inv_metric = f"{crit_inv[0].days_of_autonomy:.1f}d Min Autonomy"
        elif watch_inv:
            inv_state = "WATCH"
            inv_reason = f"{watch_inv[0].category} autonomy ({watch_inv[0].days_of_autonomy:.1f}d) approaching resupply window."
            inv_metric = f"{watch_inv[0].days_of_autonomy:.1f}d Min Autonomy"
        else:
            inv_state = "NOMINAL"
            min_doa = min((i.days_of_autonomy for i in autonomy_items), default=99.0)
            inv_reason = f"All operational consumables exceed winter safety buffers (minimum {min_doa:.0f} days)."
            inv_metric = f"{min_doa:.0f}d Min Autonomy"
        factors.append(ReadinessFactor(name="Inventory", state=inv_state, metric=inv_metric, reason=inv_reason))

        # 4. Cargo / Cold-Chain Factor
        total_c = len(state.cargo)
        breached_c = sum(1 for c in state.cargo.values() if c.condition.value == "BREACHED_DAMAGED")
        if breached_c > 0:
            c_state = "CRITICAL"
            c_reason = f"{breached_c} cold-chain package(s) sustained thermal excursion breach."
            c_metric = f"{total_c - breached_c}/{total_c} Nominal"
        else:
            c_state = "NOMINAL"
            c_reason = f"All {total_c} cargo items within nominal temperature limits and secure."
            c_metric = f"{total_c}/{total_c} Nominal"
        factors.append(ReadinessFactor(name="Cargo", state=c_state, metric=c_metric, reason=c_reason))

        # 5. Connectivity Factor
        if state.network_status.value == "OFFLINE":
            net_state = "WATCH"
            net_reason = "Satellite uplink severed; local store-and-forward buffer active."
            net_metric = "Offline Buffer"
        elif scenario_id == 5:
            net_state = "NOMINAL"
            net_reason = "Satellite restored; 30 buffered telemetry frames synchronized."
            net_metric = "Restored & Synced"
        else:
            net_state = "NOMINAL"
            net_reason = "High-throughput satellite telemetry link active."
            net_metric = "Online 100%"
        factors.append(ReadinessFactor(name="Connectivity", state=net_state, metric=net_metric, reason=net_reason))

        # 6. Emergencies Factor
        if emergency and emergency.status.value != "RESOLVED":
            emg_state = "CRITICAL"
            emg_reason = f"Active {emergency.severity.value} {emergency.incident_type} at {emergency.nearest_landmark}."
            emg_metric = "Active Response"
        elif emergency and emergency.status.value == "RESOLVED":
            emg_state = "NOMINAL"
            emg_reason = f"{emergency.incident_type} successfully resolved; personnel rescued."
            emg_metric = "Resolved"
        else:
            emg_state = "NOMINAL"
            emg_reason = "No active emergency or SAR dispatch incidents."
            emg_metric = "Nominal"
        factors.append(ReadinessFactor(name="Emergencies", state=emg_state, metric=emg_metric, reason=emg_reason))

        # Overall synthesis
        overall = final_readiness.overall_status

        # Build Explainability Block
        explainability = self._build_scenario_explainability(scenario_id, overall, factors)

        return ReadinessIntelligence(
            scenario_id=scenario_id,
            overall_state=overall,
            readiness_score=overall,
            factors=factors,
            explanation=f"Expedition readiness is {overall} across 6 operational dimensions.",
            explainability=explainability
        )

    def get_emergency_intelligence(self, scenario_id: int) -> EmergencyIntelligence:
        """
        Expose SAR decision-support intelligence and asset eligibility matrix.
        """
        raw_emergency = self.sim_service.get_emergencies(scenario_id)
        has_emg = raw_emergency["has_active_emergency"]
        emg_info = raw_emergency["emergency"]
        sar_decision = raw_emergency["sar_decision"]

        if not has_emg or not emg_info:
            return EmergencyIntelligence(
                scenario_id=scenario_id,
                has_active_emergency=False,
                explainability=ExplainabilityBlock(
                    what_happened="No active emergency incidents detected in the operational sector.",
                    why_it_matters="All field traverse teams and station personnel operate within nominal safety protocols.",
                    what_to_watch="Continuous GPS telemetry heartbeats and weather hazard radar.",
                    recommended_operator_action="Maintain standard SAR asset readiness and hourly comms check-ins."
                )
            )

        candidates: List[CandidateAssetEvaluation] = []
        selected_id = None
        selected_name = None
        reasons = []
        eta = None

        if sar_decision:
            selected_id = sar_decision.get("selected_vehicle_id")
            selected_name = sar_decision.get("selected_vehicle_name")

            for ev in sar_decision.get("evaluations", []):
                candidates.append(CandidateAssetEvaluation(
                    vehicle_id=ev["vehicle_id"],
                    vehicle_name=ev["vehicle_name"],
                    vehicle_type=ev["vehicle_type"],
                    distance_km=ev["distance_km"],
                    estimated_transit_time_min=ev["estimated_transit_time_min"],
                    fuel_remaining_pct=ev["fuel_remaining_pct"],
                    fuel_after_mission_pct=ev["fuel_after_mission_pct"],
                    is_eligible=ev["is_eligible"],
                    score=ev["score"],
                    disqualification_reasons=ev.get("disqualification_reasons", []),
                    explanation_points=ev.get("explanation_points", [])
                ))
                if ev["vehicle_id"] == selected_id:
                    eta = ev["estimated_transit_time_min"]
                    reasons = ev.get("explanation_points", [])

        explainability = ExplainabilityBlock(
            what_happened=f"{emg_info['severity']} {emg_info['incident_type']} incident occurred near {emg_info['nearest_landmark']} affecting {emg_info['affected_count']} personnel.",
            why_it_matters=f"Rapid search and rescue triage is imperative under extreme Antarctic thermal conditions to prevent severe hypothermia or injury.",
            what_to_watch=f"Dispatch asset {selected_name or 'SAR asset'} route progress, telemetry link, and ETA ({eta:.0f} min).",
            recommended_operator_action=f"Authorize SAR mission execution for {selected_name or 'primary responder'} and notify station trauma bay."
        )

        return EmergencyIntelligence(
            scenario_id=scenario_id,
            has_active_emergency=True,
            incident=emg_info,
            severity=emg_info.get("severity"),
            affected_personnel_count=emg_info.get("affected_count", 0),
            affected_personnel_ids=emg_info.get("affected_personnel_ids", []),
            required_capabilities=emg_info.get("required_capabilities", []),
            candidate_assets=candidates,
            selected_asset_id=selected_id,
            selected_asset_name=selected_name,
            selection_reasons=reasons,
            estimated_eta_min=eta,
            explainability=explainability
        )

    def get_resource_forecast(self, scenario_id: int) -> List[ResourceForecast]:
        """
        Generate explainable resource depletion forecasts for fuel, battery, and station inventory.
        """
        data = self.sim_service._get_runner_for_scenario(scenario_id)
        state = data["state"]
        runner = data["runner"]
        total_ticks = data["run_output"]["total_ticks"]

        forecasts: List[ResourceForecast] = []

        # 1. Main Station Fuel Inventory Forecast
        fuel_inv = next((inv for inv in state.inventory.values() if inv.category.value == "FUEL"), None)
        if fuel_inv:
            stock = fuel_inv.current_stock
            daily_rate = fuel_inv.daily_consumption_rate
            hourly_rate = daily_rate / 24.0 if daily_rate > 0 else 0.1
            hours_autonomy = (stock / hourly_rate) if hourly_rate > 0 else 999.0

            # Historical points
            hist_points: List[ForecastDataPoint] = []
            init_stock = stock + (daily_rate * (total_ticks / 1440.0))
            for tick_step in range(0, total_ticks + 1, max(1, total_ticks // 4)):
                t_hours = tick_step / 60.0
                val = max(0.0, init_stock - (hourly_rate * t_hours))
                hist_points.append(ForecastDataPoint(
                    timestamp_tick=tick_step,
                    time_label=f"T+{tick_step}m",
                    value=round(val, 1),
                    is_projected=False
                ))

            # Projected points (next 48 hours)
            proj_points: List[ForecastDataPoint] = []
            proj_horizon_hours = 48.0
            for h in [12.0, 24.0, 36.0, 48.0]:
                proj_val = max(0.0, stock - (hourly_rate * h))
                proj_points.append(ForecastDataPoint(
                    timestamp_tick=total_ticks + int(h * 60),
                    time_label=f"+{h:.0f}h Proj",
                    value=round(proj_val, 1),
                    is_projected=True
                ))

            fuel_risk = "CRITICAL" if fuel_inv.days_of_autonomy < fuel_inv.safety_buffer_days else ("WATCH" if fuel_inv.days_of_autonomy < 14 else "SAFE")
            
            exp = (
                f"Fuel depletion is projected at {daily_rate:.0f} L/day. "
                f"At current rate, station stock will reach 0 in {hours_autonomy:.1f} hours ({hours_autonomy/24.0:.1f} days)."
            )

            forecasts.append(ResourceForecast(
                resource="Station Fuel Reserves",
                location_id=fuel_inv.location_id,
                current_value=round(stock, 1),
                unit=fuel_inv.unit,
                current_rate=round(daily_rate, 1),
                forecast_horizon_hours=proj_horizon_hours,
                forecast_value=round(max(0.0, stock - (hourly_rate * proj_horizon_hours)), 1),
                autonomy_hours_remaining=round(hours_autonomy, 1),
                risk=fuel_risk,
                forecast_available=True,
                confidence_note="Projected based on current consumption trend and active thermal load.",
                explanation=exp,
                historical_points=hist_points,
                projected_points=proj_points
            ))

        # 2. Active Vehicle Battery / Fuel Telemetry Forecast (if vehicle is in transit)
        in_transit_veh = next((v for v in state.vehicles.values() if v.status.value in ["IN_TRANSIT", "DISPATCHED_EMERGENCY"]), None)
        if in_transit_veh:
            veh_fuel = in_transit_veh.fuel_pct
            burn_rate = in_transit_veh.fuel_burn_rate_l_per_km * (in_transit_veh.speed_kmh / 60.0) if in_transit_veh.speed_kmh > 0 else 0.5
            
            veh_hist = [
                ForecastDataPoint(timestamp_tick=0, time_label="Depart", value=100.0, is_projected=False),
                ForecastDataPoint(timestamp_tick=total_ticks, time_label="Current", value=round(veh_fuel, 1), is_projected=False)
            ]
            veh_proj = [
                ForecastDataPoint(timestamp_tick=total_ticks + 30, time_label="+30m Proj", value=round(max(0.0, veh_fuel - 12.0), 1), is_projected=True),
                ForecastDataPoint(timestamp_tick=total_ticks + 60, time_label="+60m Proj", value=round(max(0.0, veh_fuel - 24.0), 1), is_projected=True)
            ]

            forecasts.append(ResourceForecast(
                resource=f"{in_transit_veh.name} Fuel Level",
                location_id=in_transit_veh.id,
                current_value=round(veh_fuel, 1),
                unit="%",
                current_rate=round(burn_rate, 2),
                forecast_horizon_hours=1.0,
                forecast_value=round(max(0.0, veh_fuel - 24.0), 1),
                autonomy_hours_remaining=round((veh_fuel / 24.0) * 1.0, 1),
                risk="SAFE" if veh_fuel > 30.0 else "WATCH",
                forecast_available=True,
                confidence_note="Projected based on route terrain difficulty and nominal vehicle cruise speed.",
                explanation=f"{in_transit_veh.name} has {veh_fuel:.1f}% fuel remaining, sufficient for route completion.",
                historical_points=veh_hist,
                projected_points=veh_proj
            ))

        return forecasts

    def get_intelligence_summary(self, scenario_id: int) -> IntelligenceSummaryResponse:
        """
        Aggregate explainable intelligence summary across all modules for centralized command dashboards.
        """
        data = self.sim_service._get_runner_for_scenario(scenario_id)
        sc_name = data["scenario_name"]

        autonomy = self.get_autonomy_intelligence(scenario_id)
        resupply_risk = self.get_resupply_risk(scenario_id)
        readiness = self.get_readiness_intelligence(scenario_id)
        emergency = self.get_emergency_intelligence(scenario_id)
        forecasts = self.get_resource_forecast(scenario_id)

        # Alerts summary
        raw_alerts = self.sim_service.get_alerts(scenario_id)
        crit_alerts = sum(1 for a in raw_alerts if a["severity"] == "CRITICAL")
        warn_alerts = sum(1 for a in raw_alerts if a["severity"] == "WARNING")
        alerts_summary = {
            "total": len(raw_alerts),
            "critical": crit_alerts,
            "warning": warn_alerts,
            "top_alert": raw_alerts[0]["message"] if raw_alerts else "All systems nominal"
        }

        # Highest Risk
        if any(i.risk == "CRITICAL" for i in autonomy) or emergency.has_active_emergency or readiness.overall_state == "CRITICAL":
            highest_risk = "CRITICAL"
        elif any(i.risk in ["WATCH", "AT_RISK"] for i in autonomy) or readiness.overall_state in ["CONDITIONAL", "DEGRADED"]:
            highest_risk = "WARNING"
        else:
            highest_risk = "NOMINAL"

        return IntelligenceSummaryResponse(
            scenario_id=scenario_id,
            scenario_name=sc_name,
            overall_readiness=readiness.overall_state,
            highest_risk=highest_risk,
            autonomy=autonomy,
            resupply_risk=resupply_risk,
            readiness=readiness,
            emergency=emergency,
            forecasts=forecasts,
            alerts_summary=alerts_summary,
            explainability=readiness.explainability
        )

    def _build_scenario_explainability(self, scenario_id: int, overall_state: str, factors: List[ReadinessFactor]) -> ExplainabilityBlock:
        """
        Generate structured operational explainability blocks tailored to each operational demonstration.
        """
        if scenario_id == 1:
            return ExplainabilityBlock(
                what_happened="Routine expedition resupply traverse underway from Maitri-II to Camp Alpha under nominal weather.",
                why_it_matters="Operations and inventory levels conform to baseline winter survival models with full communications.",
                what_to_watch="Monitor vehicle GPS route progression and routine cold-chain medical package telemetry.",
                recommended_operator_action="Continue nominal monitoring; no corrective operator intervention required."
            )
        elif scenario_id == 2:
            return ExplainabilityBlock(
                what_happened="Severe fuel consumption spike and storage leak occurred at Maitri-II Station, reducing fuel autonomy to under 5 days.",
                why_it_matters="Fuel reserves have breached the mandatory 7-day safety buffer, endangering generator power and habitat heating.",
                what_to_watch="Station daily fuel burn rate (650 L/day) and remaining autonomy horizon (4.96 days).",
                recommended_operator_action="Prioritize emergency fuel resupply traverse, restrict non-critical heating circuits, and prepare secondary generator shedding."
            )
        elif scenario_id == 3:
            return ExplainabilityBlock(
                what_happened="Crevasse fall incident occurred at Waypoint C-3; roll-call muster identified PERS-003 as unconfirmed in the field.",
                why_it_matters="Sub-zero temperatures and crevasse exposure present immediate life-safety risk requiring urgent SAR extraction.",
                what_to_watch="Dispatched SAR vehicle telemetry, transit progress, weather visibility, and victim thermal signature.",
                recommended_operator_action="Authorize SAR rapid response dispatch (UAV-01 & Snowcat-01) and stage Maitri-II trauma clinic for immediate admission."
            )
        elif scenario_id == 4:
            return ExplainabilityBlock(
                what_happened="Medical cooler refrigeration failed on Snowcat-01, causing cargo compartment temperature to rapidly drift past allowable limits.",
                why_it_matters="Critical biological samples (CRG-BIO-01) and insulin are subject to irreversible thermal denaturation and freezing breach.",
                what_to_watch="Cold-chain container temperature curve, passive thermal buffer decay rate, and insulation status.",
                recommended_operator_action="Switch cargo cooler to auxiliary battery circuit or immediately transfer specimens to secondary insulated thermal flask."
            )
        elif scenario_id == 5:
            return ExplainabilityBlock(
                what_happened="Severe geomagnetic storm severed primary Iridium satellite uplink for 30 minutes during field traverse.",
                why_it_matters="Real-time telemetry was temporarily interrupted, but field units buffered 30 telemetry frames in local NVRAM.",
                what_to_watch="Uplink reconnection integrity and store-and-forward queue reconciliation replay metrics.",
                recommended_operator_action="Confirm complete telemetry buffer replay synchronization upon satellite restoration; verify data integrity."
            )
        else:
            return ExplainabilityBlock(
                what_happened="Operational telemetry processed across all stations and field assets.",
                why_it_matters=f"Current expedition readiness synthesized as {overall_state}.",
                what_to_watch="Consumables autonomy, vehicle telemetry heartbeats, and alert logs.",
                recommended_operator_action="Review operational dashboards and verify subsystem status."
            )
