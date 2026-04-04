from fastapi import FastAPI, HTTPException, status, Response
from fastapi.responses import FileResponse
import aiofiles
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

import psycopg2

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

from db import database, engine
from models import users, metadata
from schemas import UserCreate, userLogin
from middlewares.logger import create_access_token
ACCESS_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_MINUTES = 120

app = FastAPI()

class Token(BaseModel):
    access_token: str
    token_type: str

metadata.create_all(engine)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Запрос на получения юзера
# @app.get("/users/{user_id}")
# async def read_user(user_id: str):
#     cur.execute(f"SELECT * FROM users WHERE users.id = {user_id}") #TODO: нет защиты от инъекций
#     record = cur.fetchone()
#     return record


# @app.get("/files/{filename}/download")
# async def download_file(filename: str):
#     file_path = "userdata/" + filename
#     print(file_path)
#     return FileResponse(path=file_path, filename=filename, media_type='multipart/form-data')


# @app.post("/file/upload-file")
# async def upload_file(in_file: UploadFile):
#     async with aiofiles.open("userdata/" + in_file.filename, 'wb') as out_file:
#         content = await in_file.read()
#         await out_file.write(content)
#     return {"Result": "OK"}

@app.post("/registration")
async def registration(user: UserCreate):
    query = users.select().where(users.c.username == user.username)
    existing_user = await database.fetch_one(query)
    if existing_user:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                            detail = "User already exists")
    hashed_password = pwd_context.hash(user.password)
    query = users.insert().values(username=user.username, password = hashed_password)
    await database.execute(query)
    return {"message": "User registered successfully"}

@app.post("/authorization")
async def authorization(user: userLogin, response: Response):
    query = users.select().where(users.c.username == user.username)
    existing_user = await database.fetch_one(query)

    if not existing_user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Incorrect username or password"
            )
    if not pwd_context.verify(user.password, existing_user["password"]):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                headers={"WWW-Authenticate": "Bearer"},
                detail="Incorrect username or password",
            )
    
    if user.rememberMe:
        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(data = { "sub": user.username }, 
                                       expires_delta = access_token_expires)

    response.set_cookie(
        key="auth",
        value=access_token,
        httponly=True,
        max_age=int(access_token_expires.total_seconds()),
    )

    return { "message" : "Login successful" }