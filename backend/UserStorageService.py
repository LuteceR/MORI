import asyncio
from pathlib import Path
import shutil

import os

from fastapi import FastAPI, HTTPException, status, Response
from fastapi import HTTPException
from fastapi import File, UploadFile

from directory_tree import DisplayTree

import aiofiles

from models import users, projects
from db import database, STORAGE_FULL_PATH
from sqlalchemy import insert, select, update, delete


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

    def __init__(self, name: str):
        self.name_ = name

    async def get_user_projects(self):
        query = select(users.c.username, projects.c.name, projects.c.description).select_from(
            users.join(projects, projects.c.id_users == users.c.id_users)
            ).where(users.c.username == self.name_)
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
            Path(UserStorageService.storage_full_path + f"/USERS/{self.name_}").mkdir(parents=True)
            Path(UserStorageService.storage_full_path + f"/USERS/{self.name_}/PROJECTS/").mkdir(parents=True)
        except FileExistsError as e:
            raise e
        
    async def create_project(self, project_name: str, description: str = ""):
        """
        создаёт директорию для проекта и добавляет его в 

        Raises:
            status.HTTP_401_UNAUTHORIZED: совпадение логина и пароля
            status.HTTP_409_CONFLICT: наличие репозитория с таким же названием
        """

        if UserStorageService.storage_full_path == "": return 0

        try:
            Path(UserStorageService.storage_full_path + f"/USERS/{self.name_}/PROJECTS/{project_name}").mkdir(parents=True)
            readme_path = Path(UserStorageService.storage_full_path + f"/USERS/{self.name_}/PROJECTS/{project_name}/README.md")
            readme_path.write_text(description, encoding="utf-8")
            query = users.select().where(users.c.username == self.name_)
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
            project = Path(UserStorageService.storage_full_path + f"/USERS/{self.name_}/PROJECTS/{project_name}")
            query = users.select().where(users.c.username == self.name_)
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
        path = Path(self.storage_full_path) / "USERS" / self.name_ / "PROJECTS" / project_name / file.filename

        if project_name == file.filename:
            return HTTPException(
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
        path = Path(self.storage_full_path) / "USERS" / self.name_ / "PROJECTS" / project_name / file_to_overwrite

        if not path.is_file(): 
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="file does not exist"
            ) 

        if project_name == file.filename:
            return HTTPException(
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