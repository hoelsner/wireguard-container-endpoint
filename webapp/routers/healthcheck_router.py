import fastapi
from fastapi.exceptions import HTTPException
from routers.response_models import MessageResponseModel

import utils.wireguard
import utils.log


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

    # verify wireguard dependency on the underlying system
    try:
        utils.wireguard.WgKeyUtils().generate_private_key()
        utils.wireguard.WgKeyUtils().generate_preshared_key()

    except utils.wireguard.WgKeyUtilsException as ex:
        logger.error(f"Unable to generate keys for wireguard: {ex}")
        raise HTTPException(status_code=500, detail="healthcheck for wireguard failed")

    return MessageResponseModel(message="ok")
