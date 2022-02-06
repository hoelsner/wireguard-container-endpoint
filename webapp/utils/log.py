"""
Logging Interface
"""
import logging
import logging.config
import utils.generics


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
        config = utils.config.ConfigUtil()
        self.log_config = {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
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
