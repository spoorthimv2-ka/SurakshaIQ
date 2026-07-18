import logging
from app.config.settings import settings

def setup_logging():
    """
    Configures app-wide Python logging.
    No print() statements should be used in the application.
    """
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Application logging configured.")
    return logger

# Expose a default logger for the core module
logger = logging.getLogger("surakshaiq")
