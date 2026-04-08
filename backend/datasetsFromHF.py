from huggingface_hub import snapshot_download 
# модуль для установки с моделями с HuggingFace

class DatasetsFolder:
    local_dir_ = ""

    def set_local_dir(local_dir: str):
        """
        установка local_dir - расположения .../DATASETS
        """
        DatasetsFolder.local_dir_ = local_dir

    def download_model(repo_id: str):
        """
        установка модели с Hugging face
        """
        snapshot_download(repo_id=repo_id,
                          repo_type="dataset",
                          local_dir=f"{DatasetsFolder.local_dir_}/{repo_id}")