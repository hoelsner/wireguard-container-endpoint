"""
pytest fixtures
"""
from typing import Generator

import pytest
from httpx import AsyncClient

import models
import app


@pytest.fixture(autouse=True)
@pytest.mark.asyncio
async def test_client() -> Generator:
    """
    create a test client for FastAPI
    """
    # yield test client
    fastapi_app = app.create()
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        # startup and shutdown events not triggered with AsyncClient - initialize it manually
        await app.init_orm()
        yield client
        await app.close_orm()


@pytest.fixture(scope="function")
async def clean_db():
    """remove all entries after running tests
    """
    yield
    await models.Ipv4FilterRuleModel.all().delete()
    await models.Ipv6FilterRuleModel.all().delete()
    await models.Ipv4NatRuleModel.all().delete()
    await models.Ipv6NatRuleModel.all().delete()
    await models.PolicyRuleListModel.all().delete()
    await models.WgInterfaceModel.all().delete()
