from typing import Dict, Any, Optional
from fastapi import Request

from app.models.enums import ROLE_PERMISSIONS_MAP, Role
from app.repositories.officer_repo import OfficerRepository
from app.services.officer_service import OfficerService
from app.auth.catalyst_auth import CatalystAuth


class AuthService:
    """Authentication orchestration over Catalyst-backed officer records."""

    def __init__(self, officer_repo: OfficerRepository | None = None):
        self.officer_repo = officer_repo or OfficerRepository()
        self.officer_service = OfficerService(self.officer_repo)

    async def validate_session(self, request: Request) -> Dict[str, Any]:
        """
        Validates the Catalyst session via SDK and returns Catalyst user identity.
        """
        catalyst_identity = CatalystAuth.validate_session(request)
        return catalyst_identity

    async def get_current_user(self, request: Request) -> Dict[str, Any]:
        """
        Validates the session and syncs/retrieves the user from the repository.
        Maps Catalyst User -> SurakshaIQ Role.
        """
        catalyst_identity = await self.validate_session(request)
        
        # Sync identity to ensure the officer exists in our Data Store
        officer = await self.officer_service.sync_catalyst_identity(catalyst_identity)

        # Map role
        officer_role_str = officer.get("role", "STATION_HOUSE_OFFICER")
        try:
            role_enum = Role(officer_role_str)
        except ValueError:
            role_enum = Role.STATION_HOUSE_OFFICER

        permissions = ROLE_PERMISSIONS_MAP.get(role_enum, [])
        officer["permissions"] = [p.value for p in permissions]

        return officer

    async def login_validation(self, request: Request) -> Dict[str, Any]:
        """
        Validates login by ensuring a valid session exists.
        Returns the officer profile.
        """
        return await self.get_current_user(request)

    async def logout(self) -> None:
        """
        Logout is handled by Catalyst frontend SDKs, but this can serve as a hook
        for any backend cleanup if necessary.
        """
        pass

