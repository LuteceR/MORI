import aiofiles
from fastapi import FastAPI, HTTPException, status, Response
from huggingface_hub import snapshot_download, DatasetCard
from huggingface_hub.utils import (
    RepositoryNotFoundError,
    RevisionNotFoundError,
    EntryNotFoundError,
    LocalEntryNotFoundError,
    HfHubHTTPError,
)
from fastapi import HTTPException, status
import asyncio
import json
import shutil
from pathlib import Path

from db import database, STORAGE_FULL_PATH
from models import datasets

class DatasetsFolder:
    """
    Модуль для работы с датасетами с HuggingFace
    """
    local_dir_ = Path(STORAGE_FULL_PATH) / Path("DATASETS")

    @staticmethod
    async def get_datasets():
        """
        Возвращает все датасеты в БД
        """
        return await database.fetch_all(datasets.select())

    async def get_all_datasets(self):
        query = datasets.select()
        res = await database.fetch_all(query)
        
        for dataset in res:
            try:
                card = DatasetCard.load(dataset["name"])
                metadata = card.data.to_dict()
                metadata['name'] = dataset["name"]
                print(metadata)
                yield metadata
            except Exception as err:
                print("ERROR\n", err)


    async def get_labels_list(self, dataset: str, filepath: str, ner_key: str = "ner") -> set:
        """
        Возвращает список меток в файле датасета,
        при этом создает файл с именем `<filepath>_labels.txt` куда записывает метки
        и при повторном запуски считывает метки от туда
        
        """
        file = self.local_dir_ / dataset / (str(Path(filepath).with_suffix("")) + "_labels.txt")
        labels_list = set()
        # Если файл с метками уже существует
        if file.is_file():
            with open(file, 'r', encoding="utf-8") as f:
                for line in f.readlines():
                    labels_list.add(line.strip())
            return labels_list

        data = await self.read_file(dataset, filepath)
        try:
            for line in data:
                if len(line.strip()) == 0: continue
                labels = json.loads(line)[ner_key]
                labels_list.update(labels)
        except json.JSONDecodeError:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Invalid label's key or file")
        
        labels_list = set([x.upper().strip() for x in labels_list])
        
        with open(file, "w", encoding="utf-8") as f:
            for label in labels_list:
                f.write(label + "\n")
        return labels_list


    async def download_dataset(self, repo_id: str):
        """
        установка датасета с Hugging face

        Raises:
            RepositoryNotFoundError: репозиторий не найден или нет доступа
            RevisionNotFoundError: неверная версия (branch/tag/commit)
            EntryNotFoundError: файл не найден в репозитории
            LocalEntryNotFoundError: нет локального кэша при offline режиме
            HfHubHTTPError: ошибка HTTP
            Exception: неизвестная ошибка
        """
        query = datasets.select().where(datasets.c.name == repo_id)
        existing_dataset = await database.fetch_one(query)

        if existing_dataset:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                    detail = f"Dataset {repo_id} already exist!")

        try:
            await asyncio.to_thread(
                snapshot_download,
                repo_id=repo_id,
                repo_type="dataset",
                local_dir=f"{DatasetsFolder.local_dir_}/{repo_id}"
            )
        except(RepositoryNotFoundError):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Repository {repo_id} does not exist!")
        except(LocalEntryNotFoundError):
            raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, 
                        detail = "Can't connect to repository!")

        query = datasets.insert().values(name=repo_id, url_source=f"https://huggingface.co/datasets/{repo_id}",
                                folder_path=str(self.local_dir_ / repo_id))
        await database.execute(query)

    async def delete_dataset(self, repo_id: str):
        """
        удаление датасета с Hugging face

        Raises:
            FileNotFoundError: датасет не был найден
        """
        query = datasets.select().where(datasets.c.name == repo_id)
        existing_dataset = await database.fetch_one(query)
        if existing_dataset is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Dataset {repo_id} does not exist!")

        try:
            shutil.rmtree(f"{self.local_dir_}/{repo_id}")
        except(OSError):
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                detail = f"Dataset {repo_id} is currently in use!")
    
        query = datasets.delete().where(datasets.c.id_datasets == existing_dataset.id_datasets)
        await database.execute(query)

    def build_tree(self, path: Path):
        tree = []
        # path = self.local_dir_ / path

        for el in path.iterdir():
            if el.is_file():
                tree.append({
                    "label": el.name,
                    "suffix": el.suffix
                })
            else:
                tree.append({
                    "label": el.name,
                    "children": self.build_tree(el)
                })
                
        return tree
    

    async def read_file(self, dataset: str, filepath: str) -> list:
        """
        чтение файла с локальным путём filepath из датасета.
        dataset - глобальный путь к датасету
        """
        path = self.local_dir_ / dataset / Path(filepath)
        # path = path.join(Path(filepath))
        content = []
        try:
            async with aiofiles.open(path, "r", encoding="utf-8") as file:
                while True:
                    line = await file.readline()
                    content.append(line)
                    if not line:
                        break
        except FileNotFoundError:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"File {filepath} does not exist!")
        return content
    

    async def save_file_changes(self,
                                dataset: str,
                                filename: str,
                                content: str):
        """
        Сохранение изменений в файле

        Raises:
            status.HTTP_422_UNPROCESSABLE_CONTENT: файла не существует
            Exception: непредвиденная ошибка. Вероятно, связанная с правами доступа к директории
        """
        path = Path(self.local_dir_) / dataset / filename

        if not path.is_file(): 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="file does not exist"
            ) 

        try:
            async with aiofiles.open(path, "wb") as out:
                await out.write(content.encode())
        
        except Exception as e: 
            raise e