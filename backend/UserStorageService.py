import asyncio
from pathlib import Path
import shutil

import os

from fastapi import FastAPI, HTTPException, status, Response
from fastapi import HTTPException
from fastapi import File, UploadFile

from sqlalchemy import insert, select, delete, and_
import aiofiles

from models import users, models, datasets, projects, projects_models, projects_datasets
from db import database, STORAGE_FULL_PATH
from modelsFromHF import ModelsFolder
from metrics import storeResults

def create_file_system_structure(storage_full_path:str):
    """
    создаёт структуру файловой системы по указанному пути
    """
    base = Path(storage_full_path)
    for f in ["MODELS", "DATASETS", "USERS"]:
            (base / f).mkdir(parents=True, exist_ok=True)

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))

class UserStorageService:
    storage_full_path = f"{STORAGE_FULL_PATH}"

    def __init__(self, username: str):
        self.__username = username


    async def get_user_project(self, project_id: int):
        """ Возвращает инфу о проекте, плюс список моделей и датасетов"""
        base_query = select(
            users.c.username,
            projects.c.id_projects,
            projects.c.name,
            projects.c.description
        ).select_from(
            users.join(projects, projects.c.id_users == users.c.id_users)
        ).where(
            (users.c.username == self.__username) & (projects.c.id_projects == project_id)
        )
        result = await database.fetch_one(base_query)
        if not result:
            return None
        
        models_result = await self.get_models(result["name"])
        datasets_result = await self.get_datasets(result["name"])
        
        return {
            "project": result,
            "models": models_result,
            "datasets": datasets_result,
        }

    async def get_projects_of_user(self):
        query = select(users.c.username, projects.c.id_projects, projects.c.name, projects.c.description).select_from(
            users.join(projects, projects.c.id_users == users.c.id_users)
            ).where(users.c.username == self.__username)
        result = await database.fetch_all(query)
        return result

    def create_user_folder(self):
        """
        создаёт директорию для пользователя /self.name на диске сервера \\
        так же папку с проектами PROJECTS/

        Raises:
            FileExistsError: наличие папки пользователя
        """
        
        if UserStorageService.storage_full_path == "": return 0
        
        try:
            Path(UserStorageService.storage_full_path + f"/USERS/{self.__username}").mkdir(parents=True)
            Path(UserStorageService.storage_full_path + f"/USERS/{self.__username}/PROJECTS/").mkdir(parents=True)
        except FileExistsError as e:
            raise e
        
    async def get_project_data(self, username: str, id_projects: int):
        """
        получение основной инфрормации о проекте пользователя
        
        Raises:
            status.HTTP_404_NOT_FOUND: проект с названием project_name у пользователя username не найден
            status.HTTP_400_BAD_REQUEST: пользователь с ником username не найден
        """
        
        if UserStorageService.storage_full_path == "": return 0

        try:
            selected_users = await database.fetch_one(
                users.select().where(users.c.username == username)
                )
            
            if not selected_users:
                raise HTTPException(
                        status_code = status.HTTP_400_BAD_REQUEST, 
                        detail = "the user does not exist"
                    )
            
            project = await database.fetch_one(
                projects.select().where(
                    projects.c.id_users == selected_users['id_users'], 
                    projects.c.id_projects == id_projects
                )
            )

            if not project:
                raise HTTPException(
                        status_code = status.HTTP_404_NOT_FOUND, 
                        detail = "project does not exist"
                    )
            
            project_datasets = await database.fetch_all(
                datasets.select().select_from(
                    datasets.join(
                        projects_datasets,
                        datasets.c.id_datasets == projects_datasets.c.id_datasets
                    )
                ).where(
                    projects_datasets.c.id_projects == id_projects
                )
            )
            
            return {
                "project_datasets" : [dict(row) for row in project_datasets]
                }

        except Exception as e:
            return {"error": str(e)}
            # raise HTTPException(
            #     status_code = status.HTTP_409_CONFLICT, 
            #     detail = "Error occurred"
            #     )

    async def create_project(self, project_name: str, description: str = ""):
        """
        создаёт директорию для проекта и добавляет его в БД

        Raises HTTPException:
            HTTP_400_BAD_REQUEST: Имя проекта содержит символы помимо букв и цифр
            HTTP_401_UNAUTHORIZED: совпадение логина и пароля
            HTTP_409_CONFLICT: наличие репозитория с таким же названием
        """

        if UserStorageService.storage_full_path == "": 
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                detail = "Storage path is not set")
        if not project_name.isalnum(): 
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                detail = "Project name must contains only letters and numbers")

        try:
            Path(UserStorageService.storage_full_path + f"/USERS/{self.__username}/PROJECTS/{project_name}").mkdir(parents=True)
            readme_path = Path(UserStorageService.storage_full_path + f"/USERS/{self.__username}/PROJECTS/{project_name}/README.md")
            readme_path.write_text(description, encoding="utf-8")
            query = users.select().where(users.c.username == self.__username)
            existing_user = await database.fetch_one(query)

            if existing_user:
                stmt = insert(projects).values(
                    name = project_name,
                    description = description,
                    id_users = existing_user.id_users
                )
                stmt.compile()
                await database.execute(stmt)
            else:
                raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, 
                                    detail = "Wrong login or password")
        except FileExistsError:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                detail = "Project already exists")
        
    async def delete_project(self, project_name: str):
        """
        Удаление проекта. Удаляет папку и запись в БД

        Raises:
            status.HTTP_401_UNAUTHORIZED: совпадение логина и пароля
            status.HTTP_409_CONFLICT": отсутствие проекта
        """
        if UserStorageService.storage_full_path == "": return 0

        try:
            project = Path(UserStorageService.storage_full_path + f"/USERS/{self.__username}/PROJECTS/{project_name}")
            query = users.select().where(users.c.username == self.__username)
            existing_user = await database.fetch_one(query)

            if existing_user and project.exists():
                stmt = delete(projects).where(
                    projects.c.id_users == existing_user.id_users,
                    projects.c.name == project_name
                )
                stmt.compile()
                await database.execute(stmt)

                shutil.rmtree(project)
            else:
                raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, 
                                    detail = "Wrong login or password")
        except FileNotFoundError:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                detail = "Project does not exist")
        
    async def upload_file(self,
                          project_name: str, 
                          file: UploadFile):
        """
        загрузка файла в проект

        Raises:
            status.HTTP_422_UNPROCESSABLE_CONTENT: папка и файл не могут иметь одно название
            Exception: непредвиденная ошибка. Вероятно, связанная с правами доступа к директории
        """
        path = Path(self.storage_full_path) / "USERS" / self.__username / "PROJECTS" / project_name / file.filename

        if project_name == file.filename:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, 
                detail="folder and file cannot have the same name"
            )

        try:
            async with aiofiles.open(path, "wb") as out:
                content = await file.read()
                await out.write(content)
        except Exception as e: 
            raise e
        
    async def edit_file(self,
                        project_name: str,
                        file_to_overwrite: str, 
                        file: UploadFile):
        """
        Обновление файла файла в проект

        Raises:
            status.HTTP_422_UNPROCESSABLE_CONTENT: папка и файл не могут иметь одно название
            Exception: непредвиденная ошибка. Вероятно, связанная с правами доступа к директории
        """
        path = Path(self.storage_full_path) / "USERS" / self.__username / "PROJECTS" / project_name / file_to_overwrite

        if not path.is_file(): 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="file does not exist"
            ) 

        if project_name == file.filename:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, 
                detail="folder and file cannot have the same name"
            )

        try:
            async with aiofiles.open(path, "wb") as out:
                content = await file.read()
                await out.write(content)
        except Exception as e: 
            raise e
        
    # не работает | нужно доработать
    async def get_project_info(self,
                               owner: str,
                               project_name: str):
        """
        возвращает repo_id и структуру проекта - tree
        Raises:
            
        """
        dirPath = f"{UserStorageService.storage_full_path}/USERS/{owner}/PROJECTS/{project_name}"
        list_files("C:")


    async def get_models(self, project_name: str):
        query = users.select().where(users.c.username == self.__username)
        user = await database.fetch_one(query)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        query = projects.select().where(and_(projects.c.name == project_name, projects.c.id_users == user["id_users"]))
        project = await database.fetch_one(query)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_id = project.id_projects
        
        query = (
            select(models)
            .join(projects_models, models.c.id_models == projects_models.c.id_models)
            .where(projects_models.c.id_projects == project_id)
        )
        
        models_rows = await database.fetch_all(query)
        
        return models_rows


    async def addModel(self, project_name, model_name):
        """
        Добавляет модель в проект

        project_name, model_name - в формате 'автор/название'
        """
        query = models.select().where(models.c.name == model_name)
        model = await database.fetch_one(query)

        if model is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Model {model_name} was not found"
            )
        
        query = projects.select().where(projects.c.name == project_name)
        project = await database.fetch_one(query)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Project {project_name} was not found"
            )

        query = projects_models.select().where(and_(projects_models.c.id_projects == project.id_projects,
                                               projects_models.c.id_models == model.id_models))
        proj_model_link = await database.fetch_one(query)

        if not proj_model_link is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Model is already added"
            )

        query = projects_models.insert().values(id_projects=project.id_projects,
                                               id_models=model.id_models)
        await database.execute(query)


    async def removeModel(self, project_name, model_name):
        """
        Удаляет модель из проекта
        """
        query = models.select().where(models.c.name == model_name)
        model = await database.fetch_one(query)

        if model is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Model {model_name} was not found"
            )
        
        query = projects.select().where(projects.c.name == project_name)
        project = await database.fetch_one(query)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Project {project_name} was not found"
            )

        query = projects_models.delete().where(and_(projects_models.c.id_projects == project.id_projects,
                                               projects_models.c.id_models == model.id_models))
        await database.execute(query)


    async def get_datasets(self, project_name: str):
        query = users.select().where(users.c.username == self.__username)
        user = await database.fetch_one(query)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        query = projects.select().where(and_(projects.c.name == project_name, projects.c.id_users == user["id_users"]))
        project = await database.fetch_one(query)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_id = project.id_projects
        
        query = (
            select(datasets)
            .join(projects_datasets, datasets.c.id_datasets == projects_datasets.c.id_datasets)
            .where(projects_datasets.c.id_projects == project_id)
        )
        
        datasets_rows = await database.fetch_all(query)
        
        return datasets_rows


    async def addDataset(self, project_name, dataset_name):
        """    
        Добавляет датасет в проект

        project_name, dataset_name - в формате 'автор/название'
        """
        query = datasets.select().where(datasets.c.name == dataset_name)
        dataset = await database.fetch_one(query)

        if dataset is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Dataset {dataset_name} was not found"
            )
        
        query = projects.select().where(projects.c.name == project_name)
        project = await database.fetch_one(query)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Project {project_name} was not found"
            )

        query = projects_datasets.select().where(and_(projects_datasets.c.id_projects == project.id_projects,
                                               projects_datasets.c.id_datasets == dataset.id_datasets))
        proj_dataset_link = await database.fetch_one(query)

        if not proj_dataset_link is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Dataset is already added"
            )

        query = projects_datasets.insert().values(id_projects=project.id_projects,
                                               id_datasets=dataset.id_datasets)
        await database.execute(query)


    async def removeDataset(self, project_name, dataset_name):
        """
        Удаляет модель из проекта
        """
        query = datasets.select().where(datasets.c.name == dataset_name)
        dataset = await database.fetch_one(query)


        if dataset is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Dataset {dataset_name} was not found"
            )
        
        query = projects.select().where(projects.c.name == project_name)
        project = await database.fetch_one(query)


        if project is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Project {project_name} was not found"
            )
        query = projects_datasets.delete().where(and_(projects_datasets.c.id_projects == project.id_projects,
                                               projects_datasets.c.id_datasets == dataset.id_datasets))
        await database.execute(query)


    async def runModel(self, 
                       project_name: str, 
                       model_name: str, 
                       dataset_name: str, 
                       filepath: str, 
                       text_key: str | None = None, 
                       ner_key: str | None = None, 
                       threshold: float | None = None):
        """
        Запускает выполнение модели на указанном датасете
        filepath - путь до файла .jsonl с данными
        text_key - ключ в файле, содержащий текст

        Raises:
            HTTPException:
                * HTTP_409_CONFLICT ошибка чтения файла датасета
                * HTTP_400_BAD_REQUEST модели/датасета/прокта не существует
        """
        kwargs = {} # проверка на None передаваемых параметров
        if text_key is not None:
            kwargs['text_key'] = text_key
        if ner_key is not None:
            kwargs['ner_key'] = ner_key
        if threshold is not None:
            kwargs['threshold'] = threshold

        query = projects.select().where(projects.c.name == project_name)
        project = await database.fetch_one(query)

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Project {project_name} was not found"
            )

        mf = ModelsFolder(model_name)
        results = await mf.run_model(project.id_projects, dataset_name, 
                                     filepath, **kwargs)
        return results