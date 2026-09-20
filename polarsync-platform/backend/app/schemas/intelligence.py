"""
Pydantic Schemas for Explainable Operational Intelligence & Decision Support (Stage 3.5)
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ExplainabilityBlock(BaseModel):
    """
    Standardized operational explainability structure.
    """
    what_happened: str = Field(..., description="Summary of the operational event or observed telemetry anomaly")
    why_it_matters: str = Field(..., description="Operational impact on expedition safety, autonomy, or mission")
    what_to_watch: str = Field(..., description="Key telemetry metrics or indicators to monitor closely")
    recommended_operator_action: str = Field(..., description="Actionable decision-support guidance for operators")


class AutonomyItem(BaseModel):
    category: str
    location_id: str
    location_name: str
    current_stock: float
    unit: str
    daily_consumption_rate: float
    days_of_autonomy: float
    safety_buffer_days: float
    resupply_window_days: float
    risk: str  # SAFE, WATCH, AT_RISK, CRITICAL
    trend: str  # STABLE, DEPLETING_RAPIDLY, DEPLETING_NOMINALLY, ACCUMULATING
    explanation: str


class ResupplyRiskItem(BaseModel):
    category: str
    location_name: str
    current_stock: float
    unit: str
    days_of_autonomy: float
    safety_buffer_days: float
    resupply_window_days: float
    risk_level: str  # SAFE, WATCH, AT_RISK, CRITICAL
    explanation: str
    recommended_action: str


class ReadinessFactor(BaseModel):
    name: str  # Personnel, Fleet, Inventory, Cargo, Connectivity, Emergencies
    state: str  # NOMINAL, WATCH, DEGRADED, CRITICAL
    metric: str
    reason: str


class ReadinessIntelligence(BaseModel):
    scenario_id: int
    overall_state: str  # NOMINAL, CONDITIONAL, DEGRADED, CRITICAL
    readiness_score: str
    factors: List[ReadinessFactor]
    explanation: str
    explainability: ExplainabilityBlock


class CandidateAssetEvaluation(BaseModel):
    vehicle_id: str
    vehicle_name: str
    vehicle_type: str
    distance_km: float
    estimated_transit_time_min: float
    fuel_remaining_pct: float
    fuel_after_mission_pct: float
    is_eligible: bool
    score: float
    capabilities: List[str] = []
    disqualification_reasons: List[str] = []
    explanation_points: List[str] = []


class EmergencyIntelligence(BaseModel):
    scenario_id: int
    has_active_emergency: bool
    incident: Optional[Dict[str, Any]] = None
    severity: Optional[str] = None
    affected_personnel_count: int = 0
    affected_personnel_ids: List[str] = []
    required_capabilities: List[str] = []
    candidate_assets: List[CandidateAssetEvaluation] = []
    selected_asset_id: Optional[str] = None
    selected_asset_name: Optional[str] = None
    selection_reasons: List[str] = []
    estimated_eta_min: Optional[float] = None
    explainability: Optional[ExplainabilityBlock] = None


class ForecastDataPoint(BaseModel):
    timestamp_tick: int
    time_label: str
    value: float
    is_projected: bool


class ResourceForecast(BaseModel):
    resource: str
    location_id: Optional[str] = None
    current_value: float
    unit: str
    current_rate: float
    forecast_horizon_hours: float
    forecast_value: float
    autonomy_hours_remaining: Optional[float] = None
    risk: str  # SAFE, WATCH, AT_RISK, CRITICAL
    forecast_available: bool = True
    confidence_note: str
    explanation: str
    historical_points: List[ForecastDataPoint] = []
    projected_points: List[ForecastDataPoint] = []


class IntelligenceSummaryResponse(BaseModel):
    scenario_id: int
    scenario_name: str
    overall_readiness: str
    highest_risk: str
    autonomy: List[AutonomyItem]
    resupply_risk: List[ResupplyRiskItem]
    readiness: ReadinessIntelligence
    emergency: EmergencyIntelligence
    forecasts: List[ResourceForecast]
    alerts_summary: Dict[str, Any]
    explainability: ExplainabilityBlock
