"""
fixtures for E2E testing
"""
import logging
import time

from requests.auth import HTTPBasicAuth
import pytest

import utils


@pytest.fixture(scope="session")
def hub_basic_auth():
    """hub basic auth
    """
    return HTTPBasicAuth("wg_hub", "wg_hub")

@pytest.fixture(scope="session")
def client_basic_auth():
    """client basic auth
    """
    return HTTPBasicAuth("wg_spoke", "wg_spoke")

@pytest.fixture(scope="session")
def temp_hub_basic_auth():
    """Temp Hub basic auth
    """
    return HTTPBasicAuth("wg_temp_hub", "wg_temp_hub")

@pytest.fixture(scope="module")
def use_scenario_1():
    """setup and teardown of scenario one
    """
    logging.info("create environment for scenario 1")
    utils.create_scenario_1()
    time.sleep(60)
    yield
    logging.info("destroy environment for scenario 1")
    utils.destroy_scenario_1()

@pytest.fixture(scope="class")
def use_scenario_2():
    """setup and teardown of scenario two deployments (single client connection, two hubs)
    """
    logging.info("create environment for scenario 2")
    utils.create_scenario_2()
    time.sleep(60)
    yield
    logging.info("destroy environment for scenario 2")
    utils.destroy_scenario_2()
