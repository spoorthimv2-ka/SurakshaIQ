from typing import Dict, Any
from fastapi import Request

from app.models.enums import ROLE_PERMISSIONS_MAP, Role
from app.repositories.officer_repo import OfficerRepository
from app.repositories.catalyst_officer_repo import CatalystOfficerRepository
from app.services.officer_service import OfficerService
from app.security.jwt import create_access_token
from app.security.utils import raise_unauthorized, verify_password


class AuthService:
    """Authentication orchestration over backend JWT + Catalyst Data Store records."""

    def __init__(self, request: Request, officer_repo: OfficerRepository | None = None):
        self.request = request
        self.officer_repo = officer_repo or OfficerRepository(request)
        self.officer_service = OfficerService(request, self.officer_repo)
        self.officer_auth_repo = CatalystOfficerRepository(request)

    def _get_permissions(self, role_str: str) -> list[str]:
        try:
            role_enum = Role(role_str)
        except ValueError:
            role_enum = Role.STATION_HOUSE_OFFICER
        permissions = ROLE_PERMISSIONS_MAP.get(role_enum, [])
        return [p.value for p in permissions]

    def _get_attr(self, officer: Dict[str, Any], key: str, default=None):
        if isinstance(officer, dict):
            return officer.get(key, default)
        return getattr(officer, key, default)

    def _get_role_str(self, officer: Dict[str, Any]) -> str:
        role_val = self._get_attr(officer, "role", "")
        if isinstance(role_val, dict):
            return role_val.get("display_value") or role_val.get("label") or role_val.get("name") or ""
        return str(role_val) if role_val else ""

    def _build_officer_dict(self, officer: Dict[str, Any]) -> Dict[str, Any]:
        role_str = self._get_role_str(officer)
        row_id = self._get_attr(officer, "ROWID") or self._get_attr(officer, "row_id") or self._get_attr(officer, "id") or ""
        catalyst_user_id = self._get_attr(officer, "user_id") or self._get_attr(officer, "catalyst_user_id") or ""
        name = self._get_attr(officer, "name") or ""
        email = self._get_attr(officer, "email") or ""
        police_station_id = self._get_attr(officer, "police_station_id") or self._get_attr(officer, "station_id")
        created_at = self._get_attr(officer, "CREATEDTIME") or self._get_attr(officer, "created_at")
        updated_at = self._get_attr(officer, "MODIFIEDTIME") or self._get_attr(officer, "updated_at")

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
            d["CREATEDTIME"] = created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at)
        if updated_at:
            d["MODIFIEDTIME"] = updated_at.isoformat() if hasattr(updated_at, "isoformat") else str(updated_at)
        return d

    async def get_current_officer_from_token(self, token: str) -> Dict[str, Any]:
        from app.security.jwt import verify_access_token
        payload = verify_access_token(token)
        officer_id = payload.get("sub")
        officer = await self.officer_auth_repo.find_by_id(officer_id)
        if not officer:
            raise_unauthorized("Officer not found.")
        return self._build_officer_dict(officer)

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        officer = await self.officer_auth_repo.find_by_email(email)
        if not officer:
            raise_unauthorized("Invalid credentials.")
        hashed_password = self._get_attr(officer, "hashed_password")
        if not hashed_password:
            raise_unauthorized("Invalid credentials.")
        if not verify_password(password, hashed_password):
            raise_unauthorized("Invalid credentials.")

        role_str = self._get_role_str(officer)
        permissions = self._get_permissions(role_str)

        row_id = self._get_attr(officer, "ROWID") or self._get_attr(officer, "row_id") or self._get_attr(officer, "id") or ""
        cat_id = self._get_attr(officer, "user_id") or self._get_attr(officer, "catalyst_user_id") or ""

        payload = {
            "sub": str(row_id),
            "cat_id": str(cat_id),
            "role": role_str,
            "permissions": permissions,
        }

        access_token = create_access_token(payload)
        officer_dict = self._build_officer_dict(officer)
        officer_dict["permissions"] = permissions

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "officer": officer_dict,
        }

    async def logout(self) -> Dict[str, Any]:
        return {"message": "Successfully logged out of backend session."}
