from typing import Any
from fastapi import Request
import zcatalyst_sdk
from zcatalyst_sdk.exceptions import CatalystError, CatalystAppError
from app.core.exceptions import CatalystConnectionError
from app.core.logger import logger


class CatalystManager:
    """
    Request-scoped Catalyst SDK facade.
    Uses request headers when available (AppSail / Catalyst gateway),
    and falls back to environment variable initialization for local development.
    """

    def get_app(self, request: Request) -> Any:
        """Initializes and returns a Catalyst application instance for the given request."""
        try:
            return zcatalyst_sdk.initialize(req=request)
        except CatalystError as e:
            logger.warning(f"Request-scoped Catalyst init failed: {e}. Falling back to env-based init.")
            return self._init_from_env()
        except Exception as e:
            logger.warning(f"Unexpected error in request-scoped Catalyst init: {e}. Falling back to env-based init.")
            return self._init_from_env()

    def _init_from_env(self) -> Any:
        """Initializes Catalyst SDK from environment variables (local development fallback)."""
        try:
            return zcatalyst_sdk.initialize_app()
        except CatalystError as e:
            logger.error(f"Environment-based Catalyst initialization failed: {e}")
            raise CatalystConnectionError("Catalyst SDK initialization failed") from e
        except Exception as e:
            logger.error(f"Unexpected error in environment-based Catalyst init: {e}")
            raise CatalystConnectionError("Catalyst SDK initialization failed") from e

    def get_datastore(self, request):
        app = self.get_app(request)
        return app.datastore()

    def get_zcql(self, request):
        app = self.get_app(request)
        return app.zcql()


catalyst_manager = CatalystManager()
