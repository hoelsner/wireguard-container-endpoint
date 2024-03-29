"""
FastAPI router for rules model
"""
from typing import List

import fastapi
from fastapi import HTTPException

import app.auth
import models
import schemas
from routers.response_models import MessageResponseModel, InstanceNotFoundErrorResponseModel,ValidationFailedResponseModel, DetailMessageResponseModel


rules_router = fastapi.APIRouter()


@rules_router.get(
    "/filters/ipv4",
    response_model=List[schemas.Ipv4FilterRuleSchema],
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_filters_ipv4(username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    return a list of IPv4FilterRules
    """
    return await schemas.Ipv4FilterRuleSchema.from_queryset(models.Ipv4FilterRuleModel.all())


@rules_router.post(
    "/filters/ipv4",
    response_model=schemas.Ipv4FilterRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def create_filters_ipv4(data: schemas.Ipv4FilterRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    create new IPv4FilterRule
    """
    obj = await models.Ipv4FilterRuleModel.create(**data.dict(exclude_unset=True))
    return await schemas.Ipv4FilterRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/filters/ipv4/{instance_id}",
    response_model=schemas.Ipv4FilterRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_filter_ipv4_instance(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
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
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def update_filter_ipv4_instance(instance_id: str, data: schemas.Ipv4FilterRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    update existing IPv4FilterRule instance
    """
    await models.Ipv4FilterRuleModel.filter(instance_id=instance_id).update(
        **data.dict(exclude_unset=True)
    )
    return await schemas.Ipv4FilterRuleSchema.from_queryset_single(
        models.Ipv4FilterRuleModel.get(instance_id=instance_id)
    )


@rules_router.delete(
    "/filters/ipv4/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def delete_filter_ipv4_instance(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    delete IPv4FilterRule instance
    """
    obj = await models.Ipv4FilterRuleModel.get_or_none(instance_id=instance_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Ipv4FilterRule {instance_id} not found")

    await obj.delete()
    return MessageResponseModel(message=f"Deleted Ipv4FilterRule {instance_id}")


@rules_router.get(
    "/filters/ipv6",
    response_model=List[schemas.Ipv6FilterRuleSchema],
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_filters_ipv6(username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    return a list of IPv6FilterRuleModels
    """
    return await schemas.Ipv6FilterRuleSchema.from_queryset(models.Ipv6FilterRuleModel.all())


@rules_router.post(
    "/filters/ipv6",
    response_model=schemas.Ipv6FilterRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def create_filters_ipv6(data: schemas.Ipv6FilterRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    create new Ipv6FilterRuleModel
    """
    obj = await models.Ipv6FilterRuleModel.create(**data.dict(exclude_unset=True))
    return await schemas.Ipv6FilterRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/filters/ipv6/{instance_id}",
    response_model=schemas.Ipv6FilterRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_filter_ipv6_instance(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
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
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def update_filter_ipv6_instance(instance_id: str, data: schemas.Ipv6FilterRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    update existing Ipv6FilterRuleModel instance
    """
    await models.Ipv6FilterRuleModel.filter(instance_id=instance_id).update(
        **data.dict(exclude_unset=True)
    )
    return await schemas.Ipv6FilterRuleSchema.from_queryset_single(
        models.Ipv6FilterRuleModel.get(instance_id=instance_id)
    )


@rules_router.delete(
    "/filters/ipv6/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def delete_filter_ipv6_instance(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    delete IPv6FilterRule instance
    """
    obj = await models.Ipv6FilterRuleModel.get_or_none(instance_id=instance_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Ipv6FilterRule {instance_id} not found")

    await obj.delete()
    return MessageResponseModel(message=f"Deleted Ipv6FilterRule {instance_id}")


@rules_router.get(
    "/nat/ipv4",
    response_model=List[schemas.Ipv4NatRuleSchema],
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_nat_ipv4_rules(username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    return a list of Ipv4NatRuleModel
    """
    return await schemas.Ipv4NatRuleSchema.from_queryset(models.Ipv4NatRuleModel.all())


@rules_router.post(
    "/nat/ipv4",
    response_model=schemas.Ipv4NatRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def create_nat_ipv4_rule(data: schemas.Ipv4NatRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    create new Ipv4NatRuleModel
    """
    obj = await models.Ipv4NatRuleModel.create(**data.dict(exclude_unset=True))
    return await schemas.Ipv4NatRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/nat/ipv4/{instance_id}",
    response_model=schemas.Ipv4NatRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_nat_ipv4_rule(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
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
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def update_nat_ipv4_rule(instance_id: str, data: schemas.Ipv4NatRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
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
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def delete_nat_ipv4_rule(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    delete Ipv4NatRuleModel instance
    """
    obj = await models.Ipv4NatRuleModel.get_or_none(instance_id=instance_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Ipv4NatRule {instance_id} not found")

    await obj.delete()
    return MessageResponseModel(message=f"Deleted Ipv4NatRule {instance_id}")


@rules_router.get(
    "/nat/ipv6",
    response_model=List[schemas.Ipv6NatRuleSchema],
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_nat_ipv6_rules(username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    return a list of Ipv6NatRuleModel
    """
    return await schemas.Ipv6NatRuleSchema.from_queryset(models.Ipv6NatRuleModel.all())


@rules_router.post(
    "/nat/ipv6",
    response_model=schemas.Ipv6NatRuleSchema,
    responses={
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def create_nat_ipv6_rule(data: schemas.Ipv6NatRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    create new Ipv6NatRuleModel
    """
    obj = await models.Ipv6NatRuleModel.create(**data.dict(exclude_unset=True))
    return await schemas.Ipv6NatRuleSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/nat/ipv6/{instance_id}",
    response_model=schemas.Ipv6NatRuleSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_nat_ipv6_rule(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
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
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def update_nat_ipv6_rule(instance_id: str, data: schemas.Ipv6NatRuleSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
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
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def delete_nat_ipv6_rule(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    delete Ipv6NatRuleModel instance
    """
    obj = await models.Ipv6NatRuleModel.get_or_none(instance_id=instance_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Ipv6NatRule {instance_id} not found")

    await obj.delete()
    return MessageResponseModel(message=f"Deleted Ipv6NatRule {instance_id}")


@rules_router.get(
    "/policy_rule_list",
    response_model=List[schemas.PolicyRuleListSchema],
    responses={
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_policy_rule_list_entries(username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    return a list of PolicyRuleLists
    """
    return await schemas.PolicyRuleListSchema.from_queryset(models.PolicyRuleListModel.all())


@rules_router.post(
    "/policy_rule_list",
    response_model=schemas.PolicyRuleListSchema,
    responses={
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def create_policy_rule_list(data: schemas.PolicyRuleListSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    create new PolicyRuleList
    """
    obj = await models.PolicyRuleListModel.create(**data.dict(exclude_unset=True))
    return await schemas.PolicyRuleListSchema.from_tortoise_orm(obj)


@rules_router.get(
    "/policy_rule_list/{instance_id}",
    response_model=schemas.PolicyRuleListSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def get_policy_rule_list(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    get PolicyRuleList instance
    """
    return await schemas.PolicyRuleListSchema.from_queryset_single(
        models.PolicyRuleListModel.get(instance_id=instance_id)
    )


@rules_router.put(
    "/policy_rule_list/{instance_id}",
    response_model=schemas.PolicyRuleListSchema,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        422: {"model": ValidationFailedResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def update_policy_rule_list(instance_id: str, data: schemas.PolicyRuleListSchemaIn, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    update existing PolicyRuleList instance
    """
    await models.PolicyRuleListModel.filter(instance_id=instance_id).update(
        **data.dict(exclude_unset=True)
    )
    return await schemas.PolicyRuleListSchema.from_queryset_single(
        models.PolicyRuleListModel.get(instance_id=instance_id)
    )


@rules_router.delete(
    "/policy_rule_list/{instance_id}",
    response_model=MessageResponseModel,
    responses={
        404: {"model": InstanceNotFoundErrorResponseModel},
        401: {
            "description": "missing or invalid authentication provided on endpoint",
            "model": DetailMessageResponseModel
        }
    }
)
async def delete_policy_rule_list(instance_id: str, username: str = fastapi.Depends(app.auth.get_current_username)):
    """
    delete PolicyRuleList instance
    """
    obj = await models.PolicyRuleListModel.get_or_none(instance_id=instance_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"PolicyRuleList {instance_id} not found")

    await obj.delete()
    return MessageResponseModel(message=f"Deleted PolicyRuleList {instance_id}")
