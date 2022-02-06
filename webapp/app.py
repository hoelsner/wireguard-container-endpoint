"""
Start the Wireguard Container Endpoint (WGCE)
"""
from sys import prefix
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI, status, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise.exceptions import ValidationError

import routers
import utils


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """return HTTP 422 for data validation errors"""
    utils.LoggingUtil().logger.debug("RequestValidationError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


async def tortoise_validation_exception_handler(request: Request, exc: ValidationError):
    """validation error for tortoise"""
    utils.LoggingUtil().logger.debug("RequestValidationError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": [{"msg": str(exc), "body": "ValidationError"}]})
    )


async def tortoise_valueerror_exception_handler(request: Request, exc: ValueError):
    """exception handler to handle enum validation errors from tortoise correct"""
    utils.LoggingUtil().logger.debug("RequestValidationError: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": [{"msg": str(exc), "body": "ValidationError"}]})
    )


def create() -> FastAPI:
    """
    create Fast API app
    """
    config_util = utils.ConfigUtil()
    log_util = utils.LoggingUtil()
    log_util.logger.info("create API application...")

    # create FastAPI
    fast_api = FastAPI(
        title="Wireguard Docker Endpoint",
        description="API to configure wireguard peers via a REST API served by the container",
        version=config_util.app_version
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

    # register ORM
    register_tortoise(
        fast_api,
        db_url=config_util.db_url,
        modules={"models": config_util.db_models},
        generate_schemas=True,
        add_exception_handlers=True
    )

    # include routers
    fast_api.include_router(routers.healthcheck_router, prefix="/api/healthcheck", tags=["healthcheck"])
    fast_api.include_router(routers.rules_router, prefix="/api/rules", tags=["rules"])

    log_util.logger.info("finished API application")
    return fast_api
