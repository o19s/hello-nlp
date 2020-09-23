import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .exceptions import MissingEnvironmentVariable

security = HTTPBasic()

try:
    USER = os.environ["PROXY_USERNAME"]
    PSWD = os.environ["PROXY_PASSWORD"]
except KeyError as err:
    raise MissingEnvironmentVariable(f"{err} must be define in the environment.")


def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USER)
    correct_password = secrets.compare_digest(credentials.password, PSWD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
