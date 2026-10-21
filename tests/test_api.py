"""API tests. The agent is replaced with a fake, so these run without Ollama."""
from fastapi.testclient import TestClient

import app.api as api

client = TestClient(api.app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_ask_returns_answer(monkeypatch):
    monkeypatch.setattr(api, "ask", lambda q: {"answer": f"echo: {q}", "route": "docs", "sources": ["notes.md"]})
    r = client.post("/ask", json={"question": "  hello  "})
    assert r.status_code == 200
    assert r.json() == {"answer": "echo: hello", "route": "docs", "sources": ["notes.md"]}


def test_empty_question_rejected():
    assert client.post("/ask", json={"question": ""}).status_code == 422
    assert client.post("/ask", json={"question": "   "}).status_code == 422


def test_agent_failure_returns_503(monkeypatch):
    def boom(q):
        raise ConnectionError("Ollama is not running")
    monkeypatch.setattr(api, "ask", boom)
    r = client.post("/ask", json={"question": "anything"})
    assert r.status_code == 503
    assert "Ollama is not running" in r.json()["detail"]
