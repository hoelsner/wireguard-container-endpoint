"""
FastAPI router for wg interface model
"""
from typing import List

import fastapi
from fastapi import HTTPException

import app.wg_config_adapter
import models
import schemas
from routers.response_models import MessageResponseModel, InstanceNotFoundErrorResponseModel, ValidationFailedResponseModel, ActiveResponseModel


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


@wireguard_router.post(
    "/interfaces/{instance_id}/reconfigure",
    response_model=schemas.WgInterfaceSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_wg_interface(instance_id: str):
    """
    force apply interface configuration at system level (will temporary disrupt the wireguard connectivity)
    """
    instance = await models.WgInterfaceModel.get(instance_id=instance_id)
    adapter = app.wg_config_adapter.WgConfigAdapter(wg_interface=instance)

    # (re-)initialize configuration for wireguard configuration
    await adapter.init_config(force_overwrite=True)
    await adapter.rebuild_peer_config()
    await adapter.apply_config(recreate_interface=True)

    return MessageResponseModel(message="configuration applied")


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
    obj = await models.WgInterfaceModel.get_or_none(instance_id=instance_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"WgInterface {instance_id} not found")

    await obj.delete()
    return MessageResponseModel(message=f"Deleted WgInterface {instance_id}")


@wireguard_router.get("/interface/peers", response_model=List[schemas.WgPeerSchema])
async def get_wg_interface_peer_list():
    """
    return a list of all WgPeerModels
    """
    return await schemas.WgPeerSchema.from_queryset(models.WgPeerModel.all())


@wireguard_router.post(
    "/interface/peers",
    response_model=schemas.WgPeerSchema,
    responses={
        422: {"model": ValidationFailedResponseModel}
    }
)
async def create_wg_peer(data: schemas.WgPeerSchemaIn):
    """
    create new WgPeerModel
    """
    obj = await models.WgPeerModel.create(**data.dict(exclude_unset=True))
    return await schemas.WgPeerSchema.from_tortoise_orm(obj)


@wireguard_router.get(
    "/interface/peers/{instance_id}",
    response_model=schemas.WgPeerSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_wg_peer(instance_id: str):
    """
    get WgPeerModel instance
    """
    return await schemas.WgPeerSchema.from_queryset_single(
        models.WgPeerModel.get(instance_id=instance_id)
    )


@wireguard_router.get(
    "/interface/peers/{instance_id}/is_active",
    response_model=ActiveResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_is_peer_active(instance_id: str):
    """
    get state of the given peer
    """
    # required, because the is_active function is async and the pydantic model doesn't allow
    # the use of async computed values
    obj = await models.WgPeerModel.get(instance_id=instance_id)
    return ActiveResponseModel(active=await obj.is_active())


@wireguard_router.put(
    "/interface/peers/{instance_id}",
    response_model=schemas.WgPeerSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        422: {"model": ValidationFailedResponseModel}
    }
)
async def update_wg_peer(instance_id: str, data: schemas.WgPeerSchemaIn):
    """
    update existing WgPeerModel instance
    """
    await models.WgPeerModel.filter(instance_id=instance_id).update(
        **data.dict(exclude_unset=True)
    )
    return await schemas.WgPeerSchema.from_queryset_single(
        models.WgPeerModel.get(instance_id=instance_id)
    )


@wireguard_router.delete(
    "/interface/peers/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def delete_wg_peer(instance_id: str):
    """
    delete WgPeerModel instance
    """

    obj = await models.WgPeerModel.get_or_none(instance_id=instance_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"WgPeer {instance_id} not found")

    await obj.delete()
    return MessageResponseModel(message=f"Deleted WgPeer {instance_id}")
