"""
FastAPI router for common utilities
"""
import fastapi
import pythonping
import requests

import app.auth
from routers.response_models import PingResponseModel, DetailMessageResponseModel, UrlRequestModel, UrlResponseModel
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


@utility_router.post(
    "/wg/generate/privkey",
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
def generate_privkey(username: str = fastapi.Depends(app.auth.get_current_username)):
    """return a new private key
    """
    return {
        "private_key": utils.wireguard.WgKeyUtils().generate_private_key()
    }


@utility_router.post(
    "/wg/generate/presharedkey",
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
def generate_presharedkey(username: str = fastapi.Depends(app.auth.get_current_username)):
    """generate a new preshared key
    """
    return {
        "preshared_key": utils.wireguard.WgKeyUtils().generate_preshared_key()
    }


@utility_router.get(
    "/wg/operational",
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_wg_operational_data(username: str = fastapi.Depends(app.auth.get_current_username)):
    """get raw response from the wireguard json module
    """
    data = await utils.wireguard.WgSystemInfoAdapter().get_wg_json()
    for interfaces in data.keys():
        del data[interfaces]["privateKey"]

    return data


@utility_router.post(
    "/ping/{hostname}",
    response_model=PingResponseModel,
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def post_ping(hostname: str, username: str = fastapi.Depends(app.auth.get_current_username)):
    """send a ping to the given station and return True, if successful
    """
    logger = utils.log.LoggingUtil().logger
    config = utils.config.ConfigUtil()
    try:
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

    except Exception as ex:
        logger.info(f"ping test failed for{hostname}: {str(ex)}", exc_info=True)
        return PingResponseModel(
            success=False,
            rtt_avg=-1,
            rtt_avg_ms=-1,
            rtt_max=-1,
            rtt_max_ms=-1,
            rtt_min=-1,
            rtt_min_ms=-1,
        )


@utility_router.post(
    "/http/get/",
    response_model=UrlResponseModel,
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def post_get_url(data: UrlRequestModel, username: str = fastapi.Depends(app.auth.get_current_username)):
    """perform a HTTP get operation on the given URL and returns the text
    """
    logger = utils.log.LoggingUtil().logger
    try:
        response = requests.get(data.url, verify=data.ssl_verify, timeout=3)
        return UrlResponseModel(
            content=response.text,
            status=response.status_code
        )

    except Exception as ex:
        logger.info(f"HTTP get test failed for {data}: {str(ex)}", exc_info=True)
        return UrlResponseModel(
            content="destination not reachable",
            status=500
        )
