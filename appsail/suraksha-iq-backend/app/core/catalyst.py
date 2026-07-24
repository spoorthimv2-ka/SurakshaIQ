from typing import Any
from fastapi import Request
import zcatalyst_sdk
from zcatalyst_sdk.exceptions import CatalystError, CatalystAppError
from app.config.settings import settings
from app.core.exceptions import CatalystConnectionError
from app.core.logger import logger
from app.core.mock_data import get_mock_app


class CatalystManager:
    """
    Request-scoped Catalyst SDK facade.
    Uses request headers when available (AppSail / Catalyst gateway),
    and falls back to environment variable initialization for local development.
    When MOCK_CATALYST_DATA is enabled, returns mock objects instead of
    initializing the real Catalyst SDK.
    """

    def get_app(self, request: Request) -> Any:
        if settings.mock_catalyst_data:
            return get_mock_app()
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
            import traceback
            logger.error(f"Environment-based Catalyst initialization failed: {e}")
            logger.error(f"FULL TRACEBACK:\n{traceback.format_exc()}")
            raise CatalystConnectionError("Catalyst SDK initialization failed") from e
        except Exception as e:
            import traceback
            logger.error(f"Unexpected error in environment-based Catalyst init: {e}")
            logger.error(f"FULL TRACEBACK:\n{traceback.format_exc()}")
            raise CatalystConnectionError("Catalyst SDK initialization failed") from e

    def get_datastore(self, request):
        if settings.mock_catalyst_data:
            return get_mock_app().datastore()
        app = self.get_app(request)
        return app.datastore()

    def get_zcql(self, request):
        if settings.mock_catalyst_data:
            return get_mock_app().zcql()
        app = self.get_app(request)
        return app.zcql()


catalyst_manager = CatalystManager()
