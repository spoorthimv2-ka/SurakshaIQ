from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from enum import Enum
from app.schemas.enums import EntityStatus

class ReportType(str, Enum):
    CRIME_SUMMARY = "CRIME_SUMMARY"
    FIR_SUMMARY = "FIR_SUMMARY"
    HOTSPOT_ANALYSIS = "HOTSPOT_ANALYSIS"
    REPEAT_OFFENDER_ANALYSIS = "REPEAT_OFFENDER_ANALYSIS"
    NETWORK_ANALYSIS = "NETWORK_ANALYSIS"
    PREDICTIVE_RISK = "PREDICTIVE_RISK"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    ALERTS_SUMMARY = "ALERTS_SUMMARY"
    DISTRICT_REPORT = "DISTRICT_REPORT"
    STATION_REPORT = "STATION_REPORT"

class ReportBase(BaseModel):
    name: str
    report_type: ReportType
    parameters_json: Optional[str] = None
    created_by_officer_id: str
    status: EntityStatus = EntityStatus.ACTIVE

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    name: Optional[str] = None
    report_type: Optional[ReportType] = None
    parameters_json: Optional[str] = None
    created_by_officer_id: Optional[str] = None
    status: Optional[EntityStatus] = None

class ReportResponse(ReportBase):
    ROWID: str
    CREATEDTIME: str
    MODIFIEDTIME: str

    model_config = ConfigDict(from_attributes=True)

class ReportSummaryResponse(BaseModel):
    total_reports: int
    reports_today: int
    available_report_types: int

    model_config = ConfigDict(from_attributes=True)

class ReportTypeInfo(BaseModel):
    type: ReportType
    label: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class ReportRequest(BaseModel):
    report_type: ReportType
    name: str
    parameters_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReportStatistics(BaseModel):
    by_type: List[Dict[str, Any]]
    by_status: List[Dict[str, Any]]
    total_count: int

    model_config = ConfigDict(from_attributes=True)
