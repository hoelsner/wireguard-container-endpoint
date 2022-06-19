"""
Configuration Interface
"""
# pylint: disable=consider-using-f-string
import os
import uuid
from typing import List
from dotenv import load_dotenv
import utils.generics


class InitConfigUtil():
    """
    Initial Configuration Utility for the application
    """
    intf_name: str                      # wireguard interface name
    intf_listen_port: int               # listen port for wireguard
    intf_private_key: int               # private key to use
    intf_cidr_addresses: str            # CIDR addresses on the wireguard interface

    policy_name: str                    # name for the policy
    policy_nat_enable: bool             # True if NAT should be enabled, otherwise False
    policy_nat_intf: str                # Interface for NAT
    policy_allow_admin: bool            # True if the access to the HTTP API should be possible via VPN

    peer_public_key: str                # public key for the peer
    peer_preshared_key: str             # (optional) preshared key for the peer connection
    peer_persistent_keepalive: int      # keepalive for the initial peer
    peer_endpoint: str                  # endpoint name and port number for the peer
    peer_cidr_routes: str               # routes that should be applied to the peer

    def __init__(self):
        """
        load values
        """
        load_dotenv()
        self.intf_name = os.environ.get("INIT_INTF_NAME", "")
        self.intf_listen_port = int(os.environ.get("INIT_INTF_LISTEN_PORT", "51820"))
        self.intf_private_key = os.environ.get("INIT_INTF_PRIVATE_KEY", "")
        self.intf_cidr_addresses = os.environ.get("INIT_INTF_CIDR_ADDRESSES", "")
        self.policy_name = os.environ.get("INIT_POLICY_NAME", "base policy")
        self.policy_nat_enable = ConfigUtil.str_to_bool(os.environ.get("INIT_POLICY_NAT_ENABLE", "False"))
        self.policy_nat_intf = os.environ.get("INIT_POLICY_NAT_INTF", "")
        self.policy_allow_admin = ConfigUtil.str_to_bool(os.environ.get("INIT_POLICY_ALLOW_ADMIN", "True"))
        self.peer_public_key = os.environ.get("INIT_PEER_PUBLIC_KEY", "")
        self.peer_preshared_key = os.environ.get("INIT_PEER_PRE_SHARED_KEY", None)
        self.peer_persistent_keepalive = int(os.environ.get("INIT_PEER_PERSISTENT_KEEPALIVE", "30"))
        self.peer_endpoint = os.environ.get("INIT_PEER_ENDPOINT", "")
        self.peer_cidr_routes = os.environ.get("INIT_PEER_CIDR_ROUTES", "")

    def has_init_config(self) -> bool:
        """is initial configuration given?

        :return: _description_
        :rtype: bool
        """
        return self.intf_name != ""


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
    admin_user: str
    admin_password_file: str

    def __init__(self):
        """
        initialize the configuration util, defaults to

            URL: http://0.0.0.0:8000
            DB_FILE_PATH: ./db.sqlite3

        """
        load_dotenv()
        self.refresh_config()

    @property
    def admin_password(self) -> str:
        """admin password
        """
        value = os.environ.get("APP_ADMIN_PASSWORD", None)

        # if not set, create a password and write to backup file
        if value is None:
            if os.path.exists(self.admin_password_file):
                with open(self.admin_password_file, encoding="utf-8") as f:
                    value = f.read()

            else:
                with open(self.admin_password_file, "w", encoding="utf-8") as f:
                    value = str(uuid.uuid4())
                    f.write(value)

        return value

    def refresh_config(self):
        """refresh configuration instance with current environment data
        """
        self.base_data_dir = os.environ.get("DATA_DIR", ".")
        self.wg_config_dir = os.environ.get("WG_CONFIG_DIR", "/etc/wireguard")

        self.wg_tmp_dir = os.path.join(self.wg_config_dir, "tmp_files")
        self.admin_password_file = os.path.join(self.base_data_dir, ".generated_password")

        self.db_url = "sqlite://{}".format(
            os.path.join(
                os.environ.get("DB_FILE_PATH", f"{self.base_data_dir}/db.sqlite3")
            )
        )
        self.debug = ConfigUtil.str_to_bool(os.environ.get("DEBUG", "False"))
        self.api_port = int(os.environ.get("APP_PORT", "8000"))
        self.api_host = os.environ.get("APP_HOST", "0.0.0.0")
        self.log_level = os.environ.get("LOG_LEVEL", "debug").upper()
        self.app_name = os.environ.get("APP_NAME", "Wireguard Container Endpoint")
        self.app_version = os.environ.get("APP_VERSION", "undefined")
        self.cors_origin = os.environ.get("APP_CORS_ORIGIN", "*").split(",")
        self.cors_methods = os.environ.get("APP_CORS_METHODS", "*").split(",")
        self.cors_headers = os.environ.get("APP_CORS_HEADERS", "*").split(",")
        self.peer_tracking_timer = int(os.environ.get("APP_PEER_TRACKING_TIMER", "10"))
        self.admin_user = os.environ.get("APP_ADMIN_USER", "admin")

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
