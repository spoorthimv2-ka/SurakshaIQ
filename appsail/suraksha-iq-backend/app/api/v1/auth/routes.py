from fastapi import APIRouter, Request, Depends
from typing import Dict, Any

from app.services.auth_service import AuthService
from app.models.enums import Permission
from app.api.deps import get_current_officer, RequirePermission
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

router = APIRouter()

@router.post("/login")
async def login(
    request: Request,
    body: LoginRequest,
) -> Dict[str, Any]:
    auth_service = AuthService(request)
    officer = await auth_service.login(body.email, body.password)
    return officer

@router.post("/logout")
async def logout(request: Request):
    auth_service = AuthService()
    await auth_service.logout()
    return {"message": "Successfully logged out of backend session."}

@router.get("/me")
async def read_users_me(
    request: Request,
    current_officer: Dict[str, Any] = Depends(get_current_officer)
):
    return current_officer

@router.get("/sensitive-data")
async def read_sensitive_data(
    request: Request,
    current_officer: Dict[str, Any] = Depends(RequirePermission([Permission.VIEW_PII]))
):
    return {"message": "You have access to sensitive PII.", "officer_id": current_officer.get("ROWID")}
