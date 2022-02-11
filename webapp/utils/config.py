"""
Configuration Interface
"""
# pylint: disable=consider-using-f-string
import os
import logging
from typing import List
import distutils.dist
from dotenv import load_dotenv
import utils.generics


class ConfigUtil(metaclass=utils.generics.SingletonMeta):
    """
    Configuration Utility for the application
    """
    base_data_dir: str      # common configuration data
    db_url: str             # Database URL for Tortoise
    db_models: List[str]    # models for Tortoise
    api_port: int
    api_host: str
    log_level: str
    app_version: str
    cors_origin: str
    cors_methods: str
    cors_headers: str
    debug: bool

    def __init__(self):
        """
        initialize the configuration util, defaults to

            URL: http://0.0.0.0:8000
            DB_FILE_PATH: ./db.sqlite3

        """
        load_dotenv()
        self.base_data_dir = os.environ.get("DATA_DIR", ".")
        self.db_url = "sqlite://{}".format(
            os.path.join(
                os.environ.get("DB_FILE_PATH", "./db.sqlite3")
            )
        )
        self.db_models = [
            "models.rules",
            #"models.peer",
            "models.wg_interface",
            "aerich.models"
        ]
        self.debug = distutils.dist.strtobool(os.environ.get("DEBUG", "False"))
        self.api_port = int(os.environ.get("APP_PORT", "8000"))
        self.api_host = os.environ.get("APP_HOST", "0.0.0.0")
        self.log_level = os.environ.get("LOG_LEVEL", "debug").upper()
        self.app_version = os.environ.get("APP_VERSION", "undefined")
        self.cors_origin = os.environ.get("APP_CORS_ORIGIN", "*").split(",")
        self.cors_methods = os.environ.get("APP_CORS_METHODS", "*").split(",")
        self.cors_headers = os.environ.get("APP_CORS_HEADERS", "*").split(",")


# required for aerich migrations
_config_instance = ConfigUtil()
TORTOISE_ORM = {
    "connections": {
        "default": _config_instance.db_url
    },
    "apps": {
        "models": {
            "models": _config_instance.db_models,
            "default_connection": "default",
        },
    },
}
