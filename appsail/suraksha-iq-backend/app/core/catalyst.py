from typing import Any
from fastapi import Request
import zcatalyst_sdk
from zcatalyst_sdk.exceptions import CatalystError
from app.core.exceptions import CatalystConnectionError
from app.core.logger import logger


class CatalystManager:
    """
    Request-scoped Catalyst SDK facade.
    Initializes the SDK per HTTP request using the incoming ASGI request context.
    """

    def get_app(self, request: Request) -> Any:
        """Initializes and returns a Catalyst application instance for the given request."""
        try:
            return zcatalyst_sdk.initialize(req=request)
        except CatalystError as e:
            logger.error(f"Failed to initialize Catalyst SDK for request: {e}")
            raise CatalystConnectionError("Catalyst SDK initialization failed") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing Catalyst SDK: {e}")
            raise CatalystConnectionError("Catalyst SDK initialization failed") from e

    def get_datastore(self, request):
        app = self.get_app(request)
        return app.datastore()

    def get_zcql(self, request):
        app = self.get_app(request)
        return app.zcql()


catalyst_manager = CatalystManager()
