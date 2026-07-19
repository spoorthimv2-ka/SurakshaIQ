from fastapi import APIRouter, Depends, Request, HTTPException, status
from typing import Dict, Any

from app.services.auth_service import AuthService
from app.schemas.officer import OfficerResponse
from app.models.enums import ROLE_PERMISSIONS_MAP, Role, Permission
from app.api.deps import get_current_officer, RequirePermission, get_auth_service

router = APIRouter()

@router.post("/verify-catalyst")
async def verify_catalyst_session(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """
    1. Verifies the incoming Catalyst session/token.
    2. Syncs/provisions the Officer in Catalyst Data Store.
    3. Catalyst SDK manages sessions, so we just return a dummy token to preserve backward compatibility for schema.
    """
    officer = await auth_service.login_validation(request)
    
    return {
        "access_token": "catalyst_session_active",
        "token_type": "bearer",
        "officer": officer
    }

@router.post("/logout")
async def logout(request: Request):
    """
    Tears down the backend session. 
    Since JWTs are stateless, actual invalidation happens on the client by deleting the token.
    """
    return {"message": "Successfully logged out of backend session."}

@router.get("/me")
async def read_users_me(
    current_officer: Dict[str, Any] = Depends(get_current_officer)
):
    """
    Returns the currently authenticated officer.
    Guarded by `get_current_officer` which validates the JWT token.
    """
    return current_officer

@router.get("/sensitive-data")
async def read_sensitive_data(
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.VIEW_PII]))
):
    """
    Example protected route guarded by Permission checking.
    Only roles with VIEW_PII permission will succeed.
    """
    return {"message": "You have access to sensitive PII.", "officer_id": current_officer.get("ROWID")}
