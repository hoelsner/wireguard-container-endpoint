"""
pytest fixtures
"""
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

import models
from app import create as create_app


@pytest.fixture(scope="module")
def test_client() -> Generator:
    """
    create a test client for FastAPI
    """
    # yield test client
    with TestClient(create_app()) as client:
        yield client

    print(os.environ.get("DB_FILENAME"))

    try:
        os.remove("test.sqlite3")
    except:
        pass

@pytest.fixture
async def clean_db():
    """clean database after running test
    """
    yield
    await models.Ipv4FilterRuleModel.all().delete()
    await models.Ipv6FilterRuleModel.all().delete()
    await models.Ipv4NatRuleModel.all().delete()
    await models.Ipv6NatRuleModel.all().delete()

