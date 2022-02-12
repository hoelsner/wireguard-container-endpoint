import pytest
from fastapi.testclient import TestClient
import wgconfig.wgexec


def broken_function(*args, **kwargs) -> str:
    raise Exception("An Exception")


class TestHealtcheckEndpoint:
    """
    Test Healthcheck API endpoint
    """
    async def test_success(self, test_client: TestClient):
        """test basic healthcheck
        """
        response = await test_client.get("/api/healthcheck/")
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

    async def test_wireguard_failure(self, test_client: TestClient, monkeypatch):
        """test healthcheck with failed wireguard key generation
        """
        with monkeypatch.context() as m:
            m.setattr(wgconfig.wgexec, "generate_presharedkey", broken_function)
            response = await test_client.get("/api/healthcheck/")
            assert response.status_code == 500
            assert response.json()["detail"] == "healthcheck for wireguard failed"
