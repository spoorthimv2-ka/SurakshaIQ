import logging
from typing import Dict, Any
from fastapi import HTTPException, status
import zcatalyst_sdk  # type: ignore # pyrefly: ignore [missing-import]
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize Catalyst App SDK globally if needed, 
# although in advanced AppSail setups, you might initialize per request context.
# Since we are using token verification, we'll configure it.

def get_catalyst_app():
    """
    Initializes and returns the Catalyst SDK instance.
    """
    try:
        # In production AppSail, catalyst environment is injected.
        # For local development, Catalyst CLI or appropriate environment variables should be used.
        return zcatalyst_sdk.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize Catalyst SDK: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service initialization failed"
        )

def verify_catalyst_token(request: Any) -> Dict[str, Any]:
    """
    Validates a Zoho Catalyst ZSession or Auth Token against the Catalyst backend.
    Accepts the FastAPI Request object to extract Catalyst context headers/cookies.
    
    Returns a dictionary of user details (user_id, email_id, role, etc).
    """
    try:
        if settings.environment == "development" and not settings.catalyst_project_id:
             # Development mock if Catalyst is completely disconnected
             return {
                 "user_id": "test_catalyst_id_123",
                 "email_id": "officer@surakshaiq.local",
                 "role_details": {"role_name": "STATION_OFFICER"},
                 "first_name": "Test",
                 "last_name": "Officer"
             }

        # Initialize SDK with the incoming ASGI request if using Catalyst's Advanced AppSail features
        # Note: zcatalyst_sdk requires specific handling for FastAPI/ASGI requests.
        # This is a placeholder for the exact SDK integration.
        # app = zcatalyst_sdk.initialize(req=request)
        # user_management = app.user_management()
        # current_user = user_management.get_current_user() 
        # return current_user
        
        raise NotImplementedError("Catalyst SDK token verification logic requires HTTP Request Context bindings.")
        
    except Exception as e:
        logger.error(f"Catalyst token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Catalyst authentication token"
        )
