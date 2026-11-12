"""Regresión: no confundir OLLAMA_HOST del servidor con URL del cliente."""
from campusia.config import _ollama_client_url, AppConfig


def test_ignores_server_bind_address(monkeypatch):
    monkeypatch.setenv("OLLAMA_HOST", "0.0.0.0:11434")
    monkeypatch.delenv("CAMPUSIA_OLLAMA_URL", raising=False)
    assert _ollama_client_url() == "http://127.0.0.1:11434"
    assert AppConfig().ollama_host == "http://127.0.0.1:11434"


def test_normalizes_wildcard_in_client_url(monkeypatch):
    monkeypatch.setenv("CAMPUSIA_OLLAMA_URL", "http://0.0.0.0:11434")
    assert _ollama_client_url() == "http://127.0.0.1:11434"


def test_override_custom_client_url(monkeypatch):
    monkeypatch.setenv("CAMPUSIA_OLLAMA_URL", "http://127.0.0.1:9999")
    assert AppConfig().ollama_host == "http://127.0.0.1:9999"
