import os

import fastapi
from fastapi.exceptions import HTTPException
from routers.response_models import MessageResponseModel

import utils.wireguard
import utils.log
import utils.config


healthcheck_router = fastapi.APIRouter()


@healthcheck_router.get(
    "/",
    responses={
        200: {"description": "healthcheck was successful"},
        500: {"description": "healthcheck failed, instance broken or misconfigured"}
    },
    response_model=MessageResponseModel
)
async def healthcheck():
    """
    healtcheck API endpoint for the application
    """
    logger = utils.log.LoggingUtil().logger
    config = utils.config.ConfigUtil()

    # verify wireguard dependency on the underlying system
    try:
        utils.wireguard.WgKeyUtils().generate_private_key()
        utils.wireguard.WgKeyUtils().generate_preshared_key()

    except utils.wireguard.WgKeyUtilsException as ex:
        logger.error(f"Unable to generate keys for wireguard: {ex}")
        raise HTTPException(status_code=500, detail="healthcheck for wireguard failed")

    # test wg-json
    try:
        await utils.wireguard.WgSystemInfoAdapter().get_wg_json()

    except utils.wireguard.WgSystemInfoException as ex:
        logger.error(f"unable to get operational state of wireguard: {ex}")
        raise HTTPException(status_code=500, detail="healthcheck for wg-json failed")

    # verify permissions on the data directories
    directories = [
        config.base_data_dir,
        config.wg_config_dir,
        config.wg_tmp_dir,
    ]
    for dir in directories:
        if not os.access(dir, os.W_OK):
            logger.error(f"unabe to write data to configuration directory")
            raise HTTPException(status_code=500, detail="directory permission check failed")

    return MessageResponseModel(message="ok")
