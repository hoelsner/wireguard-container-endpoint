import pytest
from fastapi.testclient import TestClient
import utils.config


async def test_gen_privkey(test_client: TestClient):
    """test generate privkey
    """
    response = await test_client.post("/api/utils/wg/generate/privkey")
    assert response.status_code == 200

    json_data = response.json()
    assert "private_key" in json_data.keys()
    assert isinstance(json_data["private_key"], str)


async def test_gen_psk(test_client: TestClient):
    """test generate preshared key
    """
    response = await test_client.post("/api/utils/wg/generate/presharedkey")
    assert response.status_code == 200

    json_data = response.json()
    assert "preshared_key" in json_data.keys()
    assert isinstance(json_data["preshared_key"], str)

async def test_get_instance_info(test_client: TestClient, monkeypatch):
    """test get instance info endpoint
    """
    cu = utils.config.ConfigUtil()

    response = await test_client.get("/api/utils/instance/info")
    assert response.status_code == 200

    json_data = response.json()
    assert json_data == {
        "version": cu.app_version,
        "debug": False
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
            "debug": False
        }
        m.setenv("APP_VERSION", old_value)
