from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db import SECRET_KEY

ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt