from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List


class UserSettings(BaseModel):
    user_id: str
    theme: str = "light"
    language: str = "en"
    notifications_enabled: bool = True
    email_alerts: bool = True
    push_notifications: bool = True
    ai_suggestions: bool = True
    default_district_id: Optional[str] = None
    default_station_id: Optional[str] = None
    timezone: str = "Asia/Kolkata"

    model_config = ConfigDict(from_attributes=True)


class SystemSettings(BaseModel):
    key: str
    value: Any
    description: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)


class Notification(BaseModel):
    notification_id: str
    user_id: str
    type: str
    title: str
    message: str
    severity: str
    read: bool = False
    dismissed: bool = False
    created_at: str
    read_at: Optional[str] = None
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class NotificationSummary(BaseModel):
    total: int
    unread: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]

    model_config = ConfigDict(from_attributes=True)


class ExportRequest(BaseModel):
    report_type: str
    format: str  # csv, json, print
    filters: Optional[Dict[str, Any]] = None
    data: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class ExportResponse(BaseModel):
    download_url: Optional[str] = None
    content: Optional[str] = None
    filename: str
    format: str
    size_bytes: int

    model_config = ConfigDict(from_attributes=True)


class AIReportRequest(BaseModel):
    report_type: str
    scope: Dict[str, Any]
    analytics: Optional[Dict[str, Any]] = None
    format: str = "text"

    model_config = ConfigDict(from_attributes=True)


class AIReportResponse(BaseModel):
    report_id: str
    title: str
    content: str
    format: str
    generated_at: str
    confidence: float
    is_fallback: bool
    sections: List[str]

    model_config = ConfigDict(from_attributes=True)
