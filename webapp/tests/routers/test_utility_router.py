import pytest
from fastapi.testclient import TestClient
import wgconfig.wgexec

import utils.config


def wgexec_mock():
    """mock function to generate keys"""
    return "yGdF7UWA/ieg1yBjIc0ahLdDQZHhK4oUAlcAytIk4Xw="


async def test_gen_privkey(test_client: TestClient, monkeypatch):
    """test generate privkey
    """
    with monkeypatch.context() as m:
        m.setattr(wgconfig.wgexec, "generate_privatekey", wgexec_mock)

        response = await test_client.post("/api/utils/wg/generate/privkey")
        assert response.status_code == 200

        json_data = response.json()
        assert json_data == {
            "private_key": "yGdF7UWA/ieg1yBjIc0ahLdDQZHhK4oUAlcAytIk4Xw="
        }


async def test_gen_psk(test_client: TestClient, monkeypatch):
    """test generate preshared key
    """
    with monkeypatch.context() as m:
        m.setattr(wgconfig.wgexec, "generate_presharedkey", wgexec_mock)

        response = await test_client.post("/api/utils/wg/generate/presharedkey")
        assert response.status_code == 200

        json_data = response.json()
        assert json_data == {
            "preshared_key": "yGdF7UWA/ieg1yBjIc0ahLdDQZHhK4oUAlcAytIk4Xw="
        }


async def test_get_instance_info(test_client: TestClient, monkeypatch):
    """test get instance info endpoint
    """
    cu = utils.config.ConfigUtil()

    response = await test_client.get("/api/utils/instance/info")
    assert response.status_code == 200

    json_data = response.json()
    assert json_data == {
        "version": cu.app_version,
        "name": "Wireguard Docker Endpoint",
        "debug": cu.debug
    }

    # test with different app version
    old_value = cu.app_version
    with monkeypatch.context() as m:
        m.setenv("APP_VERSION", "MockedVersion")
        cu.refresh_config()
        response = await test_client.get("/api/utils/instance/info")
        assert response.status_code == 200

        json_data = response.json()
        assert json_data == {
            "version": "MockedVersion",
            "name": "Wireguard Docker Endpoint",
            "debug": cu.debug
        }
        m.setenv("APP_VERSION", old_value)
