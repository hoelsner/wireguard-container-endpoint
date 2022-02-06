import fastapi
from routers.response_models import MessageResponseModel


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
    # TODO: add healthchecks for application
    return MessageResponseModel(message="ok")
