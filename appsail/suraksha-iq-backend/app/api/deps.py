from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any

from app.models.enums import Role, Permission, ROLE_PERMISSIONS_MAP
from app.security.utils import raise_unauthorized, raise_forbidden
from app.security.jwt import verify_access_token
from app.repositories.catalyst_officer_repo import CatalystOfficerRepository

# Swagger/OpenAPI Bearer authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


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
        "badge_number": None,
        "status": "ACTIVE",
        "station_id": str(police_station_id) if police_station_id else None,
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
    token: str = Depends(oauth2_scheme),
) -> Dict[str, Any]:

    payload = verify_access_token(token)

    officer_id = payload.get("sub")

    if not officer_id:
        raise_unauthorized("Invalid token.")

    repo = CatalystOfficerRepository(request)

    officer = await repo.find_by_id(officer_id)

    if not officer:
        raise_unauthorized("Officer not found.")

    d = _build_officer_dict(officer)

    permissions = []

    try:
        role_enum = Role(d.get("role", ""))
        permissions = [
            p.value for p in ROLE_PERMISSIONS_MAP.get(role_enum, [])
        ]
    except ValueError:
        pass

    d["permissions"] = permissions

    return d


async def get_current_officer(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    return current_user


class RequireRole:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_officer: Dict[str, Any] = Depends(get_current_officer),
    ) -> Dict[str, Any]:

        officer_role = current_officer.get("role", "")

        if officer_role not in [r.value for r in self.allowed_roles]:
            raise_forbidden(
                f"Operation not permitted. Required roles: {[r.value for r in self.allowed_roles]}"
            )

        return current_officer


class RequirePermission:
    def __init__(self, required_permissions: list[Permission]):
        self.required_permissions = required_permissions

    async def __call__(
        self,
        current_officer: Dict[str, Any] = Depends(get_current_officer),
    ) -> Dict[str, Any]:

        officer_role_str = current_officer.get("role", "")

        try:
            officer_role = Role(officer_role_str)
        except ValueError:
            raise_forbidden(f"Unknown role: {officer_role_str}")

        officer_permissions = ROLE_PERMISSIONS_MAP.get(officer_role, [])

        for perm in self.required_permissions:
            if perm not in officer_permissions:
                raise_forbidden(
                    f"Operation not permitted. Missing permission: {perm.value}"
                )

        return current_officer