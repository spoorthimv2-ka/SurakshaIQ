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

class DashboardSummaryResponse(BaseModel):
    total_crimes: int
    total_firs: int
    active_firs: int
    closed_firs: int
    crimes_today: int
    firs_today: int
    registered_districts: int
    registered_police_stations: int

    @property
    def totalCases(self) -> int:
        return self.total_crimes

    @property
    def openCases(self) -> int:
        return self.active_firs

    @property
    def resolvedCases(self) -> int:
        return self.closed_firs

    activeAlerts: int = 0
    hotspotsCount: int = 0
    anomaliesCount: int = 0

    model_config = ConfigDict(from_attributes=True)

class RecentCrimeResponse(BaseModel):
    ROWID: str
    title: str
    crime_type: str
    status: str
    CREATEDTIME: str

    model_config = ConfigDict(from_attributes=True)

class RecentFirResponse(BaseModel):
    ROWID: str
    fir_number: str
    crime_id: str
    status: str
    CREATEDTIME: str

    model_config = ConfigDict(from_attributes=True)

class CrimeTrendResponse(BaseModel):
    period: str
    count: int

    model_config = ConfigDict(from_attributes=True)

class DistrictSummaryResponse(BaseModel):
    district_id: str
    district_name: str
    crime_count: int
    fir_count: int
    active_investigations: int

    model_config = ConfigDict(from_attributes=True)
