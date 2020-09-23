import pytest


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv("PROXY_USERNAME", "cat")
    monkeypatch.setenv("PROXY_PASSWORD", "tac")
    monkeypatch.setenv("ES_HOST", "eshost")
    monkeypatch.setenv("ES_PORT", "9981")
    monkeypatch.setenv("ES_USE_SSL", "true")
