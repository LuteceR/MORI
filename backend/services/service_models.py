from fastapi import FastAPI, HTTPException, status, Depends, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from fastapi.responses import StreamingResponse

from db import database, engine, STORAGE_FULL_PATH
from models import metadata
from schemas import *
from modelsFromHF import *
from services.service_auth import get_current_user

from middlewares.logger import *

app = FastAPI(title="MORI models_service", 
              description="✨ МОРИ - машинное обучение разворачивание и исследование ✨", 
              version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/model")
async def download_model_hf(current_user: Annotated[userLogin, Depends(get_current_user)],
                            model_repo: str):
    m = ModelsFolder(model_repo)
    await m.create_model()
    return { 
        "message" : "Model is downloaded successfully" 
        }

@app.get("/get_models_metadata")
async def get_metadata_of_all_models(current_user: Annotated[userLogin, Depends(get_current_user)]):
    m = ModelsFolder('')

    async def gen():
        async for metadata in m.get_models_readme_data():
            yield json.dumps(metadata, ensure_ascii=False) + "\n"

    return StreamingResponse(
        gen(),
        media_type="application/x-ndjson"
    )
@app.get("/model")
async def get_model_information(current_user: Annotated[userLogin, Depends(get_current_user)],
                                model_repo: str):
    mf = ModelsFolder(model_repo)
    return await mf.get_model_info()


@app.get("/models")
async def get_models(current_user: Annotated[userLogin, Depends(get_current_user)]):
    mf = ModelsFolder("")
    return await mf.get_models()

# теперь запуск только через проект
# @app.post("/model/run")
# async def run_model_on_dataset(current_user: Annotated[userLogin, Depends(get_current_user)],
#                                model_repo: str, 
#                                dataset_repo: str, 
#                                filepath: str, 
#                                text_key: str):
#     mf = ModelsFolder(model_repo)
#     return await mf.run_model(dataset_repo, filepath, text_key)


@app.delete("/model")
async def delete_model(current_user: Annotated[userLogin, Depends(get_current_user)],
                        model_repo: str):
    m = ModelsFolder(model_repo)
    await m.delete_model()
    return { 
        "message" : "Model is deleted successfully" 
        }