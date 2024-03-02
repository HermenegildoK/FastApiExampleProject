import logging
from typing import Optional

from simple_example.web_app_example.logger import get_standard_logger
from simple_example.web_app_example.settings import Settings

logger: Optional[logging.Logger] = None


def init_app_globals(settings: Settings) -> None:
    global logger
    if logger is None:
        logger = get_standard_logger(
            name=f"application:{settings.APP_NAME}", log_settings=settings.LOGGING
        )
    logger.info("Log setup done")
