from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.enums import EntityStatus

class AlertBase(BaseModel):
    title: str
    description: str
    severity: str
    source: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    district_id: Optional[str] = None
    station_id: Optional[str] = None
    recommended_action: Optional[str] = None
    status: EntityStatus = EntityStatus.ACTIVE

class AlertCreate(AlertBase):
    pass

class AlertUpdate(BaseModel):
    status: Optional[EntityStatus] = None
    recommended_action: Optional[str] = None

class AlertResponse(AlertBase):
    ROWID: str
    CREATEDTIME: str
    MODIFIEDTIME: str

    model_config = ConfigDict(from_attributes=True)

class AlertSummary(BaseModel):
    total_alerts: int
    active_alerts: int
    acknowledged_alerts: int
    resolved_alerts: int
    critical_alerts: int

    model_config = ConfigDict(from_attributes=True)

class AlertStatistics(BaseModel):
    by_severity: List[dict]
    by_source: List[dict]
    by_district: List[dict]

    model_config = ConfigDict(from_attributes=True)
