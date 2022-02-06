"""
Configuration Interface
"""
# pylint: disable=consider-using-f-string
import os
from typing import List
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

    def __init__(self):
        """
        initialize the configuration util, defaults to

            URL: http://0.0.0.0:8000
            DB File: ./db.sqlite3

        """
        load_dotenv()
        self.base_data_dir = os.environ.get("DATA_DIR", ".")
        self.db_url = "sqlite://{}".format(
            os.path.join(
                self.base_data_dir,
                os.environ.get("DB_FILENAME", "db.sqlite3")
            )
        )
        self.db_models = [
            "models",
            "aerich.models"
        ]
        self.api_port = int(os.environ.get("APP_PORT", "8000"))
        self.api_host = os.environ.get("APP_HOST", "0.0.0.0")
        self.log_level = os.environ.get("LOG_LEVEL", "info").upper()
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
