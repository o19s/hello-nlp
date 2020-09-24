import pytest
from fastapi import HTTPException
from fastapi.security.http import HTTPBasicCredentials


def test_basic_auth(environment):
    # Import is inside because PROXY_USERNAME and PROXY_PASSWORD
    # environment variables are checked on the import time.
    # These variables are set by the `environment` fixture.
    from hello_nlp.auth import basic_auth

    result = basic_auth(HTTPBasicCredentials(username="cat", password="tac"))
    assert result == "cat"


def test_basic_auth_fails_on_invalid_credentials(environment):
    from hello_nlp.auth import basic_auth

    with pytest.raises(HTTPException):
        result = basic_auth(HTTPBasicCredentials(username="dog", password="tac"))
        assert result.status_code == 401
