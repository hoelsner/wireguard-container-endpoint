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
    app_name: str
    app_version: str
    cors_origin: str
    cors_methods: str
    cors_headers: str
    debug: bool
    wg_config_dir: str
    wg_tmp_dir: str
    peer_tracking_timer: int

    def __init__(self):
        """
        initialize the configuration util, defaults to

            URL: http://0.0.0.0:8000
            DB_FILE_PATH: ./db.sqlite3

        """
        load_dotenv()
        self.refresh_config()

    def refresh_config(self):
        """refresh configuration instance with current environment data
        """
        self.base_data_dir = os.environ.get("DATA_DIR", ".")
        self.wg_config_dir = os.environ.get("WG_CONFIG_DIR", "/etc/wireguard")

        self.wg_tmp_dir = os.path.join(self.wg_config_dir, "tmp_files")

        self.db_url = "sqlite://{}".format(
            os.path.join(
                os.environ.get("DB_FILE_PATH", f"{self.base_data_dir}/db.sqlite3")
            )
        )
        self.debug = ConfigUtil.str_to_bool(os.environ.get("DEBUG", "False"))
        self.api_port = int(os.environ.get("APP_PORT", "8000"))
        self.api_host = os.environ.get("APP_HOST", "0.0.0.0")
        self.log_level = os.environ.get("LOG_LEVEL", "debug").upper()
        self.app_name = os.environ.get("APP_NAME", "Wireguard Docker Endpoint")
        self.app_version = os.environ.get("APP_VERSION", "undefined")
        self.cors_origin = os.environ.get("APP_CORS_ORIGIN", "*").split(",")
        self.cors_methods = os.environ.get("APP_CORS_METHODS", "*").split(",")
        self.cors_headers = os.environ.get("APP_CORS_HEADERS", "*").split(",")
        self.peer_tracking_timer = int(os.environ.get("APP_PEER_TRACKING_TIMER", "10"))

        self.db_models = [
            "models.rules",
            "models.peer",
            "models.wg_interface",
            "aerich.models"
        ]

        os.makedirs(self.base_data_dir, exist_ok=True)
        os.makedirs(self.wg_config_dir, exist_ok=True)
        os.makedirs(self.wg_tmp_dir, exist_ok=True)

    @staticmethod
    def str_to_bool(value: str) -> bool:
        """convert string to bool"""
        true_values = ["true", "1", "yes"]
        return True if value.lower() in true_values else False


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
