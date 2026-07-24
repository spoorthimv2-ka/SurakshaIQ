from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.enums import EntityStatus

class DistrictBase(BaseModel):
    name: str
    code: str
    status: EntityStatus = EntityStatus.ACTIVE

class DistrictCreate(DistrictBase):
    pass

class DistrictUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[EntityStatus] = None

class DistrictResponse(DistrictBase):
    ROWID: str
    CREATEDTIME: str
    MODIFIEDTIME: str
    
    model_config = ConfigDict(from_attributes=True)


class DistrictSummary(BaseModel):
    id: str
    name: str
    caseCount: int = 0
    riskIndex: float = 0.0

    model_config = ConfigDict(from_attributes=True)
