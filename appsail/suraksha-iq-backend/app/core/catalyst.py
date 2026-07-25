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
            logger.info("Database using MockApp")
            return get_mock_app()
        try:
            app = zcatalyst_sdk.initialize(req=request)
            logger.info("Database using Catalyst datastore")
            return app
        except CatalystError as e:
            logger.warning(f"Request-scoped Catalyst init failed: {e}. Falling back to env-based init.")
            return self._init_from_env()
        except Exception as e:
            logger.warning(f"Unexpected error in request-scoped Catalyst init: {e}. Falling back to env-based init.")
            return self._init_from_env()

    def _init_from_env(self) -> Any:
        """Initializes Catalyst SDK from environment variables (local development fallback)."""
        try:
            app = zcatalyst_sdk.initialize_app()
            logger.info("Database using Catalyst runtime")
            return app
        except (CatalystError, Exception) as e:
            import traceback
            logger.error(f"Environment-based Catalyst initialization failed: {e}")
            logger.error(f"FULL TRACEBACK:\n{traceback.format_exc()}")
            logger.warning("Catalyst SDK unavailable. Falling back to mock Catalyst data.")
            return get_mock_app()

    def get_app_for_ai(self, request: Request) -> Any:
        """Initialize a real Catalyst SDK app for AI/QuickML.

        This path NEVER returns MockApp, even when mock_catalyst_data is enabled.
        The AI client needs real credentials for AuthorizedHttpClient.

        Returns None if SDK initialization fails, allowing AI fallback behaviour.
        """
        try:
            app = zcatalyst_sdk.initialize(req=request)
            logger.info("AI using real Catalyst SDK")
            return app
        except CatalystError as e:
            logger.warning(f"Request-scoped Catalyst init for AI failed: {e}. Falling back to env-based init.")
            try:
                app = zcatalyst_sdk.initialize_app()
                logger.info("AI using Catalyst runtime")
                return app
            except (CatalystError, Exception) as env_err:
                import traceback
                logger.error(f"Environment-based Catalyst initialization for AI failed: {env_err}")
                logger.error(f"FULL TRACEBACK:\n{traceback.format_exc()}")
                logger.warning("AI SDK unavailable. Falling back to local intelligence.")
                return None
        except Exception as e:
            logger.warning(f"Unexpected error in AI Catalyst init: {e}")
            return None

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
