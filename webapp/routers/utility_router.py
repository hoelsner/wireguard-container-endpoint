"""
FastAPI router for common utilities
"""
import fastapi
import pythonping

from routers.response_models import PingResponseModel
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
        "name": config.app_name,
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


@utility_router.get("/wg/operational")
async def get_wg_operational_data():
    """get raw response from the wireguard json module
    """
    data = await utils.wireguard.WgSystemInfoAdapter().get_wg_json()
    for interfaces in data.keys():
        del data[interfaces]["privateKey"]

    return data


@utility_router.post(
    "/ping/{hostname}",
    response_model=PingResponseModel
)
async def post_ping(hostname: str):
    """send a ping to the given station and return True, if successful
    """
    config = utils.config.ConfigUtil()
    response = pythonping.ping(hostname, timeout=1, count=4, verbose=config.debug)
    return PingResponseModel(
        success=response.success(),
        rtt_avg=response.rtt_avg,
        rtt_avg_ms=response.rtt_avg_ms,
        rtt_max=response.rtt_max,
        rtt_max_ms=response.rtt_max_ms,
        rtt_min=response.rtt_min,
        rtt_min_ms=response.rtt_min_ms,
    )
