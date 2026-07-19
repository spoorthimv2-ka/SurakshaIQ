from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, Dict, Any, List
from app.models.enums import Role
from app.schemas.enums import EntityStatus

class AdminUser(BaseModel):
    user_id: str
    officer_id: Optional[str] = None
    name: str
    email: EmailStr
    role: Role
    district: Optional[str] = None
    station: Optional[str] = None
    status: EntityStatus
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

class AdminUserCreate(BaseModel):
    name: str
    email: EmailStr
    role: Role
    district: Optional[str] = None
    station: Optional[str] = None
    status: EntityStatus = EntityStatus.ACTIVE

    model_config = ConfigDict(from_attributes=True)

class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None
    district: Optional[str] = None
    station: Optional[str] = None
    status: Optional[EntityStatus] = None

    model_config = ConfigDict(from_attributes=True)

class RoleInfo(BaseModel):
    id: str
    label: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class AdminStatistics(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    users_by_role: List[Dict[str, Any]]
    users_by_district: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)

class AuditLog(BaseModel):
    log_id: str
    action: str
    user: str
    target: str
    timestamp: str
    metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)
