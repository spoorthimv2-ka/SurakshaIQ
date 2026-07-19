import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
import zcatalyst_sdk  # type: ignore
from app.config.settings import settings

logger = logging.getLogger(__name__)

class CatalystAuth:
    """
    Wrapper for Zoho Catalyst Authentication SDK.
    Handles initialization, session validation, and user retrieval without business logic.
    """

    @staticmethod
    def has_catalyst_headers(request: Request) -> bool:
        """
        Checks if any Catalyst specific headers are present in the request.
        """
        for header in request.headers:
            if header.lower().startswith("x-zc-") or header.lower() == "cookie":
                return True
        return False

    @staticmethod
    def get_catalyst_app(request: Optional[Request] = None):
        """
        Initializes and returns the Catalyst SDK instance.
        Returns None if Catalyst headers are missing or initialization fails.
        """
        try:
            if request:
                if not CatalystAuth.has_catalyst_headers(request):
                    logger.warning("Catalyst headers missing from request. Skipping initialization.")
                    return None
                return zcatalyst_sdk.initialize(req=request)
            return zcatalyst_sdk.initialize()
        except Exception as e:
            logger.error(f"Failed to initialize Catalyst SDK for auth: {str(e)}")
            return None

    @staticmethod
    def validate_session(request: Request) -> Dict[str, Any]:
        """
        Validates a Zoho Catalyst session using the incoming request context.
        Raises HTTP 401 or 503 if unavailable or invalid.
        """
        app = CatalystAuth.get_catalyst_app(request)
        
        if not app:
            if settings.environment == "development" and not settings.catalyst_project_id:
                # Mock response for local development without active Catalyst connection
                return {
                    "user_id": "mock_cat_123",
                    "email_id": "officer@surakshaiq.local",
                    "role_details": {"role_name": "STATION_HOUSE_OFFICER"},
                    "first_name": "Dev",
                    "last_name": "Officer"
                }
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Catalyst authentication is unavailable or headers are missing."
            )

        try:
            user_management = app.user_management()
            # This retrieves the current authenticated user details from the session
            current_user = user_management.get_current_user()
            return current_user
        except Exception as e:
            logger.error(f"Catalyst session validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Catalyst authentication session."
            )
