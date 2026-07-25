from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from app.models.enums import Role, Permission, JurisdictionType
from app.security.utils import raise_unauthorized, raise_forbidden
from app.authorization.permissions import PermissionRegistry
from app.authorization.service import get_current_officer, enforce_jurisdiction, RequirePermission
from app.config.settings import settings
from app.core.logger import logger

bearer_scheme = HTTPBearer(auto_error=False)


class _DeprecatedCurrentUser:
    def __init__(self):
        pass

    async def __call__(self, current_officer: Dict[str, Any] = Depends(get_current_officer)) -> Dict[str, Any]:
        return current_officer


get_current_user = get_current_officer
get_current_officer = get_current_officer


class RequireRole:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_officer: Dict[str, Any] = Depends(get_current_officer),
    ) -> Dict[str, Any]:
        officer_role_str = current_officer.get("role", "")
        try:
            officer_role = Role(officer_role_str)
        except ValueError:
            raise_forbidden(f"Unknown role: {officer_role_str}")

        if officer_role not in self.allowed_roles:
            raise_forbidden(
                f"Operation not permitted. Required roles: {[r.value for r in self.allowed_roles]}"
            )

        return current_officer
