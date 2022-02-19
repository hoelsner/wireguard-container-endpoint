"""
Logging Interface
"""
import logging
import logging.config
import utils.generics
from utils.config import ConfigUtil


class LoggingUtil(metaclass=utils.generics.SingletonMeta):
    """
    simple logging utility
    """
    log_config: dict = None
    logger: logging.Logger

    def __init__(self):
        """
        initialize logging configuration
        """
        config = ConfigUtil()
        format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        if config.debug:
            # use a more expressive debugger when debug mode is enabled
            format_string = "%(relativeCreated)s | %(name)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s"

        self.log_config = {
            "version": 1,
            "formatters": {
                "default": {
                    "format": format_string
                }
            },
            "handlers": {
                "console": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "level": config.log_level
                }
            },
            "root": {
                    "handlers": ["console"],
                    "level": config.log_level
            },
            "loggers": {
                "applog": {
                    "propagate": True
                },
                "wg_adapter": {
                    "propagate": True
                },
                "wg_sysinfo": {
                    "propagate": True
                },
                "peer_tracking": {
                    "propagate": True
                },
                "aiosqlite": {
                    "level": "INFO",
                    "propagate": True
                },
                "uvicorn": {
                    "propagate": True
                },
                "uvicorn.access": {
                    "propagate": True
                },
                "tortoise": {
                    "propagate": True,
                    "level": "WARN",
                },
                "tortoise.db_client": {
                    "propagate": True,
                    "level": "WARN",
                }
            }
        }
        # update logging configuration
        logging.config.dictConfig(self.log_config)
        self.logger = logging.getLogger("applog")
