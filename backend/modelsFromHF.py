from huggingface_hub import snapshot_download 
# модуль для установки с моделями с HuggingFace

class ModelsFolder:
    local_dir_ = ""

    def set_local_dir(local_dir: str):
        """
        установка local_dir - расположения .../MODELS
        """
        ModelsFolder.local_dir_ = local_dir

    def download_model(repo_id: str):
        """
        установка модели с Hugging face
        """
        snapshot_download(repo_id=repo_id, 
                        local_dir=f"{ModelsFolder.local_dir_}/{repo_id}")