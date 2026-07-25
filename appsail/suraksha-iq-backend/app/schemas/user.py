from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import Role
from app.schemas.enums import EntityStatus

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    role: Role
    status: EntityStatus = EntityStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    status: Optional[EntityStatus] = None

class UserResponse(UserBase):
    ROWID: str
    CREATEDTIME: str
    MODIFIEDTIME: str
    
    model_config = ConfigDict(from_attributes=True)
