from fastapi import APIRouter
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
from routers.route_auth import get_current_user

from middlewares.logger import *
from UserStorageService import create_file_system_structure
from UserStorageService import UserStorageService
from routers.route_datasets import d

router = APIRouter(tags=["projects"])

# create project
@router.post("/project")
async def project_initialization(project: ProjectCreate, 
                                 current_user: Annotated[OAuth2PasswordRequestForm, Depends(get_current_user)]):
    
    user = UserStorageService(current_user.username)
    await user.create_project(project.project_name, project.description)
    
    return { 
        "message" : "Project is created successfully"
        }


@router.get("/projects")
async def get_user_projects(current_user: Annotated[userLogin, Depends(get_current_user)]):
    user = UserStorageService(current_user.username)
    return await user.get_user_projects()
    

@router.patch("/project")
async def upload_project_file(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              file: UploadFile):
    
    user = UserStorageService(current_user.username)

    await user.upload_file(project_name, file)
    
    return {
        "message": "Project's file was uploaded successfully"
    }

@router.get("/project_data")
async def get_main_project_data(username: str,
                                id_projects: int, 
                                request: Request):
    user = UserStorageService(username)
    result = await user.get_project_data(username, id_projects)

    return result

@router.patch("/project-file")
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


@router.delete("/project")
async def delete_project(project: ProjectDelete, 
                         current_user: Annotated[userLogin, Depends(get_current_user)]):
    
    
    user = UserStorageService(current_user.username)
    await user.delete_project(project.project_name)

    return {
        "message": "Project is deleted successfully"
    }


@router.patch("/project/model")
async def add_model_to_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              model_name: str):
    
    user = UserStorageService(current_user.username)

    await user.addModel(project_name, model_name)
    
    return {
        "message": "Model added to project successfully"
    }


@router.patch("/project/dataset")
async def add_dataset_to_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              dataset_name: str):
    
    user = UserStorageService(current_user.username)

    await user.addDataset(project_name, dataset_name)
    
    return {
        "message": "Dataset added to project successfully"
    }


@router.get("/project/run")
async def run_project(current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              model_name: str,
                              dataset_name: str,
                              filepath: str, 
                              text_key: str):
    
    user = UserStorageService(current_user.username)
    
    return await user.runModel(project_name, model_name, dataset_name, filepath, text_key)