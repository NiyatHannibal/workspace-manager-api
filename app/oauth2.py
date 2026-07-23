import jwt
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from . import schemas
from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "0123sdfnnnnnnnnnnnnnnnnnasrrfjfnhhbvf"
ALGORITHM = "HS256"
EXPIRATION_TIME = 30


def create_access_token(payload: dict):
    to_encode = payload.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=EXPIRATION_TIME)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        u_id: int = payload.get("user_id")

        if u_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=u_id)
        return token_data
    except InvalidTokenError:
        raise credentials_exception


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"www-Authenticate": "Bearer"})
    return verify_access_token(token, credentials_exception)
