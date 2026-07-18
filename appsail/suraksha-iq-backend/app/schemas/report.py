from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

class ReportBase(BaseModel):
    name: str
    report_type: str
    parameters_json: Optional[Dict[str, Any]] = None

class ReportResponse(ReportBase):
    id: str
    created_by_officer_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportListResponse(BaseModel):
    data: List[ReportResponse]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)

class ReportDetailResponse(ReportResponse):
    # Depending on the report_type, this could hold the fetched data
    # For now, it just holds the configuration metadata.
    report_data: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)
