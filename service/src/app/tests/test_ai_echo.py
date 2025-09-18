from fastapi.testclient import TestClient

from app.main import app


def test_ai_echo():
    client = TestClient(app)
    resp = client.get("/ai/echo", params={"text": "hello"})
    assert resp.status_code == 200
    assert resp.json()["result"].startswith("echo: hello")
