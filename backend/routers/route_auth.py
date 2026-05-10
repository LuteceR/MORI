from fastapi import APIRouter
from fastapi import HTTPException, status, Response, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from typing import Annotated, Optional
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext
from datetime import timedelta

from db import database
from models import users
from schemas import *
from modelsFromHF import *
from middlewares.logger import *
from UserStorageService import UserStorageService
from app import RUN_MODE

ACCESS_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_MINUTES = 120

class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if scheme.lower() == "bearer":
            return param

        if cookie_authorization:
            scheme, param = get_authorization_scheme_param(cookie_authorization)
            if scheme.lower() == "bearer":
                if RUN_MODE == "development":
                    print("authorization with cookie: ", param)
                return param

        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
    
router = APIRouter()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="token")
DUMMY_HASH = pwd_context.hash("dummypassword")

# Получает user у бд из jwt-токена, исп-ся только для авторизац. в запросах
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = None
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if user is None:
        raise credentials_exception
    return user

# Получает user у бд по паролю
async def authenticate_user(username: str, password: str):
    query = users.select().where(users.c.username == username)
    db_user = await database.fetch_one(query)

    if not db_user:
        pwd_context.verify(password, DUMMY_HASH)
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Incorrect username or password"
            )
    
    if not pwd_context.verify(password, db_user["password"]):
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Incorrect username or password",
            )
    return db_user

@router.post("/registration")
async def registration(user: userLogin, response: Response):
    query = users.select().where(users.c.username == user.username)
    existing_user = await database.fetch_one(query)
    
    if existing_user:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                            detail = "User already exists")
    
    if user.rememberMe:
        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    hashed_password = pwd_context.hash(user.password)
    query = users.insert().values(username=user.username, password=hashed_password)
    await database.execute(query)

    user_folder = UserStorageService(user.username)
    user_folder.create_user_folder()

    access_token = create_access_token({ "sub": user.username })

    return {"message": "User registered successfully"}


# видимо только для dev-инструментов (/docs)
@router.post("/token")
async def login_for_access_token(
    current_user: Annotated[OAuth2PasswordRequestForm, Depends(get_current_user)],
) -> Token:
    
    user = await authenticate_user(current_user.username, current_user.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token({"sub": user.username}, access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/authorization")
async def authorization(user: userLogin, response: Response) -> Token:
    await authenticate_user(user.username, user.password)

    if user.rememberMe:
        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token({ "sub": user.username }, access_token_expires)
    
    response = JSONResponse({"message": "User is authorised successfully"})
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",
        domain="",
        max_age=int(access_token_expires.total_seconds()),
    )
    return response
  


@router.get('/cookie')
async def root(request: Request):
    return request.cookies