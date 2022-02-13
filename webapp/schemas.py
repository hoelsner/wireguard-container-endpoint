"""
pydantic schemas to build the bridge between the router and the models
"""
from typing import Type

import tortoise
from tortoise.contrib.pydantic import pydantic_model_creator, PydanticModel

from models.wg_interface import WgInterfaceModel
from models.peer import WgPeerModel
from models.rules import PolicyRuleListModel, Ipv4FilterRuleModel, Ipv6FilterRuleModel, Ipv4NatRuleModel, Ipv6NatRuleModel
from utils.config import ConfigUtil


_config_instance = ConfigUtil()
tortoise.Tortoise.init_models(_config_instance.db_models, "models")

PolicyRuleListSchema: Type[PydanticModel] = pydantic_model_creator(
    PolicyRuleListModel,
    name="PolicyRuleListSchema"
)
PolicyRuleListSchemaIn: Type[PydanticModel] = pydantic_model_creator(
    PolicyRuleListModel,
    name="PolicyRuleListSchemaIn",
    exclude_readonly=True,
    exclude=(
        "ipv4_filter_rules",
        "ipv6_filter_rules",
        "ipv4_nat_rules",
        "ipv6_nat_rules"
    )
)

Ipv4FilterRuleSchema: Type[PydanticModel] = pydantic_model_creator(
    Ipv4FilterRuleModel,
    name="Ipv4FilterRuleSchema"
)
Ipv4FilterRuleSchemaIn: Type[PydanticModel] = pydantic_model_creator(
    Ipv4FilterRuleModel,
    name="Ipv4FilterRuleModelIn",
    exclude_readonly=True
)

Ipv6FilterRuleSchema: Type[PydanticModel] = pydantic_model_creator(
    Ipv6FilterRuleModel,
    name="Ipv6FilterRuleSchema"
)
Ipv6FilterRuleSchemaIn: Type[PydanticModel] = pydantic_model_creator(
    Ipv6FilterRuleModel,
    name="Ipv6FilterRuleSchemaIn",
    exclude_readonly=True
)

Ipv4NatRuleSchema: Type[PydanticModel] = pydantic_model_creator(
    Ipv4NatRuleModel,
    name="Ipv4NatRuleSchema"
)
Ipv4NatRuleSchemaIn: Type[PydanticModel] = pydantic_model_creator(
    Ipv4NatRuleModel,
    name="Ipv4NatRuleSchemaIn",
    exclude_readonly=True
)

Ipv6NatRuleSchema: Type[PydanticModel] = pydantic_model_creator(
    Ipv6NatRuleModel,
    name="Ipv6NatRuleSchema"
)
Ipv6NatRuleSchemaIn: Type[PydanticModel] = pydantic_model_creator(
    Ipv6NatRuleModel,
    name="Ipv6NatRuleSchemaIn",
    exclude_readonly=True
)

WgInterfaceSchema: Type[PydanticModel] = pydantic_model_creator(
    WgInterfaceModel,
    name="WgInterfaceSchema"
)
WgInterfaceSchemaIn: Type[PydanticModel] = pydantic_model_creator(
    WgInterfaceModel,
    name="WgInterfaceSchemaIn",
    exclude_readonly=True
)

WgPeerSchema: Type[PydanticModel] = pydantic_model_creator(
    WgPeerModel,
    name="WgPeerSchema"
)
WgPeerSchemaIn: Type[PydanticModel] = pydantic_model_creator(
    WgPeerModel,
    name="WgPeerSchemaIn",
    exclude_readonly=True
)
