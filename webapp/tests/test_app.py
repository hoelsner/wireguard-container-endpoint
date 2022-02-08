import pytest
from fastapi.testclient import TestClient


class TestFastApiDocs:
    async def test_docs(self, test_client: TestClient):
        response = await test_client.get("/docs")
        assert response.status_code == 200
