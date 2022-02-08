import pytest
from fastapi.testclient import TestClient


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
