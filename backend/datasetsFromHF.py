from huggingface_hub import snapshot_download
from huggingface_hub.utils import (
    RepositoryNotFoundError,
    RevisionNotFoundError,
    EntryNotFoundError,
    LocalEntryNotFoundError,
    HfHubHTTPError,
)
import shutil
# модуль для установки с моделями с HuggingFace

class DatasetsFolder:
    local_dir_ = ""

    def set_local_dir(self, local_dir: str):
        """
        установка директории для хранения датасетов \\
        Ожидаемо: STORAGE_FULL_PATH/DATASETS
        """
        DatasetsFolder.local_dir_ = f"{local_dir}\\DATASETS"

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

data = DatasetsFolder()
data.set_local_dir("C:\\Users\\lagge\\Desktop\\projects\\MORI\\backend\\folder")

# test
# data.download_dataset("Ujjwal-Tyagi/ai-ml-foundations-book-collection")
# data.download_dataset("TeichAI/claude-4.5-opus-high-reasoning-250x")
# data.download_dataset("TeichAI/gpt-5.2-high-reasoning-250x")

