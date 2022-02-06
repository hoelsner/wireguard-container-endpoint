import pytest
from fastapi.testclient import TestClient


class TestFastApiDocs:
    def test_docs(self, test_client: TestClient):
        response = test_client.get("/docs")
        assert response.status_code == 200
