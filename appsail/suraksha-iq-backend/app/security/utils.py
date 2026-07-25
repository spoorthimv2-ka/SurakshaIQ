from typing import Dict, Any
from fastapi import HTTPException, status
import logging
import bcrypt

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

def hash_password(plain: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))