import zcatalyst_sdk
from zcatalyst_sdk.exceptions import CatalystError
from app.core.exceptions import CatalystConnectionError
from app.core.logger import logger


class CatalystManager:
    _instance = None
    _initialized = False
    _is_unavailable = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self):
        if not self._initialized and not self._is_unavailable:
            try:
                zcatalyst_sdk.initialize(name="[DEFAULT]", scope=None, req=None)
                logger.info("Catalyst SDK initialized from ambient AppSail runtime context.")
                self._initialized = True
            except CatalystError:
                logger.warning(
                    "Catalyst runtime context unavailable; "
                    "falling back to local development initialization via initialize_app()."
                )
                try:
                    zcatalyst_sdk.initialize_app(name="[DEFAULT]")
                    logger.info("Catalyst SDK initialized via initialize_app() for local development.")
                    self._initialized = True
                except CatalystError as e:
                    logger.error(f"Failed to initialize Catalyst SDK locally: {e}")
                    self._is_unavailable = True
            except Exception as e:
                logger.error(f"Unexpected error initializing Catalyst SDK: {e}")
                self._is_unavailable = True

    def _get_app(self):
        if not self._initialized:
            self.initialize()
        if self._is_unavailable:
            raise CatalystConnectionError("Catalyst is currently unavailable.")
        try:
            return zcatalyst_sdk.get_app(name="[DEFAULT]")
        except CatalystError as e:
            logger.error(f"Failed to access Catalyst app instance: {e}")
            raise CatalystConnectionError("Catalyst app access failed")

    def get_datastore(self):
        app = self._get_app()
        return app.datastore

    def get_zcql(self):
        app = self._get_app()
        return app.zcql


catalyst_manager = CatalystManager()
