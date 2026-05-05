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
from datasetsFromHF import DatasetsFolder

router = APIRouter()

# create project
@router.post("/project")
async def project_initialization(request: Request, 
                                 current_user: Annotated[OAuth2PasswordRequestForm, Depends(get_current_user)],
                                 project_name: str, 
                                 description: str):
    
    user = UserStorageService(current_user.username)
    await user.create_project(project_name, description)
    
    return { 
        "message" : "Project is created successfully"
        }


# not finished
@router.get("/project")
async def get_abstract_info(owner: str,
                            project_name: str):
    return {
        "repo_id": f"{owner}/{project_name}",
        
    }
    

@router.patch("/project")
async def upload_project_file(request: Request,
                              current_user: Annotated[userLogin, Depends(get_current_user)],
                              project_name: str,
                              file: UploadFile):
    
    username = request.cookies.get('username')

    user = UserStorageService(username)

    await user.upload_file(project_name, file)
    
    return {
        "message": "Project's file was uploaded successfully"
    }


@router.patch("/project-file")
async def edit_project_file(request: Request,
                            current_user: Annotated[userLogin, Depends(get_current_user)],
                            project_name: str,
                            filename: str,
                            newFile: UploadFile):
    
    username = request.cookies.get('username')
    
    user = UserStorageService(username)
    await user.edit_file(project_name = project_name,
                   file_to_overwrite = filename,
                   file = newFile)
    
    return {
        "message": "file changed successfully"
    }


@router.delete("/project")
async def delete_project(request: Request, 
                         current_user: Annotated[userLogin, Depends(get_current_user)],
                         username: str,
                         project_name: str):
    
    
    user = UserStorageService(username)
    await user.delete_project(project_name)

    return {
        "message": "Project is deleted successfully"
    }