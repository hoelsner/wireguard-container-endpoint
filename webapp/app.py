"""
Start the Wireguard Container Endpoint (WGCE)
"""
import tortoise
from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from tortoise.exceptions import ValidationError,  DoesNotExist, IntegrityError

import routers.healthcheck_router
import routers.rules_router
from utils.config import ConfigUtil
from utils.log import LoggingUtil


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """return HTTP 422 for data validation errors"""
    LoggingUtil().logger.debug("RequestValidationError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


async def tortoise_validation_exception_handler(request: Request, exc: ValidationError):
    """validation error for tortoise"""
    LoggingUtil().logger.debug("RequestValidationError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": [{"msg": str(exc), "body": "ValidationError"}]})
    )


async def tortoise_valueerror_exception_handler(request: Request, exc: ValueError):
    """exception handler to handle enum validation errors from tortoise correct"""
    LoggingUtil().logger.debug("RequestValidationError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": [{"msg": str(exc), "body": "ValidationError"}]})
    )


async def tortoise_doesnotexist_exception_handler(request: Request, exc: DoesNotExist):
    """does not exists exception handler to catch errors from tortoise"""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


async def tortoise_integrityerror_exception_handler(request: Request, exc: IntegrityError):
    """integrity error exception handler to catch errors from tortoise"""
    return JSONResponse(
        status_code=422,
        content={"detail": [{"loc": [], "msg": str(exc), "type": "IntegrityError"}]},
    )


async def init_orm() -> None:
    """initialize tortoise ORM for FastAPI and generate schema initially if no tables are stored in the
    database
    """
    config_util = ConfigUtil()
    logger = LoggingUtil().logger

    tortoise.Tortoise.init_models(config_util.db_models, "models")
    await tortoise.Tortoise.init(
        db_url=config_util.db_url,
        modules={
            "models": config_util.db_models
        }
    )
    logger.info(f"register database at {config_util.db_url}")
    logger.debug("Tortoise-ORM started, %s, %s", tortoise.Tortoise._connections, tortoise.Tortoise.apps)

    logger.info("ORM generating schema")
    await tortoise.Tortoise.generate_schemas(safe=True)


async def close_orm() -> None:
    """close Tortoise ORM
    """
    logger = LoggingUtil().logger
    await tortoise.Tortoise.close_connections()
    logger.info("ORM shutdown")


def create() -> FastAPI:
    """
    create Fast API app
    """
    config_util = ConfigUtil()
    log_util = LoggingUtil()
    log_util.logger.info("create API application...")

    if config_util.debug:
        log_util.logger.warning("Server running in debug mode")

    # create FastAPI
    fast_api = FastAPI(
        title="Wireguard Docker Endpoint",
        description="API to configure wireguard peers via a REST API served by the container",
        version=config_util.app_version,
        debug=config_util.debug
    )
    fast_api.add_middleware(
        CORSMiddleware,
        allow_origins=config_util.cors_origin,
        allow_credentials=True,
        allow_methods=config_util.cors_methods,
        allow_headers=config_util.cors_headers,
    )

    # register custom exception handler
    fast_api.add_exception_handler(RequestValidationError, validation_exception_handler)
    fast_api.add_exception_handler(ValidationError, tortoise_validation_exception_handler)
    fast_api.add_exception_handler(ValueError, tortoise_valueerror_exception_handler)
    fast_api.add_exception_handler(DoesNotExist, tortoise_doesnotexist_exception_handler)
    fast_api.add_exception_handler(IntegrityError, tortoise_integrityerror_exception_handler)

    # register event handler
    fast_api.add_event_handler("startup", init_orm)
    fast_api.add_event_handler("shutdown", close_orm)

    # include routers
    fast_api.include_router(routers.healthcheck_router, prefix="/api/healthcheck", tags=["healthcheck"])
    fast_api.include_router(routers.rules_router, prefix="/api/rules", tags=["rules"])
    fast_api.include_router(routers.wireguard_router, prefix="/api/wg", tags=["rules"])

    log_util.logger.info("finished API application")
    return fast_api
