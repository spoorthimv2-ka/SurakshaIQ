from typing import Dict, Any
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

def raise_unauthorized(detail: str = "Invalid or expired authentication credentials") -> None:
    """Raises HTTP 401 Unauthorized."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

def raise_forbidden(detail: str = "Operation not permitted") -> None:
    """Raises HTTP 403 Forbidden."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )

def get_catalyst_auth_context(catalyst_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reads and sanitizes the Catalyst authentication context.
    Returns safe user attributes.
    """
    if not catalyst_user:
        raise_unauthorized("No Catalyst authentication context found.")
    
    return {
        "user_id": catalyst_user.get("user_id"),
        "email_id": catalyst_user.get("email_id"),
        "role_details": catalyst_user.get("role_details", {}),
    }

def reject_unauthorized(catalyst_user: Dict[str, Any]) -> None:
    """
    Checks if a user context is valid; if not, rejects the request.
    """
    if not catalyst_user or not catalyst_user.get("user_id"):
        logger.warning("Rejected unauthorized request: Missing user_id in context.")
        raise_unauthorized("Authentication required.")
