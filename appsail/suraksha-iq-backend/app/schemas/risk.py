from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class RiskFactor(BaseModel):
    name: str
    weight: float
    contribution: float

    model_config = ConfigDict(from_attributes=True)

class RiskPrediction(BaseModel):
    entity_id: str
    entity_type: str
    entity_name: str
    risk_score: float
    risk_level: str
    contributing_factors: List[RiskFactor]
    last_updated: str

    model_config = ConfigDict(from_attributes=True)

class DistrictRisk(BaseModel):
    district_id: str
    district_name: str
    risk_score: float
    risk_level: str
    crime_count: int
    fir_count: int
    hotspot_score: float
    repeat_offender_count: int
    contributing_factors: List[RiskFactor]

    model_config = ConfigDict(from_attributes=True)

class StationRisk(BaseModel):
    station_id: str
    station_name: str
    district_id: str
    district_name: str
    risk_score: float
    risk_level: str
    crime_count: int
    fir_count: int
    hotspot_score: float
    contributing_factors: List[RiskFactor]

    model_config = ConfigDict(from_attributes=True)

class RiskSummary(BaseModel):
    total_entities: int
    average_risk: float
    highest_risk_district: str
    highest_risk_station: str
    total_high_risk: int
    total_critical_risk: int
    risk_distribution: List[dict]

    model_config = ConfigDict(from_attributes=True)
