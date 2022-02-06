import pytest
from fastapi.testclient import TestClient


class TestHealtcheckEndpoint:
    """
    Test Healthcheck API endpoint
    """
    def test_success(self, test_client: TestClient):
        response = test_client.get("/api/healthcheck/")
        assert response.status_code == 200
        assert response.json() == {"message": "ok"}
