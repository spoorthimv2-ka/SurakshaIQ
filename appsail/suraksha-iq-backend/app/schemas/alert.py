from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class AlertBase(BaseModel):
    type: str
    severity: str
    status: str
    message: str
    district_id: Optional[str] = None

class AlertResponse(AlertBase):
    id: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AlertListResponse(BaseModel):
    data: List[AlertResponse]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)
