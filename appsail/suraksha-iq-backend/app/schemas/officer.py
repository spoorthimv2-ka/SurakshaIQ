from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import Role

class OfficerBase(BaseModel):
    name: str
    email: EmailStr
    role: Role
    rank: Optional[str] = None
    designation: Optional[str] = None
    police_station_id: Optional[UUID] = None

class OfficerCreate(OfficerBase):
    catalyst_user_id: str

class OfficerResponse(OfficerBase):
    id: UUID
    catalyst_user_id: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
