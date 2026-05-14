from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.utils import get_authorization_scheme_param
from typing import Annotated
from pathlib import Path
from huggingface_hub.utils import disable_progress_bars

from db import database, engine, STORAGE_FULL_PATH
from models import metadata
from schemas import *
from modelsFromHF import *
from routers import route_auth, route_projects, route_models, route_datasets
from routers.route_auth import get_current_user

from middlewares.logger import *
from UserStorageService import create_file_system_structure
from UserStorageService import UserStorageService
from datasetsFromHF import DatasetsFolder
import os
tags = [
    {"name": "auth", "description": ""},
    {"name": "models", "description": ""},
    {"name": "datasets", "description": ""},
    {"name": "projects", "description": ""}
]

app = FastAPI(title="MORI", 
              description="✨ МОРИ - машинное обучение разворачивание и исследование ✨", 
              version="0.1.0",
              openapi_tags=tags)
metadata.create_all(engine)
app.include_router(route_auth.router)
app.include_router(route_projects.router)
app.include_router(route_models.router)
app.include_router(route_datasets.router)

create_file_system_structure(STORAGE_FULL_PATH)

RUN_MODE = os.getenv("APP_ENV", "production") # or "development"

# настройка CORS политики
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    disable_progress_bars() # выкл вывод загрузки у huggingface_hub
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return { "status": "ok" }

