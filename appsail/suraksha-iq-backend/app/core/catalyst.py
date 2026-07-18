import zcatalyst_sdk
from zcatalyst_sdk.exceptions import CatalystError
from app.config.settings import settings
from app.core.exceptions import CatalystConnectionError
from app.core.logger import logger

class CatalystManager:
    """
    Singleton wrapper for Zoho Catalyst SDK initialization and core accessors.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CatalystManager, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        """Initializes the Zoho Catalyst SDK if not already initialized."""
        if not self._initialized:
            try:
                # AppSail environments natively inject Catalyst context, but we provide a fallback
                # or explicit init if credentials are set in settings (for local testing).
                if settings.catalyst_project_id:
                    zcatalyst_sdk.initialize(
                        project_id=settings.catalyst_project_id,
                        environment=settings.catalyst_environment,
                        app_key=settings.catalyst_app_key,
                        app_secret=settings.catalyst_app_secret
                    )
                    logger.info("Catalyst SDK initialized with explicit credentials.")
                else:
                    zcatalyst_sdk.initialize()
                    logger.info("Catalyst SDK initialized using ambient environment variables.")
                self._initialized = True
            except CatalystError as e:
                logger.error(f"Failed to initialize Catalyst SDK: {e}")
                raise CatalystConnectionError(str(e))
            except Exception as e:
                logger.error(f"Unexpected error initializing Catalyst SDK: {e}")
                raise CatalystConnectionError("Unexpected initialization error")

    def get_datastore(self):
        """Returns the Catalyst Data Store client."""
        if not self._initialized:
            self.initialize()
        try:
            return zcatalyst_sdk.datastore()
        except CatalystError as e:
            logger.error(f"Failed to access Catalyst Data Store: {e}")
            raise CatalystConnectionError("Data Store access failed")

    def get_zcql(self):
        """Returns the Catalyst ZCQL client for complex queries."""
        if not self._initialized:
            self.initialize()
        try:
            return zcatalyst_sdk.zcql()
        except CatalystError as e:
            logger.error(f"Failed to access Catalyst ZCQL: {e}")
            raise CatalystConnectionError("ZCQL access failed")

catalyst_manager = CatalystManager()
