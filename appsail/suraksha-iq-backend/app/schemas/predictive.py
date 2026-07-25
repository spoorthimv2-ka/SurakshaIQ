from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class ForecastPoint(BaseModel):
    date: str
    predicted_count: int
    confidence_low: int
    confidence_high: int
    confidence_score: float

    model_config = ConfigDict(from_attributes=True)


class CrimeForecast(BaseModel):
    entity_id: str
    entity_type: str
    entity_name: str
    period: str
    forecast_points: List[ForecastPoint]
    confidence: float
    total_predicted: int

    model_config = ConfigDict(from_attributes=True)


class EmergingHotspot(BaseModel):
    id: str
    district_id: str
    district_name: str
    station_id: str
    station_name: str
    intensity: float
    confidence: float
    risk_level: str
    explanation: str
    predicted_crime_count: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class RiskIndex(BaseModel):
    entity_id: str
    entity_type: str
    entity_name: str
    risk_score: float
    risk_level: str
    trend: str
    previous_score: float
    score_change: float
    explanation: str

    model_config = ConfigDict(from_attributes=True)


class PatrolRecommendation(BaseModel):
    zone_id: str
    zone_name: str
    zone_type: str
    recommendation_type: str
    priority: str
    description: str
    reason: str
    suggested_patrols: int
    time_windows: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class TemporalDistribution(BaseModel):
    hour: Optional[int] = None
    day_of_week: Optional[str] = None
    month: Optional[str] = None
    season: Optional[str] = None
    count: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


class TemporalIntelligence(BaseModel):
    hourly_distribution: List[TemporalDistribution]
    daily_distribution: List[TemporalDistribution]
    monthly_distribution: List[TemporalDistribution]
    seasonal_distribution: List[TemporalDistribution]
    peak_hour: Optional[int] = None
    peak_day: Optional[str] = None
    peak_month: Optional[str] = None
    peak_season: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TrendCategory(BaseModel):
    category: str
    trend: str
    change_percent: float
    count_current: int
    count_previous: int

    model_config = ConfigDict(from_attributes=True)


class EmergingPattern(BaseModel):
    pattern_type: str
    description: str
    affected_entities: List[str]
    confidence: float
    severity: str

    model_config = ConfigDict(from_attributes=True)


class TrendAnalysis(BaseModel):
    increasing_categories: List[TrendCategory]
    decreasing_categories: List[TrendCategory]
    stable_categories: List[TrendCategory]
    emerging_patterns: List[EmergingPattern]
    overall_trend: str

    model_config = ConfigDict(from_attributes=True)


class ScenarioFilters(BaseModel):
    district_id: Optional[str] = None
    station_id: Optional[str] = None
    crime_category: Optional[str] = None
    time_window: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ScenarioSimulation(BaseModel):
    filters: ScenarioFilters
    forecast: Dict[str, Any]
    risk: Dict[str, Any]
    hotspots: List[Dict[str, Any]]
    patrol_recommendations: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)


class PredictiveDashboard(BaseModel):
    highest_risk_district: Dict[str, Any]
    fastest_growing_crime: Dict[str, Any]
    emerging_hotspot: Dict[str, Any]
    forecast_confidence: float
    recommended_patrol_increase: int
    predicted_incident_count: int
    time_period: str

    model_config = ConfigDict(from_attributes=True)


class PredictiveAIExplanation(BaseModel):
    forecast_explanation: str
    risk_explanation: str
    strategy_recommendations: List[str]
    executive_summary: str
    confidence: float
    is_fallback: bool

    model_config = ConfigDict(from_attributes=True)


class PredictiveFilters(BaseModel):
    district_id: Optional[str] = None
    station_id: Optional[str] = None
    crime_category: Optional[str] = None
    time_period: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
