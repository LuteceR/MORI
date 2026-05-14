from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.utils import get_authorization_scheme_param
from typing import Annotated
from pathlib import Path
from huggingface_hub.utils import disable_progress_bars
import aiofiles

from db import database, engine, STORAGE_FULL_PATH
from models import metadata
from schemas import *
from modelsFromHF import *
from routers.route_auth import get_current_user

from middlewares.logger import *
from UserStorageService import create_file_system_structure
from UserStorageService import UserStorageService
from datasetsFromHF import DatasetsFolder

router = APIRouter(tags=["datasets"])

d = DatasetsFolder()

@router.post("/dataset")
async def download_dataset_hf(request: Request,
                              current_user: Annotated[userLogin, Depends(get_current_user)],
                              dataset_repo: str):
    
    await DatasetsFolder().download_dataset(dataset_repo)
    
    return { 
        "message" : "Dataset is downloaded successfully" 
        }

@router.get("/dataset")
async def get_info(request: Request,
                    current_user: Annotated[userLogin, Depends(get_current_user)],
                    dataset: str):
    
    if not "/" in dataset:
        raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, 
                    detail = "Incorrect dataset repo id"
                )

    dataset = dataset.replace("\\", "/").split("/")
    
    if (len(dataset) != 2):
        raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND, 
                    detail = "Dataset does not exists"
                )

    dataset_path = d.local_dir_ / dataset[0] / dataset[1]

    if not dataset_path.is_dir():
        raise HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND, 
                    detail = "Dataset does not exists"
                )
    
    tree = d.build_tree(Path(dataset[0]) / dataset[1])

    return {
        "dataset": f"{dataset[0]}/{dataset[1]}",
        "tree": tree,
    }


@router.get("/file_from_dataset")
async def get_info(request: Request,
                   current_user: Annotated[userLogin, Depends(get_current_user)],
                    dataset: str,
                    filepath: str):

    dataset = dataset.replace("\\", "/")

    async def gen():
        path = d.local_dir_ / dataset / Path(filepath)
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as file:
                buffer = ""

                async for line in file:
                    buffer += line

                    if len(buffer) > 256:
                        # print(buffer + f"\n\n---------------{len(buffer)}---------------\n")
                        yield buffer
                        buffer = ""
                        # await asyncio.sleep(0.2)
                
                if buffer:
                    # print(buffer + f"\n\n---------------{len(buffer)}---------------\n")
                    yield buffer
                    # await asyncio.sleep(0.5)

        except Exception as e:
            print("ERROR IN STREAM: ", e)
            raise
    return StreamingResponse(gen(), 
                             media_type="application/x-ndjson")

@router.post("/save_file_changes")
async def save_file_changes(current_user: Annotated[userLogin, Depends(get_current_user)],
                            data: SaveRequest,):
    
    await d.save_file_changes(data.dataset, data.filename, data.content)

    return { 
        "status" : "success"
        }