from fastapi import Depends, Request, HTTPException, status
from typing import Dict, Any

from app.services.auth_service import AuthService
from app.models.enums import Role, Permission, ROLE_PERMISSIONS_MAP
from app.security.utils import raise_unauthorized, raise_forbidden
from app.core.exceptions import CatalystConnectionError

async def get_auth_service() -> AuthService:
    try:
        return AuthService()
    except CatalystConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Catalyst authentication is unavailable locally."
        )

async def require_authenticated_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Validates that a valid Catalyst session exists for the request.
    Returns the Catalyst user identity.
    """
    try:
        catalyst_user = await auth_service.validate_session(request)
        if not catalyst_user:
            raise_unauthorized("Authentication required.")
        return catalyst_user
    except Exception as e:
        raise_unauthorized(str(e))

async def get_current_user(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    Retrieves the full authenticated user (Officer) profile from the Data Store,
    mapped from the Catalyst session identity.
    """
    try:
        user = await auth_service.get_current_user(request)
        if not user:
            raise_unauthorized("User profile not found in system.")
        return user
    except Exception as e:
        raise_unauthorized(str(e))

# get_current_officer is kept for backward compatibility with existing routes
async def get_current_officer(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Alias for get_current_user to maintain backward compatibility.
    """
    return current_user

class RequireRole:
    """
    Dependency class to enforce Role-based access control.
    """
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_officer: Dict[str, Any] = Depends(get_current_officer)) -> Dict[str, Any]:
        officer_role = current_officer.get("role", "")
        if officer_role not in [r.value for r in self.allowed_roles]:
            raise_forbidden(f"Operation not permitted. Required roles: {[r.value for r in self.allowed_roles]}")
        return current_officer

class RequirePermission:
    """
    Dependency class to enforce Permission-based access control.
    """
    def __init__(self, required_permissions: list[Permission]):
        self.required_permissions = required_permissions

    async def __call__(self, current_officer: Dict[str, Any] = Depends(get_current_officer)) -> Dict[str, Any]:
        officer_role_str = current_officer.get("role", "")
        try:
            officer_role = Role(officer_role_str)
        except ValueError:
            raise_forbidden(f"Unknown role: {officer_role_str}")
        
        officer_permissions = ROLE_PERMISSIONS_MAP.get(officer_role, [])
        
        for perm in self.required_permissions:
            if perm not in officer_permissions:
                raise_forbidden(f"Operation not permitted. Missing permission: {perm.value}")
        return current_officer
