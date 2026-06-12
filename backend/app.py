from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub.utils import disable_progress_bars

from db import database, engine, STORAGE_FULL_PATH
from models import metadata
from schemas import *
from modelsFromHF import *
from routers import route_auth, route_projects, route_models, route_datasets

from middlewares.logger import *
from UserStorageService import create_file_system_structure

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

metadata.create_all(engine)
app.include_router(route_auth.router)
app.include_router(route_projects.router)
app.include_router(route_models.router)
app.include_router(route_datasets.router)

create_file_system_structure(STORAGE_FULL_PATH)
disable_progress_bars() # выкл вывод загрузки у huggingface_hub


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return { "status": "ok" }

