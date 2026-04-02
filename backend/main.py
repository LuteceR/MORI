from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi import UploadFile
import aiofiles

import psycopg2

from pydantic_settings import BaseSettings, SettingsConfigDict

class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="settings/.env", env_file_encoding="utf-8", extra="ignore"
    )
    bd_addr: str
    bd_port: str
    bd_name: str
    bd_user: str
    bd_password: str


# Считываем конфиг из .env
config = ConfigBase()

db_params = {
    "host": config.bd_addr,
    "database": config.bd_name,
    "user": config.bd_user,
    "password": config.bd_password,
    "port": config.bd_port
}

# подключаемся к бд
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

app = FastAPI()

# главная страницы сайта http://localhost:8000
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Запрос на получения юзера
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    cur.execute(f"SELECT * FROM users WHERE users.id = {user_id}") #TODO: нет защиты от инъекций
    record = cur.fetchone()
    return record


@app.get("/files/{filename}/download")
async def download_file(filename: str):
    file_path = "userdata/" + filename
    print(file_path)
    return FileResponse(path=file_path, filename=filename, media_type='multipart/form-data')


@app.post("/file/upload-file")
async def upload_file(in_file: UploadFile):
    async with aiofiles.open("userdata/" + in_file.filename, 'wb') as out_file:
        content = await in_file.read()
        await out_file.write(content)
    return {"Result": "OK"}