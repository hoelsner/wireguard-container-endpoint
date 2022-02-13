"""
FastAPI router for common utilities
"""
import fastapi
import utils.wireguard
import utils.config


utility_router = fastapi.APIRouter()


@utility_router.get("/instance/info")
def get_instance_info():
    """return certin information about the application instance
    """
    config = utils.config.ConfigUtil()
    return {
        "version": config.app_version,
        "debug": config.debug
    }


@utility_router.post("/wg/generate/privkey")
def generate_privkey():
    """return a new private key
    """
    return {
        "private_key": utils.wireguard.WgKeyUtils().generate_private_key()
    }


@utility_router.post("/wg/generate/presharedkey")
def generate_presharedkey():
    """generate a new preshared key
    """
    return {
        "preshared_key": utils.wireguard.WgKeyUtils().generate_preshared_key()
    }


utility_router.get("/wg/operational")
def get_wg_operational_data():
    """get raw response from the wireguard json module
    """
    return utils.wireguard.WgSystemInfo().get_wg_json()
