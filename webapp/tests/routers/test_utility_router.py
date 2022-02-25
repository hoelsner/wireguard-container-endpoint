import json

import pytest
from fastapi.testclient import TestClient
import wgconfig.wgexec

import utils.config
import utils.os_func


def mock_wg_json_command(command: str, **kwargs):
    data = {
        "wgvpn16": {
                "privateKey": "4PSSsNFfYpqzJ3thGCeHd8pZWkZVdoJbm2G7oiA6TmQ=",
                "publicKey": "yx0owjK+RWUD3ccSDBus7PA/B+WuVhSYUmEO9XAil0k=",
                "listenPort": 51820,
                "peers": {
                        "s5WDa5TV/DeXYLQZfXG4RD1/eGPt2rkDMGB1Z379ZQs=": {
                                "presharedKey": "V4x0/xBvGj4/vAo7UIA5kYOMwvppI45lVgmAiiIhRaQ=",
                                "endpoint": "172.29.0.1:62818",
                                "latestHandshake": 200000000,
                                "transferRx": 82224,
                                "transferTx": 1680,
                                "allowedIps": [
                                        "172.29.1.16/32",
                                        "fd00:1::16/128"
                                ]
                        }
                }
        }
    }
    return json.dumps(data, indent=4), "", True


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


async def test_get_wg_operational_data(test_client: TestClient, monkeypatch):
    """test get WG operational data
    """
    with monkeypatch.context() as m:
        m.setattr(utils.os_func, "run_subprocess", mock_wg_json_command)

        response = await test_client.get("/api/utils/wg/operational")
        assert response.status_code == 200

        json_data = response.json()
        assert "privateKey" not in json_data["wgvpn16"].keys(), "private key is not exposed"
