from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from app.models.enums import Role, JurisdictionType, AccountStatus
from app.schemas.enums import EntityStatus

class OfficerBase(BaseModel):
    name: str
    email: EmailStr
    role: Role
    badge_number: str
    station_id: Optional[str] = None
    user_id: str
    district_id: Optional[str] = None
    jurisdiction_type: JurisdictionType = JurisdictionType.STATION
    account_status: AccountStatus = AccountStatus.ACTIVE
    status: EntityStatus = EntityStatus.ACTIVE
    rank: Optional[str] = None
    designation: Optional[str] = None

class OfficerCreate(OfficerBase):
    pass

class OfficerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    badge_number: Optional[str] = None
    station_id: Optional[str] = None
    district_id: Optional[str] = None
    jurisdiction_type: Optional[JurisdictionType] = None
    account_status: Optional[AccountStatus] = None
    status: Optional[EntityStatus] = None
    rank: Optional[str] = None
    designation: Optional[str] = None

class OfficerResponse(OfficerBase):
    ROWID: str
    CREATEDTIME: str
    MODIFIEDTIME: str
    failed_attempts: int = 0
    locked_until: Optional[str] = None
    last_login: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
