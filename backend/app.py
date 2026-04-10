from fastapi import FastAPI, HTTPException, status, Response
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

import psycopg2

from pydantic import BaseModel

from db import database, engine, STORAGE_FULL_PATH
from models import users, metadata
from schemas import UserCreate, userLogin
from modelsFromHF import ModelsFolder, sync_models

from middlewares.logger import create_access_token
from UserFolder import create_file_system_structure
from UserFolder import UserFolder

ACCESS_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_MINUTES = 120

app = FastAPI()

class Token(BaseModel):
    access_token: str
    token_type: str

metadata.create_all(engine)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
create_file_system_structure(STORAGE_FULL_PATH)

async def check_user_pass(username: str, password: str):
    query = users.select().where(users.c.username == username)
    existing_user = await database.fetch_one(query)

    if not existing_user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Wrong login or password"
            )
    
    if not pwd_context.verify(password, existing_user["password"]):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                headers={"WWW-Authenticate": "Bearer"},
                detail="Incorrect username or password",
            )


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/registration")
async def registration(user: UserCreate):
    query = users.select().where(users.c.username == user.username)
    existing_user = await database.fetch_one(query)
    
    if existing_user:
        raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                            detail = "User already exists")
    
    hashed_password = pwd_context.hash(user.password)
    query = users.insert().values(username=user.username, password=hashed_password)
    await database.execute(query)

    user_folder = UserFolder(user.username)
    user_folder.create_user_folder()

    return {"message": "User registered successfully"}

@app.post("/authorization")
async def authorization(user: userLogin, response: Response):
    await check_user_pass(user.username, user.password)
    
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

@app.post("/project")
async def project_initialization(username: str, 
                                 password: str,
                                 project_name: str, 
                                 description: str):
    await check_user_pass(username, password)

    user = UserFolder(username)
    await user.create_project_folder(project_name, description)
    
    return { 
        "message" : "Project is created successfully"
        }

@app.delete("/project")
async def delete_project(username: str, 
                         password: str,
                         project_name: str):
    
    await check_user_pass(username, password)
    
    user = UserFolder(username)
    await user.delete_project_folder(project_name)

    return {
        "message": "Project is deleted successfully"
    }

@app.post("/model")
async def download_model_hf(username: str, 
                            password: str,
                            repo_id: str):
    await check_user_pass(username, password)
    m = ModelsFolder(repo_id)
    await m.create_model()
    return { 
        "message" : "Model is downloaded successfully" 
        }

@app.delete("/model")
async def delete_model(username: str, 
                       password: str,
                       model_name: str):
    await check_user_pass(username, password)
    m = ModelsFolder(model_name)
    await m.delete_model()
    return { 
        "message" : "Model is deleted successfully" 
        }


@app.post("/model-sync")
async def sync_m(username: str, password: str):
    await check_user_pass(username, password)
    await sync_models()
    return { 
        "message" : "Ended. result in console" 
        }
    