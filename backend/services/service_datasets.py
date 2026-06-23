from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
from pathlib import Path
import aiofiles

from db import database, engine, STORAGE_FULL_PATH
from models import metadata
from schemas import *
from modelsFromHF import *
from services.service_auth import get_current_user

from middlewares.logger import *
from datasetsFromHF import DatasetsFolder

app = FastAPI(title="MORI datasets_service", 
              description="✨ МОРИ - машинное обучение разворачивание и исследование ✨", 
              version="0.1.0")
metadata.create_all(engine)

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

d = DatasetsFolder()

@app.get("/test")
async def qwerty():
    return await DatasetsFolder().readDataset("Llamacha/ner_quechua_iic", "test2.csv")


@app.post("/dataset")
async def download_dataset_hf(current_user: Annotated[userLogin, Depends(get_current_user)],
                              repo_id: str):
    await d.download_dataset(repo_id)
    return { 
        "message" : "Dataset is downloaded successfully" 
        }


@app.get("/datasets-info")
async def get_info_of_all_datasets(current_user: Annotated[userLogin, Depends(get_current_user)]):

    async def gen():
        async for metadata in d.get_all_datasets():
            yield json.dumps(metadata, ensure_ascii=False) + "\n"

    return StreamingResponse(
        gen(),
        media_type="application/x-ndjson"
    )


@app.get("/dataset")
async def get_info(current_user: Annotated[userLogin, Depends(get_current_user)],
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
    
    tree = d.build_tree(dataset_path)

    return {
        "dataset": f"{dataset[0]}/{dataset[1]}",
        "tree": tree,
    }


@app.get("/dataset-labels")
async def get_dataset_labels_list(current_user: Annotated[userLogin, Depends(get_current_user)],
                                  dataset: str,
                                  filename: str,
                                  ner_key: str):
    return await d.get_labels_list(dataset, filename, ner_key)


@app.get('/get_dataset_info')
async def get_metadata_of_dataset(current_user: Annotated[userLogin, Depends(get_current_user)],
                                repo_id: str):
    return await d.get_dataset_readme_data(repo_id)


@app.get("/datasets")
async def get_all_datasets(current_user: Annotated[userLogin, Depends(get_current_user)]):
    return await d.get_datasets()


@app.get("/file_from_dataset")
async def get_info(current_user: Annotated[userLogin, Depends(get_current_user)],
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


@app.post("/save_file_changes")
async def save_file_changes(current_user: Annotated[userLogin, Depends(get_current_user)],
                            data: SaveRequest,):
    
    await d.save_file_changes(data.dataset, data.filename, data.content)

    return { 
        "status" : "success"
        }

@app.delete('/dataset')
async def dataset(current_user: Annotated[userLogin, Depends(get_current_user)],
                repo_id: str):
    await d.delete_dataset(repo_id)
    return {
        "status": "dataset deleted successfully"
    }