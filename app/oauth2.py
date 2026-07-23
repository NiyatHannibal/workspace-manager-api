import jwt
from datetime import datetime, timezone, timedelta
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "0123sdfnnnnnnnnnnnnnnnnnasrrfjfnhhbvf"
ALGORITHM = "HS256"
EXPIRATION_TIME = 30


def create_access_token(payload: dict):
    to_encode = payload.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=EXPIRATION_TIME)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
