"""
FastAPI Endpoints for Explainable Operational Intelligence & Decision Support (Stage 3.5)
"""
from typing import List
from fastapi import APIRouter, Query, HTTPException, Depends

from app.schemas.intelligence import (
    AutonomyItem,
    ResupplyRiskItem,
    ReadinessIntelligence,
    EmergencyIntelligence,
    ResourceForecast,
    IntelligenceSummaryResponse
)
from app.services.intelligence_service import IntelligenceService
from app.services.simulation_service import SimulationService

router = APIRouter()

# Dependency provider for IntelligenceService
def get_intelligence_service() -> IntelligenceService:
    return IntelligenceService()


@router.get("/summary", response_model=IntelligenceSummaryResponse)
def get_intelligence_summary(
    scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)"),
    service: IntelligenceService = Depends(get_intelligence_service)
) -> IntelligenceSummaryResponse:
    """
    Get aggregated explainable operational intelligence summary across all dimensions.
    """
    try:
        return service.get_intelligence_summary(scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate intelligence summary: {str(e)}")


@router.get("/autonomy", response_model=List[AutonomyItem])
def get_autonomy_intelligence(
    scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)"),
    service: IntelligenceService = Depends(get_intelligence_service)
) -> List[AutonomyItem]:
    """
    Get winter autonomy intelligence and Days of Autonomy per inventory category.
    """
    try:
        return service.get_autonomy_intelligence(scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate autonomy intelligence: {str(e)}")


@router.get("/resupply-risk", response_model=List[ResupplyRiskItem])
def get_resupply_risk(
    scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)"),
    service: IntelligenceService = Depends(get_intelligence_service)
) -> List[ResupplyRiskItem]:
    """
    Get resupply risk levels (SAFE, WATCH, AT_RISK, CRITICAL) and actionable operator guidance.
    """
    try:
        return service.get_resupply_risk(scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze resupply risk: {str(e)}")


@router.get("/readiness", response_model=ReadinessIntelligence)
def get_readiness_intelligence(
    scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)"),
    service: IntelligenceService = Depends(get_intelligence_service)
) -> ReadinessIntelligence:
    """
    Get multi-factor expedition readiness assessment and explainability synthesis.
    """
    try:
        return service.get_readiness_intelligence(scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate readiness intelligence: {str(e)}")


@router.get("/emergency", response_model=EmergencyIntelligence)
def get_emergency_intelligence(
    scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)"),
    service: IntelligenceService = Depends(get_intelligence_service)
) -> EmergencyIntelligence:
    """
    Get emergency incident triage, SAR asset selection matrix, and operational justification.
    """
    try:
        return service.get_emergency_intelligence(scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve emergency intelligence: {str(e)}")


@router.get("/forecast", response_model=List[ResourceForecast])
def get_resource_forecast(
    scenario_id: int = Query(1, ge=1, le=5, description="Scenario ID (1-5)"),
    service: IntelligenceService = Depends(get_intelligence_service)
) -> List[ResourceForecast]:
    """
    Get explainable resource depletion forecasts for fuel, battery, and station consumables.
    """
    try:
        return service.get_resource_forecast(scenario_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate resource forecast: {str(e)}")
