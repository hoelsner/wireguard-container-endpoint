"""
FastAPI router for rules model
"""
from typing import List
import fastapi
from fastapi import HTTPException
import schemas
import models
from routers.response_models import MessageResponseModel, InstanceNotFoundErrorResponseModel,ValidationFailedResponseModel


rules_router = fastapi.APIRouter()


@rules_router.get("/filters/ipv4", response_model=List[schemas.Ipv4FilterRuleSchema])
async def get_filters_ipv4():
    """
    return a list of IPv4FilterRules
    """
    return await schemas.Ipv4FilterRuleSchema.from_queryset(models.Ipv4FilterRuleModel.all())


@rules_router.post(
    "/filters/ipv4",
    response_model=schemas.Ipv4FilterRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel}
    }
)
async def create_filters_ipv4(ipv4_filter_rule: schemas.Ipv4FilterRuleSchema):
    """
    create new IPv4FilterRule
    """
    obj = await models.Ipv4FilterRuleModel.create(**ipv4_filter_rule.dict(exclude_unset=True))
    return await schemas.Ipv4FilterRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/filters/ipv4/{instance_id}",
    response_model=schemas.Ipv4FilterRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_filter_ipv4_instance(instance_id: str):
    """
    get IPv4FilterRule instance
    """
    return await schemas.Ipv4FilterRuleSchema.from_queryset_single(
        models.Ipv4FilterRuleModel.get(instance_id=instance_id)
    )


@rules_router.put(
    "/filters/ipv4/{instance_id}",
    response_model=schemas.Ipv4FilterRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        422: {"model": ValidationFailedResponseModel}
    }
)
async def update_filter_ipv4_instance(instance_id: str, ipv4_filter_rule: schemas.Ipv4FilterRuleSchema):
    """
    update existing IPv4FilterRule instance
    """
    await models.Ipv4FilterRuleModel.filter(instance_id=instance_id).update(
        **ipv4_filter_rule.dict(exclude_unset=True)
    )
    return await schemas.Ipv4FilterRuleSchema.from_queryset_single(
        models.Ipv4FilterRuleModel.get(instance_id=instance_id)
    )


@rules_router.delete(
    "/filters/ipv4/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def delete_filter_ipv4_instance(instance_id: str):
    """
    delete IPv4FilterRule instance
    """
    deleted_count = await models.Ipv4FilterRuleModel.filter(instance_id=instance_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Ipv4FilterRule {instance_id} not found")

    return MessageResponseModel(message=f"Deleted Ipv4FilterRule {instance_id}")


@rules_router.get("/filters/ipv6", response_model=List[schemas.Ipv6FilterRuleSchema])
async def get_filters_ipv6():
    """
    return a list of IPv6FilterRuleModels
    """
    return await schemas.Ipv6FilterRuleSchema.from_queryset(models.Ipv6FilterRuleModel.all())


@rules_router.post(
    "/filters/ipv6",
    response_model=schemas.Ipv6FilterRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel}
    }
)
async def create_filters_ipv6(ipv6_filter_rule: schemas.Ipv6FilterRuleSchema):
    """
    create new Ipv6FilterRuleModel
    """
    obj = await models.Ipv6FilterRuleModel.create(**ipv6_filter_rule.dict(exclude_unset=True))
    return await schemas.Ipv6FilterRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/filters/ipv6/{instance_id}",
    response_model=schemas.Ipv6FilterRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_filter_ipv6_instance(instance_id: str):
    """
    get Ipv6FilterRuleModel instance
    """
    return await schemas.Ipv6FilterRuleSchema.from_queryset_single(
        models.Ipv6FilterRuleModel.get(instance_id=instance_id)
    )


@rules_router.put(
    "/filters/ipv6/{instance_id}",
    response_model=schemas.Ipv6FilterRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        422: {"model": ValidationFailedResponseModel}
    }
)
async def update_filter_ipv6_instance(instance_id: str, ipv6_filter_rule: schemas.Ipv6FilterRuleSchema):
    """
    update existing Ipv6FilterRuleModel instance
    """
    await models.Ipv6FilterRuleModel.filter(instance_id=instance_id).update(
        **ipv6_filter_rule.dict(exclude_unset=True)
    )
    return await schemas.Ipv6FilterRuleSchema.from_queryset_single(
        models.Ipv6FilterRuleModel.get(instance_id=instance_id)
    )


