from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres.connection import get_db

async def get_db_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    """
    Centralized dependency for injecting the AsyncSession into API routes.
    Use this as: `session: AsyncSession = Depends(get_db_session)`
    """
    return session

from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security.jwt import verify_access_token, TokenPayload
from app.repositories.officer_repo import OfficerRepository
from app.models.officer import Officer
from app.models.enums import Role, Permission

oauth2_scheme = HTTPBearer()

async def get_current_officer(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session)
) -> Officer:
    """
    Validates the JWT token, checks expiration, and retrieves the Officer from DB.
    Throws 401 if token is invalid or officer doesn't exist/is deleted.
    """
    token_payload_dict = verify_access_token(credentials.credentials)
    token_data = TokenPayload(**token_payload_dict)
    
    officer = await OfficerRepository.get_by_catalyst_id(session, token_data.cat_id)
    if not officer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Officer not found or deactivated.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return officer

class RequireRole:
    """
    Dependency class to enforce Role-based access control.
    """
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_officer: Officer = Depends(get_current_officer)) -> Officer:
        if current_officer.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {[r.value for r in self.allowed_roles]}"
            )
        return current_officer

class RequirePermission:
    """
    Dependency class to enforce Permission-based access control.
    Uses the centralized ROLE_PERMISSIONS_MAP to determine if the officer has the permission.
    """
    def __init__(self, required_permissions: list[Permission]):
        self.required_permissions = required_permissions

    async def __call__(self, current_officer: Officer = Depends(get_current_officer)) -> Officer:
        from app.models.enums import ROLE_PERMISSIONS_MAP
        officer_permissions = ROLE_PERMISSIONS_MAP.get(current_officer.role, [])
        
        for perm in self.required_permissions:
            if perm not in officer_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Operation not permitted. Missing permission: {perm.value}"
                )
        return current_officer
