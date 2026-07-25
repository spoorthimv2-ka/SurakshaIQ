from fastapi import Request, APIRouter, Depends, Query, HTTPException, status
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from app.api.deps import get_current_officer
from app.services.predictive_service import PredictiveService
from app.schemas.predictive import (
    PredictiveFilters,
    CrimeForecast,
    EmergingHotspot,
    RiskIndex,
    PatrolRecommendation,
    TemporalIntelligence,
    TrendAnalysis,
    ScenarioFilters,
    ScenarioSimulation,
    PredictiveDashboard,
    PredictiveAIExplanation,
)


class ExplainRequest(BaseModel):
    filters: Optional[Dict[str, Any]] = None


router = APIRouter()


@router.get(
    "/forecast",
    response_model=List[CrimeForecast],
    summary="Crime Forecast",
    description="Forecast crime trends by district, police station, or crime category for next 7/30/90 days.",
)
async def get_forecast(
    request: Request,
    district_id: Optional[str] = Query(None),
    station_id: Optional[str] = Query(None),
    crime_category: Optional[str] = Query(None),
    time_period: Optional[str] = Query("30d"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(district_id=district_id, station_id=station_id, crime_category=crime_category, time_period=time_period)
        result = await service.get_forecast(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch forecast: {str(e)}")


@router.get(
    "/emerging-hotspots",
    response_model=List[EmergingHotspot],
    summary="Emerging Hotspot Prediction",
    description="Predict future hotspot locations with intensity, confidence, and explanation.",
)
async def get_emerging_hotspots(
    request: Request,
    district_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(district_id=district_id)
        result = await service.get_emerging_hotspots(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch emerging hotspots: {str(e)}")


@router.get(
    "/risk-index",
    response_model=List[RiskIndex],
    summary="Dynamic Risk Index",
    description="Generate risk scores for districts, police stations, and crime categories with trend indicators.",
)
async def get_risk_index(
    request: Request,
    district_id: Optional[str] = Query(None),
    station_id: Optional[str] = Query(None),
    crime_category: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(district_id=district_id, station_id=station_id, crime_category=crime_category)
        result = await service.get_dynamic_risk_index(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch risk index: {str(e)}")


@router.get(
    "/patrol-recommendations",
    response_model=List[PatrolRecommendation],
    summary="Patrol Deployment Intelligence",
    description="Generate recommendations for patrol allocation, checkpoints, surveillance areas, and resource allocation.",
)
async def get_patrol_recommendations(
    request: Request,
    district_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(district_id=district_id)
        result = await service.get_patrol_recommendations(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch patrol recommendations: {str(e)}")


@router.get(
    "/temporal-intelligence",
    response_model=TemporalIntelligence,
    summary="Temporal Intelligence",
    description="Analyse hourly, day-of-week, monthly, seasonal crime distribution.",
)
async def get_temporal_intelligence(
    request: Request,
    district_id: Optional[str] = Query(None),
    station_id: Optional[str] = Query(None),
    crime_category: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(district_id=district_id, station_id=station_id, crime_category=crime_category)
        result = await service.get_temporal_intelligence(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch temporal intelligence: {str(e)}")


@router.get(
    "/trend-analysis",
    response_model=TrendAnalysis,
    summary="Trend Analysis",
    description="Show increasing, decreasing, stable crime categories and emerging patterns.",
)
async def get_trend_analysis(
    request: Request,
    district_id: Optional[str] = Query(None),
    station_id: Optional[str] = Query(None),
    crime_category: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(district_id=district_id, station_id=station_id, crime_category=crime_category)
        result = await service.get_trend_analysis(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch trend analysis: {str(e)}")


@router.post(
    "/scenario-simulator",
    response_model=ScenarioSimulation,
    summary="Scenario Simulator",
    description="Simulate district/station/category/time-window combinations. Returns recomputed forecast, risk, hotspots, and patrols.",
)
async def simulate_scenario(
    request: Request,
    scenario: ScenarioFilters,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        result = await service.simulate_scenario(current_user, scenario)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to run scenario: {str(e)}")


@router.get(
    "/dashboard",
    response_model=PredictiveDashboard,
    summary="Predictive Dashboard",
    description="Aggregated KPI cards for predictive intelligence.",
)
async def get_predictive_dashboard(
    request: Request,
    district_id: Optional[str] = Query(None),
    station_id: Optional[str] = Query(None),
    crime_category: Optional[str] = Query(None),
    time_period: Optional[str] = Query("30d"),
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(district_id=district_id, station_id=station_id, crime_category=crime_category, time_period=time_period)
        result = await service.get_predictive_dashboard(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch predictive dashboard: {str(e)}")


@router.post(
    "/ai-intelligence",
    response_model=PredictiveAIExplanation,
    summary="AI Intelligence",
    description="Generate AI-powered forecast explanation, risk explanation, strategy recommendations, and executive summary. Falls back to deterministic when AI is unavailable.",
)
async def get_ai_intelligence(
    request: Request,
    body: ExplainRequest = ...,
    current_user: Dict[str, Any] = Depends(get_current_officer),
):
    try:
        service = PredictiveService(request)
        filters = PredictiveFilters(**(body.filters or {}))
        result = await service.get_ai_intelligence(current_user, filters)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate AI intelligence: {str(e)}")
