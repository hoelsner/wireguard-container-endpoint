"""
FastAPI router for wg interface model
"""
from typing import List
import fastapi
from fastapi import HTTPException
import schemas
import models
from routers.response_models import MessageResponseModel, InstanceNotFoundErrorResponseModel,ValidationFailedResponseModel


wireguard_router = fastapi.APIRouter()


@wireguard_router.get("/interfaces", response_model=List[schemas.WgInterfaceSchema])
async def get_wg_interface_list():
    """
    return a list of WgInterface
    """
    return await schemas.WgInterfaceSchema.from_queryset(models.WgInterfaceModel.all())


@wireguard_router.post(
    "/interfaces",
    response_model=schemas.WgInterfaceSchema,
    responses={
        422: {"model": ValidationFailedResponseModel}
    }
)
async def create_wg_interface(data: schemas.WgInterfaceSchemaIn):
    """
    create new WgInterface
    """
    obj = await models.WgInterfaceModel.create(**data.dict(exclude_unset=True))
    return await schemas.WgInterfaceSchema.from_tortoise_orm(obj)


@wireguard_router.get(
    "/interfaces/{instance_id}",
    response_model=schemas.WgInterfaceSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_wg_interface(instance_id: str):
    """
    get WgInterface instance
    """
    return await schemas.WgInterfaceSchema.from_queryset_single(
        models.WgInterfaceModel.get(instance_id=instance_id)
    )


@wireguard_router.put(
    "/interfaces/{instance_id}",
    response_model=schemas.WgInterfaceSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        422: {"model": ValidationFailedResponseModel}
    }
)
async def update_wg_interface(instance_id: str, data: schemas.WgInterfaceSchemaIn):
    """
    update existing WgInterface instance
    """
    await models.WgInterfaceModel.filter(instance_id=instance_id).update(
        **data.dict(exclude_unset=True)
    )
    return await schemas.WgInterfaceSchema.from_queryset_single(
        models.WgInterfaceModel.get(instance_id=instance_id)
    )


@wireguard_router.delete(
    "/interfaces/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def delete_wg_interface(instance_id: str):
    """
    delete WgInterface instance
    """
    deleted_count = await models.WgInterfaceModel.filter(instance_id=instance_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"WgInterface {instance_id} not found")

    return MessageResponseModel(message=f"Deleted WgInterface {instance_id}")
