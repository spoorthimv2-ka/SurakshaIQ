from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.enums import EntityStatus


class AppUserBase(BaseModel):
    name: str
    email: str
    role: str
    status: EntityStatus = EntityStatus.ACTIVE


class AppUserCreate(AppUserBase):
    pass


class AppUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[EntityStatus] = None


class AppUserResponse(AppUserBase):
    ROWID: str
    CREATEDTIME: str
    MODIFIEDTIME: str

    model_config = ConfigDict(from_attributes=True)
