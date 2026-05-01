import aiofiles
from fastapi import FastAPI, HTTPException, status, Response
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile, Request
from collections.abc import AsyncIterable

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from pathlib import Path

from pydantic import BaseModel

from db import database, engine, STORAGE_FULL_PATH
from models import users, metadata
from schemas import SaveRequest, UserCreate, userLogin, file
from modelsFromHF import *

from middlewares.logger import create_access_token
from UserStorageService import create_file_system_structure
from UserStorageService import UserStorageService
from datasetsFromHF import DatasetsFolder

ACCESS_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_MINUTES = 120

app = FastAPI()

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


async def auth_check(username: str, auth_token: str):
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Wrong username!"
            )
    if create_access_token({"sub": user.username }) != auth_token:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                headers={"WWW-Authenticate": "Bearer"},
                detail="Incorrect auth cookie",
            )

d = DatasetsFolder()
d.set_local_dir(STORAGE_FULL_PATH)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def root():
    return { "status" : "ok"}

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

    user_folder = UserStorageService(user.username)
    user_folder.create_user_folder()

    return {"message": "User registered successfully"}

@app.post("/authorization")
async def authorization(user: userLogin, response: Response):
    await check_user_pass(user.username, user.password)
    
    if user.rememberMe:
        access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    else:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token({ "sub": user.username })

    response.set_cookie(
        key="auth",
        value=access_token,
        secure=True,
        max_age=int(access_token_expires.total_seconds())
    )

    response.set_cookie(
        key="username",
        value=user.username,
        secure=True,
        max_age=int(access_token_expires.total_seconds()),
    )

    return { "message" : "Login successful" }
    


@app.get('/cookie')
async def root(request: Request):
    return request.cookies.get('auth')

# create project
@app.post("/project")
async def project_initialization(request: Request, 
                                 username: str, 
                                 project_name: str, 
                                 description: str):
    await auth_check(username, request.cookies.get('auth'))

    user = UserStorageService(username)
    await user.create_project(project_name, description)
    
    return { 
        "message" : "Project is created successfully"
        }


# not finished
@app.get("/project")
async def get_abstract_info(owner: str,
                            project_name: str):
    return {
        "repo_id": f"{owner}/{project_name}",
        
    }
    

@app.patch("/project")
async def upload_project_file(request: Request, 
                              username: str,
                              project_name: str,
                              file: UploadFile):
    
    await auth_check(username, request.cookies.get('auth'))

    user = UserStorageService(username)

    await user.upload_file(project_name, file)
    
    return {
        "message": "Project's file was uploaded successfully"
    }


@app.patch("/project-file")
async def edit_project_file(request: Request, 
                            username: str, 
                            project_name: str,
                            filename: str,
                            newFile: UploadFile):
    
    await auth_check(username, request.cookies.get('auth'))
    
    user = UserStorageService(username)
    await user.edit_file(project_name = project_name,
                   file_to_overwrite = filename,
                   file = newFile)
    
    return {
        "message": "file changed successfully"
    }


@app.delete("/project")
async def delete_project(request: Request, 
                         username: str,
                         project_name: str):
    
    await auth_check(username, request.cookies.get('auth'))
    
    user = UserStorageService(username)
    await user.delete_project(project_name)

    return {
        "message": "Project is deleted successfully"
    }

@app.post("/model")
async def download_model_hf(request: Request, 
                            username: str,
                            repo_id: str):
    await auth_check(username, request.cookies.get('auth'))
    m = ModelsFolder(repo_id)
    await m.create_model()
    return { 
        "message" : "Model is downloaded successfully" 
        }


@app.get("/model")
async def get_model_information(request: Request, 
                                username: str,
                                model_name: str):
    await auth_check(username, request.cookies.get('auth'))
    mf = ModelsFolder(model_name)
    return await mf.get_model_info()


@app.get("/models")
async def get_model_information(request: Request, 
                                username: str):
    await auth_check(username, request.cookies.get('auth'))
    mf = ModelsFolder("")
    return await mf.get_models()


@app.delete("/model")
async def delete_model(request: Request, 
                        username: str,
                        model_name: str):
    await auth_check(username, request.cookies.get('auth'))
    m = ModelsFolder(model_name)
    await m.delete_model()
    return { 
        "message" : "Model is deleted successfully" 
        }



# datasetmaster/resumes
@app.get("/dataset")
async def get_info(dataset: str):
    # await auth_check(username, request.cookies.get('auth'))
    
    if not "/" in dataset:
        return HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, 
                    detail = "Incorrect dataset repo id"
                )

    dataset = dataset.replace("\\", "/").split("/")
    
    if (len(dataset) != 2):
        return HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND, 
                    detail = "Dataset does not exists"
                )

    # d.download_dataset("fka/prompts.chat")

    dataset_path = d.local_dir_ / dataset[0] / dataset[1]

    if not dataset_path.is_dir():
        return HTTPException(
                    status_code = status.HTTP_404_NOT_FOUND, 
                    detail = "Dataset does not exists"
                )
    
    tree = d.build_tree(Path(dataset[0]) / dataset[1])

    return {
        "dataset": f"{dataset[0]}/{dataset[1]}",
        "tree": tree,
    }


@app.get("/file_from_dataset")
async def get_info(dataset: str,
                   filepath: str):

    # await auth_check(username, request.cookies.get('auth'))
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
async def save_file_changes(data: SaveRequest):
    
    await d.save_file_changes(data.dataset, data.filename, data.content)

    return { 
        "status" : "success"
        }