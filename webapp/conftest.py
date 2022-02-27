"""
pytest fixtures
"""
import os
import shutil
from base64 import b64encode
from typing import Generator

import pytest
from httpx import AsyncClient

import models
import app.fast_api
import utils.os_func
import utils.config


@pytest.fixture(scope="function", autouse=True)
def disable_os_level_commands(monkeypatch):
    """fixture to disable the os_level sub-commands commands
    """
    def disabled_run_subprocess(command: str, **kwargs):
        if command == "wg-json":
            return "{}", "mocked stderr", True

        return "mocked stdout", "mocked stderr", True

    def disable_configure_route(**kwargs):
        pass

    with monkeypatch.context() as m:
        m.setattr(utils.os_func, "run_subprocess", disabled_run_subprocess)
        m.setattr(utils.os_func, "configure_route", disable_configure_route)
        yield


@pytest.fixture(scope="session", autouse=True)
def create_test_dirs():
    """ensure that test dirs exist
    """
    # create data directory
    data_dir = os.environ.get("DATA_DIR", None)
    wg_data_dir = os.environ.get("WG_CONFIG_DIR", None)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)

    if wg_data_dir:
        os.makedirs(wg_data_dir, exist_ok=True)

    yield

    # cleanup data directory
    if wg_data_dir:
        shutil.rmtree(wg_data_dir)


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def base_test_client() -> Generator:
    """create a test client for FastAPI
    """
    # yield test client
    fastapi_app = app.fast_api.create()
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        # startup and shutdown events not triggered with AsyncClient - initialize it manually
        await app.fast_api.startup_app()
        yield client
        await app.fast_api.shutdown_app()


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def unauth_test_client(base_test_client) -> Generator:
    """extend the test client for FastAPI with authentication
    """
    # inject authentication data for testing
    base_test_client.headers = {}
    yield base_test_client


@pytest.fixture(scope="function")
@pytest.mark.asyncio
async def test_client(base_test_client, basic_auth_header) -> Generator:
    """extend the test client for FastAPI with authentication
    """
    # inject authentication data for testing
    base_test_client.headers = basic_auth_header
    yield base_test_client


@pytest.fixture(scope="function")
def basic_auth_header():
    """get http base authentication
    """
    config = utils.config.ConfigUtil()
    auth_string = b64encode(f"{config.admin_user}:{config.admin_password}".encode("utf-8")).decode("utf-8")
    return {"Authorization": f"Basic {auth_string}"}


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
    await models.WgPeerModel.all().delete()
