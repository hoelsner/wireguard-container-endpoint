import pytest
from fastapi.testclient import TestClient


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
