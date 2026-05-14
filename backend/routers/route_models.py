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

router = APIRouter(tags=["models"])

@router.post("/model")
async def download_model_hf(current_user: Annotated[userLogin, Depends(get_current_user)],
                            model_repo: str):
    m = ModelsFolder(model_repo)
    await m.create_model()
    return { 
        "message" : "Model is downloaded successfully" 
        }


@router.get("/model")
async def get_model_information(current_user: Annotated[userLogin, Depends(get_current_user)],
                                model_repo: str):
    mf = ModelsFolder(model_repo)
    return await mf.get_model_info()


@router.get("/models")
async def get_models_information(current_user: Annotated[userLogin, Depends(get_current_user)]):
    mf = ModelsFolder("")
    return await mf.get_models()


@router.post("/model/run")
async def run_model_on_dataset(current_user: Annotated[userLogin, Depends(get_current_user)],
                               model_repo: str, 
                               dataset_repo: str, 
                               filepath: str, 
                               text_key: str):
    mf = ModelsFolder(model_repo)
    return await mf.run_model(dataset_repo, filepath, text_key)


@router.delete("/model")
async def delete_model(current_user: Annotated[userLogin, Depends(get_current_user)],
                        model_repo: str):
    m = ModelsFolder(model_repo)
    await m.delete_model()
    return { 
        "message" : "Model is deleted successfully" 
        }