from typing import Dict, Any
from fastapi import Request

from app.models.enums import Role, JurisdictionType
from app.authorization.permissions import PermissionRegistry
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
        permissions = PermissionRegistry.get_permissions(role_enum)
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

    async def login(self, badge_number: str, password: str) -> Dict[str, Any]:
        officer = await self.officer_auth_repo.find_by_badge_number(badge_number)
        if not officer:
            raise_unauthorized("Invalid credentials.")

        account_status = self._get_attr(officer, "account_status", "ACTIVE")
        if account_status != "ACTIVE":
            raise_unauthorized("Account is inactive or locked.")

        locked_until = self._get_attr(officer, "locked_until")
        if locked_until:
            try:
                from datetime import datetime
                if datetime.fromisoformat(locked_until) > datetime.now(datetime.now().astimezone().tzinfo):
                    raise_unauthorized("Account is temporarily locked due to too many failed attempts.")
            except Exception:
                pass

        hashed_password = self._get_attr(officer, "hashed_password")
        if not hashed_password:
            raise_unauthorized("Invalid credentials.")
        if not verify_password(password, hashed_password):
            await self.increment_failed_attempts(officer)
            raise_unauthorized("Invalid credentials.")

        await self.reset_failed_attempts(officer)
        await self.update_last_login(officer)

        role_str = self._get_role_str(officer)
        permissions = self._get_permissions(role_str)

        row_id = self._get_attr(officer, "ROWID") or self._get_attr(officer, "row_id") or self._get_attr(officer, "id") or ""
        cat_id = self._get_attr(officer, "user_id") or self._get_attr(officer, "catalyst_user_id") or ""
        badge_number_val = self._get_attr(officer, "badge_number") or ""
        police_station_id = self._get_attr(officer, "police_station_id") or self._get_attr(officer, "station_id")
        district_id = self._get_attr(officer, "district_id") or ""
        jurisdiction_type = self._get_attr(officer, "jurisdiction_type") or ""
        token_version = 1

        try:
            role_enum = Role(role_str)
            state_access = PermissionRegistry.jurisdiction_for_role(role_enum) == JurisdictionType.STATE
        except ValueError:
            state_access = False

        payload = {
            "sub": str(row_id),
            "cat_id": str(cat_id),
            "badge_number": str(badge_number_val),
            "role": role_str,
            "permissions": permissions,
            "jurisdiction_type": jurisdiction_type,
            "station_id": str(police_station_id) if police_station_id else None,
            "district_id": str(district_id) if district_id else None,
            "state_access": state_access,
            "token_version": token_version,
        }

        access_token = create_access_token(payload)
        officer_dict = self._build_officer_dict(officer)
        officer_dict["permissions"] = permissions
        officer_dict["state_access"] = state_access
        officer_dict["token_version"] = token_version

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "officer": officer_dict,
        }

    async def increment_failed_attempts(self, officer: Dict[str, Any]) -> None:
        row_id = self._get_attr(officer, "ROWID") or self._get_attr(officer, "row_id") or self._get_attr(officer, "id")
        if not row_id:
            return
        current_attempts = self._get_attr(officer, "failed_attempts", 0)
        try:
            current_attempts = int(current_attempts)
        except (TypeError, ValueError):
            current_attempts = 0
        update_data: Dict[str, Any] = {"failed_attempts": current_attempts + 1}
        if current_attempts + 1 >= 5:
            update_data["account_status"] = "LOCKED"
            from datetime import datetime, timezone, timedelta
            locked_until = datetime.now(timezone.utc).__add__(timedelta(minutes=15)).isoformat()
            update_data["locked_until"] = locked_until
        update_data["ROWID"] = row_id
        self.officer_repo.get_table().update_row(update_data)

    async def reset_failed_attempts(self, officer: Dict[str, Any]) -> None:
        row_id = self._get_attr(officer, "ROWID") or self._get_attr(officer, "row_id") or self._get_attr(officer, "id")
        if not row_id:
            return
        self.officer_repo.get_table().update_row({
            "ROWID": row_id,
            "failed_attempts": 0,
            "account_status": "ACTIVE",
            "locked_until": None,
        })

    async def update_last_login(self, officer: Dict[str, Any]) -> None:
        row_id = self._get_attr(officer, "ROWID") or self._get_attr(officer, "row_id") or self._get_attr(officer, "id")
        if not row_id:
            return
        from datetime import datetime, timezone
        last_login = datetime.now(timezone.utc).isoformat()
        self.officer_repo.get_table().update_row({
            "ROWID": row_id,
            "last_login": last_login,
        })

    async def logout(self) -> Dict[str, Any]:
        return {"message": "Successfully logged out of backend session."}
