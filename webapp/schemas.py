"""
pydantic schemas to build the bridge between the router and the models
"""
from tortoise.contrib.pydantic import pydantic_model_creator
import models


Ipv4FilterRuleSchema = pydantic_model_creator(models.Ipv4FilterRuleModel, name="Ipv4FilterRuleSchema")
Ipv6FilterRuleSchema = pydantic_model_creator(models.Ipv6FilterRuleModel, name="Ipv6FilterRuleSchema")
Ipv4NatRuleSchema = pydantic_model_creator(models.Ipv4NatRuleModel, name="Ipv4NatRuleSchema")
Ipv6NatRuleSchema = pydantic_model_creator(models.Ipv6NatRuleModel, name="Ipv6NatRuleSchema")
