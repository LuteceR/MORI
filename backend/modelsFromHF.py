# модуль для установки моделей с HuggingFace
from huggingface_hub import snapshot_download

from huggingface_hub.errors import RepositoryNotFoundError, LocalEntryNotFoundError
from fastapi import FastAPI, HTTPException, status, Response
from db import database, STORAGE_FULL_PATH
from models import models
import asyncio
import shutil
import os

class ModelsFolder:
    local_dir_ = ""
    def __init__(self, model_name: str):
        ModelsFolder.local_dir_ = STORAGE_FULL_PATH + "/MODELS/"
        self.model_name = model_name
        self.full_path = ModelsFolder.local_dir_ + model_name
        
    
    async def create_model(self, orig_model_id: int = None):
        """
        Загружает модель с huggingface и создает запись в бд
        ModelsFolder.model_name должен содержать путь до репозитория
        """
        query = models.select().where(models.c.name == self.model_name)
        existing_model = await database.fetch_one(query)

        if existing_model:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                    detail = f"Model {self.model_name} already exist!")
        print("model:", self.model_name)
        
        try:
            # т.к. snapshot_download не асинхронный
            await asyncio.to_thread(snapshot_download, self.model_name, local_dir=f"{self.full_path}")
        except(RepositoryNotFoundError):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Repository {self.model_name} does not exist!")
        except(LocalEntryNotFoundError):
            raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, 
                        detail = "Can't connect to repository!")
    

        query = models.insert().values(name=self.model_name, folder_path=self.full_path,
                                        id_original_model=orig_model_id)
        await database.execute(query)


    async def delete_model(self):
        query = models.select().where(models.c.name == self.model_name)
        existing_model = await database.fetch_one(query)
        if existing_model is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Model {self.model_name} does not exist!")
        
        if os.path.exists(self.full_path):
            try:
                shutil.rmtree(self.full_path)
            except(OSError):
                raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                        detail = f"Model {self.model_name} is currently in use!")
        query = models.delete().where(models.c.id_models == existing_model.id_models)
        await database.execute(query)



async def sync_models():
    """
    1) добавлять в бд модели из папки (нужна валидация),
    2) загружать в папки модели из бд если есть ссылка на источник
    3) Иначе удалять
    """
    
    # Сканирование хранилища и добавление в БД
    print("Сканирование хранилища и добавление в БД")
    for entry in os.scandir(STORAGE_FULL_PATH + "/MODELS/"):
        if not entry.is_dir():
            continue
        print("----", entry.name, "----")
        subfolders = [subentry for subentry in os.scandir(entry.path) if entry.is_dir()]

        # работает для моделей от huggingface
        # entry - папка автора модели, subfolders - 1 папка самой модели
        if len(subfolders) != 1:
            print("Имеет некорректную файловую структуру, пропускаю")
            continue
        
        model_name = entry.name + subfolders[0].name
        query = models.select().where(models.c.name == model_name)
        existing_model = await database.fetch_one(query)
        if existing_model:
            print("Уже синхронизировано")
            continue

        query = models.insert().values(name=model_name, folder_path=subfolders[0].path)
        await database.execute(query)

    # Сканирование БД и загрузка из huggingface
    print("Сканирование БД и загрузка из huggingface")
    query = models.select()
    DB_models = await database.fetch_all(query)
    if DB_models is None:
        print("В БД не моделей!")
        return
        
    for model in DB_models:
        print("----", model.name, "----")
        if os.path.exists(model.folder_path):
            print("Уже синхронизировано")
            continue

        try:
            # т.к. snapshot_download не асинхронный
            await asyncio.to_thread(snapshot_download, model.name, local_dir=f"{model.full_path}")
        except Exception as e:
            print("Произошла ошибка при загрузке модели с huggingface:", e)

