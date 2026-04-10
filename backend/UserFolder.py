from pathlib import Path
import shutil


from fastapi import FastAPI, HTTPException, status, Response
from models import users, projects
from db import database, STORAGE_FULL_PATH
from sqlalchemy import insert, update, delete


def create_file_system_structure(storage_full_path:str):
    """
    создаёт структуру файловой системы по указанному пути
    """
    base = Path(storage_full_path)
    for f in ["MODELS", "DATASETS", "USERS"]:
            (base / f).mkdir(parents=True, exist_ok=True)

class UserFolder:
    storage_full_path = STORAGE_FULL_PATH

    def __init__(self, name: str):
        self.name_ = name

    def create_user_folder(self):
        """
        создаёт директорию для пользователя /self.name на диске сервера \\
        так же папку с проектами PROJECTS/
        """
        
        if UserFolder.storage_full_path == "": return 0
        
        try:
            Path(UserFolder.storage_full_path + f"/USERS/{self.name_}").mkdir(parents=True)
            Path(UserFolder.storage_full_path + f"/USERS/{self.name_}/PROJECTS/").mkdir(parents=True)
            return 1
        except FileExistsError:
            return 0
        
    async def create_project_folder(self, project_name: str, description: str = ""):
        """
        создаёт директорию для проекта
        """

        if UserFolder.storage_full_path == "": return 0

        try:
            Path(UserFolder.storage_full_path + f"/USERS/{self.name_}/PROJECTS/{project_name}").mkdir(parents=True)
            readme_path = Path(UserFolder.storage_full_path + f"/USERS/{self.name_}/PROJECTS/{project_name}/README.md")
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
        
    async def delete_project_folder(self, project_name: str):

        if UserFolder.storage_full_path == "": return 0

        try:
            project = Path(UserFolder.storage_full_path + f"/USERS/{self.name_}/PROJECTS/{project_name}")
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
        except FileExistsError:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                detail = "Project already exists")