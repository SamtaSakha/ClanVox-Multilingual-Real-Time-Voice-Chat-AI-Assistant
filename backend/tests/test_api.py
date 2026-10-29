import pytest
import httpx
from backend.app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_languages_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/v1/languages")
        assert res.status_code == 200
        data = res.json()
        assert "languages" in data
        assert "hi" in data["languages"]
        assert "en" in data["languages"]

@pytest.mark.asyncio
async def test_create_session():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/v1/sessions", json={"mode": "voice", "initial_language": "hi"})
        assert res.status_code == 200
        data = res.json()
        assert "session_id" in data
        assert data["language"] == "hi"

@pytest.mark.asyncio
async def test_chat_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/v1/chat", json={
            "session_id": "test_sess_1",
            "message": "Namaste! Aap kaise hain?",
            "language": "hi"
        })
        assert res.status_code == 200
        data = res.json()
        assert "reply" in data
        assert data["language"] == "hi"
