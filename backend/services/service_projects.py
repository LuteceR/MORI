from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from db import database, engine, STORAGE_FULL_PATH
from models import metadata
from schemas import *
from modelsFromHF import *
from services.service_auth import get_current_user

from middlewares.logger import *
from UserStorageService import UserStorageService
from services.routers.router_metrics import router as router_metrics

app = FastAPI(title="MORI projects_service", 
              description="✨ МОРИ - машинное обучение разворачивание и исследование ✨", 
              version="0.1.0")
metadata.create_all(engine)

app.include_router(router_metrics)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/project")
async def get_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                      project_id: int):
    user = UserStorageService(current_user.username)
    return await user.get_user_project(project_id)


@app.get("/projects")
async def get_user_projects(current_user: Annotated[userLogin, Depends(get_current_user)]):
    user = UserStorageService(current_user.username)
    return await user.get_projects_of_user()


# create project
@app.post("/project")
async def project_initialization(project: ProjectCreate, 
                                 current_user: Annotated[OAuth2PasswordRequestForm, Depends(get_current_user)]):
    
    user = UserStorageService(current_user.username)
    await user.create_project(project.project_name, project.description)
    
    return { 
        "message" : "Project is created successfully"
        }
    

@app.patch("/project")
async def upload_project_file(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              file: UploadFile):
    
    user = UserStorageService(current_user.username)

    await user.upload_file(project_name, file)
    
    return {
        "message": "Project's file was uploaded successfully"
    }

# not used
@app.get("/project_data")
async def get_main_data(username: str,
                        id_projects: int):
    user = UserStorageService(username)
    result = await user.get_project_data(username, id_projects)

    return result

@app.patch("/project-file")
async def edit_project_file(current_user: Annotated[userLogin, Depends(get_current_user)],
                            project_name: str,
                            filename: str,
                            newFile: UploadFile):
    
    
    user = UserStorageService(current_user.username)
    await user.edit_file(project_name = project_name,
                   file_to_overwrite = filename,
                   file = newFile)
    
    return {
        "message": "file changed successfully"
    }


@app.delete("/project")
async def delete_project(project: ProjectDelete, 
                         current_user: Annotated[userLogin, Depends(get_current_user)]):
    
    
    user = UserStorageService(current_user.username)
    await user.delete_project(project.project_name)

    return {
        "message": "Project is deleted successfully"
    }

# not used
@app.get("/project/models")
async def get_project_models(current_user: Annotated[userLogin, Depends(get_current_user)],
                             project_name: str):
    
    user = UserStorageService(current_user.username)
    return await user.get_models(project_name)


@app.patch("/project/model")
async def add_model_to_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              model_name: str):
    
    user = UserStorageService(current_user.username)

    await user.addModel(project_name, model_name)
    
    return {
        "message": "Model added to project successfully"
    }


@app.delete("/project/model")
async def remove_model_from_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              model_name: str):
    
    user = UserStorageService(current_user.username)
    await user.removeModel(project_name, model_name)
    
    return {
        "message": "Model removed successfully"
    }


@app.patch("/project/dataset")
async def add_dataset_to_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              dataset_name: str):
    
    user = UserStorageService(current_user.username)

    await user.addDataset(project_name, dataset_name)
    
    return {
        "message": "Dataset added to project successfully"
    }


@app.delete("/project/dataset")
async def remove_dataset_from_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              dataset_name: str):
    user = UserStorageService(current_user.username)
    await user.removeDataset(project_name, dataset_name)
    
    return {
        "message": "Dataset removed successfully"
    }


@app.get("/project/run")
async def run_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              model_name: str,
                              dataset_name: str,
                              filepath: str, 
                              text_key: str | None = None,
                              ner_key: str | None = None,
                              threshold: float | None = None):
    
    user = UserStorageService(current_user.username)
    
    return await user.runModel(project_name, model_name, dataset_name, filepath, text_key, ner_key, threshold=threshold)

