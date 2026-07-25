from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.enums import Role, Permission, JurisdictionType
from app.authorization.permissions import PermissionRegistry
from app.security.jwt import verify_access_token
from app.repositories.catalyst_officer_repo import CatalystOfficerRepository
from app.security.utils import raise_unauthorized, raise_forbidden
from app.core.logger import logger

bearer_scheme = HTTPBearer(auto_error=False)


def _get_attr(officer: Dict[str, Any], key: str, default=None):
    if isinstance(officer, dict):
        return officer.get(key, default)
    return getattr(officer, key, default)


def _build_officer_dict(officer: Dict[str, Any]) -> Dict[str, Any]:
    role_val = _get_attr(officer, "role", "")
    if isinstance(role_val, dict):
        role_str = (
            role_val.get("display_value")
            or role_val.get("label")
            or role_val.get("name")
            or ""
        )
    else:
        role_str = str(role_val) if role_val else ""

    row_id = (
        _get_attr(officer, "ROWID")
        or _get_attr(officer, "row_id")
        or _get_attr(officer, "id")
        or ""
    )
    catalyst_user_id = (
        _get_attr(officer, "user_id")
        or _get_attr(officer, "catalyst_user_id")
        or ""
    )
    name = _get_attr(officer, "name") or ""
    email = _get_attr(officer, "email") or ""
    police_station_id = (
        _get_attr(officer, "police_station_id")
        or _get_attr(officer, "station_id")
    )
    district_id = _get_attr(officer, "district_id") or ""
    badge_number = _get_attr(officer, "badge_number") or ""
    jurisdiction_type = _get_attr(officer, "jurisdiction_type") or ""
    account_status = _get_attr(officer, "account_status") or "ACTIVE"
    last_login = _get_attr(officer, "last_login") or ""
    failed_attempts = _get_attr(officer, "failed_attempts") or 0
    locked_until = _get_attr(officer, "locked_until") or ""
    created_at = (
        _get_attr(officer, "CREATEDTIME")
        or _get_attr(officer, "created_at")
    )
    updated_at = (
        _get_attr(officer, "MODIFIEDTIME")
        or _get_attr(officer, "updated_at")
    )

    d: Dict[str, Any] = {
        "ROWID": str(row_id),
        "user_id": str(catalyst_user_id),
        "name": name,
        "email": email,
        "role": role_str,
        "badge_number": badge_number,
        "station_id": str(police_station_id) if police_station_id else None,
        "district_id": str(district_id) if district_id else None,
        "jurisdiction_type": jurisdiction_type,
        "account_status": account_status,
        "last_login": last_login,
        "failed_attempts": int(failed_attempts) if failed_attempts else 0,
        "locked_until": locked_until,
        "status": account_status,
    }

    if created_at:
        d["CREATEDTIME"] = (
            created_at.isoformat()
            if hasattr(created_at, "isoformat")
            else str(created_at)
        )
    if updated_at:
        d["MODIFIEDTIME"] = (
            updated_at.isoformat()
            if hasattr(updated_at, "isoformat")
            else str(updated_at)
        )

    return d


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    if not credentials:
        raise_unauthorized("Not authenticated")

    token = credentials.credentials
    payload = verify_access_token(token)

    officer_id = payload.get("sub")
    if not officer_id:
        raise_unauthorized("Invalid token.")

    repo = CatalystOfficerRepository(request)
    officer = await repo.find_by_id(officer_id)

    if not officer:
        raise_unauthorized("Officer not found.")

    d = _build_officer_dict(officer)

    try:
        role_enum = Role(d.get("role", ""))
        perms = [p.value for p in PermissionRegistry.get_permissions(role_enum)]
    except ValueError:
        perms = []

    d["permissions"] = perms
    d["role_enum"] = role_enum if 'role_enum' in dir() else None

    token_version = payload.get("token_version", 1)
    d["token_version"] = token_version

    return d


async def get_current_officer(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return current_user


class RequirePermission:
    def __init__(self, required_permissions: list[Permission], require_all: bool = True):
        self.required_permissions = required_permissions
        self.require_all = require_all

    async def __call__(
        self,
        current_officer: Dict[str, Any] = Depends(get_current_officer),
    ) -> Dict[str, Any]:
        officer_role_str = current_officer.get("role", "")
        try:
            officer_role = Role(officer_role_str)
        except ValueError:
            raise_forbidden(f"Unknown role: {officer_role_str}")

        if self.require_all:
            if not PermissionRegistry.has_all(officer_role, self.required_permissions):
                missing = [
                    p.value for p in self.required_permissions
                    if not PermissionRegistry.has_permission(officer_role, p)
                ]
                raise_forbidden(f"Missing permissions: {missing}")
        else:
            if not PermissionRegistry.has_any(officer_role, self.required_permissions):
                raise_forbidden("No required permissions present.")

        return current_officer


def enforce_jurisdiction(officer: Dict[str, Any], target_district_id: Optional[str] = None, target_station_id: Optional[str] = None) -> None:
    role_str = officer.get("role", "")
    try:
        role = Role(role_str)
    except ValueError:
        return

    jurisdiction_type = officer.get("jurisdiction_type") or PermissionRegistry.jurisdiction_for_role(role).value

    if role == Role.SYSTEM_ADMINISTRATOR:
        return

    if jurisdiction_type == JurisdictionType.STATION.value:
        if target_station_id and officer.get("station_id") and target_station_id != officer.get("station_id"):
            raise_forbidden("Access denied: outside station jurisdiction.")
    elif jurisdiction_type == JurisdictionType.DISTRICT.value:
        if target_district_id:
            officer_district = officer.get("district_id")
            if officer_district and target_district_id != officer_district:
                raise_forbidden("Access denied: outside district jurisdiction.")
        elif target_station_id:
            officer_district = officer.get("district_id")
            if officer_district:
                raise_forbidden("Access denied: station-level query outside district jurisdiction.")
    elif jurisdiction_type == JurisdictionType.STATE.value:
        pass
