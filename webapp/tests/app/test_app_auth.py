from base64 import b64encode

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("disable_os_level_commands")
async def test_missing_authentication_credentials(unauth_test_client: TestClient):
    """test what happens if authentication credentials are missing
    """
    # endpoint requires authentication
    response = await unauth_test_client.post("/api/utils/wg/generate/privkey")
    assert response.status_code == 401


@pytest.mark.usefixtures("disable_os_level_commands")
async def test_invalid_authentication(unauth_test_client: TestClient):
    """test what happens if authentication credentials are missing
    """
    auth_string = b64encode(f"admin:MyInvalidPassword".encode("utf-8")).decode("utf-8")

    # endpoint requires authentication
    response = await unauth_test_client.post("/api/utils/wg/generate/privkey", headers={"Authorization": f"Basic {auth_string}"})
    assert response.status_code == 401


@pytest.mark.usefixtures("disable_os_level_commands")
async def test_valid_authentication(unauth_test_client: TestClient, basic_auth_header):
    """test what happens if authentication credentials are missing
    """
    # endpoint requires authentication
    response = await unauth_test_client.post("/api/utils/wg/generate/privkey", headers=basic_auth_header)
    assert response.status_code == 200
