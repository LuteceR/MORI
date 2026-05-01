import aiofiles
from fastapi import FastAPI, HTTPException, status, Response
from huggingface_hub import snapshot_download
from huggingface_hub.utils import (
    RepositoryNotFoundError,
    RevisionNotFoundError,
    EntryNotFoundError,
    LocalEntryNotFoundError,
    HfHubHTTPError,
)
import shutil
from pathlib import Path
# модуль для установки с моделями с HuggingFace

class DatasetsFolder:
    local_dir_ = Path()

    def set_local_dir(self, local_dir: str):
        """
        установка директории для хранения датасетов \\
        Ожидаемо: STORAGE_FULL_PATH/DATASETS
        """
        DatasetsFolder.local_dir_ = Path(local_dir) / "DATASETS"

    def download_dataset(self, repo_id: str):
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
        try:
            snapshot_download(repo_id=repo_id,
                            repo_type="dataset",
                            local_dir=f"{DatasetsFolder.local_dir_}/{repo_id}")
        except Exception:
            raise


    def delete_dataset(self, repo_id: str):
        """
        удаление датасета с Hugging face

        Raises:
            FileNotFoundError: датасет не был найден
        """
        try:
            shutil.rmtree(f"{self.local_dir_}/{repo_id}")
        except FileNotFoundError:
            raise

    def build_tree(self, path: Path):
        tree = []
        path = self.local_dir_ / path

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
    
    async def read_file(self, dataset: str, filepath: str):
        """
        чтение файла с локальным путём filepath из датасета.
        dataset - глобальный путь к датасету
        """
        path = self.local_dir_ / dataset / Path(filepath)
        # path = path.join(Path(filepath))
        content = []
        async with aiofiles.open(path, "r", encoding="utf-8") as file:
            while True:
                line = await file.readline()
                content.append(line)
                if not line:
                    break
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
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="file does not exist"
            ) 

        try:
            async with aiofiles.open(path, "wb") as out:
                await out.write(content.encode())
        
        except Exception as e: 
            raise e