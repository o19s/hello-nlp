import pytest


@pytest.fixture
def environment(monkeypatch):
    monkeypatch.setenv("PROXY_USERNAME", "cat")
    monkeypatch.setenv("PROXY_PASSWORD", "tac")
    monkeypatch.setenv("NLP_HOST", "localhost")
    monkeypatch.setenv("NLP_PORT", "9200")
    monkeypatch.setenv("NLP_USE_SSL", "false")
