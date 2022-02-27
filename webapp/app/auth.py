import secrets

from fastapi import status, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import utils.config


security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    """HTTP Basic authentication for FastAPI
    """
    config = utils.config.ConfigUtil()

    correct_username = secrets.compare_digest(credentials.username, config.admin_user)
    correct_password = secrets.compare_digest(credentials.password, config.admin_password)

    # verify given credentials
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid authentication credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username
