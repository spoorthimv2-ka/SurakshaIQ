from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID

class KPIDelta(BaseModel):
    value: float
    delta: Optional[float] = None

class DashboardKPIsResponse(BaseModel):
    total_cases: KPIDelta
    resolution_rate: KPIDelta
    active_hotspots: KPIDelta
    open_alerts: KPIDelta
    risk_index: KPIDelta

    model_config = ConfigDict(from_attributes=True)

class CrimeCategoryStats(BaseModel):
    crime_type: str
    count: int

class DistrictStats(BaseModel):
    district_id: UUID
    district_name: str
    count: int

class StatusStats(BaseModel):
    status: str
    count: int

class DashboardStatisticsResponse(BaseModel):
    by_category: List[CrimeCategoryStats]
    by_district: List[DistrictStats]
    by_status: List[StatusStats]
    total_count: int

    model_config = ConfigDict(from_attributes=True)
