import aiofiles
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
        async with aiofiles.open(path, "r") as file:
            content = await file.read()
        return content