@rules_router.delete(
    "/filters/ipv6/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def delete_filter_ipv6_instance(instance_id: str):
    """
    delete IPv6FilterRule instance
    """
    deleted_count = await models.Ipv6FilterRuleModel.filter(instance_id=instance_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Ipv6FilterRule {instance_id} not found")

    return MessageResponseModel(message=f"Deleted Ipv6FilterRule {instance_id}")


@rules_router.get("/nat/ipv4", response_model=List[schemas.Ipv4NatRuleSchema])
async def get_nat_ipv4_rules():
    """
    return a list of Ipv4NatRuleModel
    """
    return await schemas.Ipv4NatRuleSchema.from_queryset(models.Ipv4NatRuleModel.all())


@rules_router.post(
    "/nat/ipv4",
    response_model=schemas.Ipv4NatRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel}
    }
)
async def create_nat_ipv4_rule(data: schemas.Ipv4NatRuleSchema):
    """
    create new Ipv4NatRuleModel
    """
    obj = await models.Ipv4NatRuleModel.create(**data.dict(exclude_unset=True))
    return await schemas.Ipv4NatRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/nar/ipv4/{instance_id}",
    response_model=schemas.Ipv4NatRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_nat_ipv4_rule(instance_id: str):
    """
    get Ipv4NatRuleModel instance
    """
    return await schemas.Ipv4NatRuleSchema.from_queryset_single(
        models.Ipv4NatRuleModel.get(instance_id=instance_id)
    )


@rules_router.put(
    "/nat/ipv4/{instance_id}",
    response_model=schemas.Ipv4NatRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        422: {"model": ValidationFailedResponseModel}
    }
)
async def update_nat_ipv4_rule(instance_id: str, data: schemas.Ipv4NatRuleSchema):
    """
    update existing Ipv4NatRuleModel instance
    """
    await models.Ipv4NatRuleModel.filter(instance_id=instance_id).update(
        **data.dict(exclude_unset=True)
    )
    return await schemas.Ipv4NatRuleSchema.from_queryset_single(
        models.Ipv4NatRuleModel.get(instance_id=instance_id)
    )


@rules_router.delete(
    "/nat/ipv4/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def delete_nat_ipv4_rule(instance_id: str):
    """
    delete Ipv4NatRuleModel instance
    """
    deleted_count = await models.Ipv4NatRuleModel.filter(instance_id=instance_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Ipv4NatRule {instance_id} not found")

    return MessageResponseModel(message=f"Deleted Ipv4NatRule {instance_id}")


@rules_router.get("/nat/ipv6", response_model=List[schemas.Ipv6NatRuleSchema])
async def get_nat_ipv6_rules():
    """
    return a list of Ipv6NatRuleModel
    """
    return await schemas.Ipv6NatRuleSchema.from_queryset(models.Ipv6NatRuleModel.all())


@rules_router.post(
    "/nat/ipv6",
    response_model=schemas.Ipv6NatRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel}
    }
)
async def create_nat_ipv6_rule(data: schemas.Ipv6NatRuleSchema):
    """
    create new Ipv6NatRuleModel
    """
    obj = await models.Ipv6NatRuleModel.create(**data.dict(exclude_unset=True))
    return await schemas.Ipv6NatRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/nar/ipv6/{instance_id}",
    response_model=schemas.Ipv6NatRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def get_nat_ipv6_rule(instance_id: str):
    """
    get Ipv6NatRuleModel instance
    """
    return await schemas.Ipv6NatRuleSchema.from_queryset_single(
        models.Ipv6NatRuleModel.get(instance_id=instance_id)
    )


@rules_router.put(
    "/nat/ipv6/{instance_id}",
    response_model=schemas.Ipv6NatRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        422: {"model": ValidationFailedResponseModel}
    }
)
async def update_nat_ipv6_rule(instance_id: str, data: schemas.Ipv6NatRuleSchema):
    """
    update existing Ipv6NatRuleModel instance
    """
    await models.Ipv6NatRuleModel.filter(instance_id=instance_id).update(
        **data.dict(exclude_unset=True)
    )
    return await schemas.Ipv6NatRuleSchema.from_queryset_single(
        models.Ipv6NatRuleModel.get(instance_id=instance_id)
    )


@rules_router.delete(
    "/nat/ipv6/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel}
    }
)
async def delete_nat_ipv6_rule(instance_id: str):
    """
    delete Ipv6NatRuleModel instance
    """
    deleted_count = await models.Ipv6NatRuleModel.filter(instance_id=instance_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Ipv6NatRule {instance_id} not found")

    return MessageResponseModel(message=f"Deleted Ipv6NatRule {instance_id}")
