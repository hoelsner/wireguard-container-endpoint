"""
pydantic schemas to build the bridge between the router and the models
"""
from tortoise.contrib.pydantic import pydantic_model_creator
import models


Ipv4FilterRuleSchema = pydantic_model_creator(models.Ipv4FilterRuleModel, name="Ipv4FilterRuleSchema")
