from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.api.deps import get_db_session
from app.auth.catalyst_verifier import verify_catalyst_token
from app.services.officer_service import OfficerService
from app.security.jwt import create_access_token
from app.schemas.officer import OfficerResponse
from app.models.enums import ROLE_PERMISSIONS_MAP

router = APIRouter()

@router.post("/verify-catalyst")
async def verify_catalyst_session(
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    1. Verifies the incoming Catalyst session/token.
    2. Syncs/provisions the Officer in the backend database.
    3. Issues a short-lived localized JWT for subsequent API calls.
    """
    # 1. Verify Catalyst Identity
    catalyst_identity = verify_catalyst_token(request)
    
    # 2. Sync with local database (creates Officer on first login)
    officer = await OfficerService.sync_catalyst_identity(session, catalyst_identity)
    
    # 3. Create Backend JWT Session
    permissions = ROLE_PERMISSIONS_MAP.get(officer.role, [])
    
    token_payload = {
        "sub": str(officer.id),
        "cat_id": officer.catalyst_user_id,
        "role": officer.role.value if hasattr(officer.role, 'value') else str(officer.role),
        "permissions": [p.value for p in permissions]
    }
    
    access_token = create_access_token(token_payload)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "officer": OfficerResponse.model_validate(officer).model_dump()
    }

@router.post("/logout")
async def logout(request: Request):
    """
    Tears down the backend session. 
    Since JWTs are stateless, actual invalidation happens on the client by deleting the token,
    or via a token blocklist (if implemented later).
    """
    # [Task 2 Integration Point: Add token blocklist or Redis session invalidation here]
    return {"message": "Successfully logged out of backend session."}

from app.api.deps import get_current_officer, RequirePermission
from app.models.enums import Permission
from app.models.officer import Officer

@router.get("/me", response_model=OfficerResponse)
async def read_users_me(
    current_officer: Officer = Depends(get_current_officer)
):
    """
    Returns the currently authenticated officer. 
    Guarded by `get_current_officer` which validates the JWT token.
    """
    return current_officer

@router.get("/sensitive-data")
async def read_sensitive_data(
    current_officer: Officer = Depends(RequirePermission([Permission.VIEW_PII]))
):
    """
    Example protected route guarded by Permission checking.
    Only roles with VIEW_PII permission will succeed.
    """
    return {"message": "You have access to sensitive PII.", "officer_id": current_officer.id}
