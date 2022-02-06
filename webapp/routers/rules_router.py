"""
FastAPI router for rules model
"""
from typing import List
import fastapi
from fastapi import HTTPException
import schemas
import models
from routers.response_models import MessageResponseModel, InstanceNotFoundErrorResponseModel


rules_router = fastapi.APIRouter()


@rules_router.get("/filters/ipv4", response_model=List[schemas.Ipv4FilterRuleSchema])
async def get_filters_ipv4():
    """
    return a list of IPv4FilterRules
    """
    return await schemas.Ipv4FilterRuleSchema.from_queryset(models.Ipv4FilterRuleModel.all())


@rules_router.post("/filters/ipv4", response_model=schemas.Ipv4FilterRuleSchema)
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
        404: {"model": InstanceNotFoundErrorResponseModel}
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
