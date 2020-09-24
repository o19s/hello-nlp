import pytest


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv("PROXY_USERNAME", "username")
    monkeypatch.setenv("PROXY_PASSWORD", "password")
    monkeypatch.setenv("NLP_HOST", "localhost")
    monkeypatch.setenv("NLP_PORT", "9200")
    monkeypatch.setenv("NLP_USE_SSL", "false")
