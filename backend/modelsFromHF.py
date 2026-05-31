from huggingface_hub import snapshot_download
from huggingface_hub.errors import RepositoryNotFoundError, LocalEntryNotFoundError
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
from fastapi import FastAPI, HTTPException, status, Response
from db import database, STORAGE_FULL_PATH
from sqlalchemy import select
import asyncio
import aiofiles
import shutil
from pathlib import Path
import json
from torch import no_grad, softmax

from models import models, datasets
from datasetsFromHF import DatasetsFolder
from metrics import *

class ModelsFolder:
    """
        Модуль для работы с моделями из HuggingFace
    """
    local_dir_ = Path(STORAGE_FULL_PATH) / Path("MODELS")
    def __init__(self, model_name: str):
        """
        model_name - репозиторий модели (автор/модель)
        """
        self.model_name = model_name
        self.full_path = ModelsFolder.local_dir_ / Path(model_name)
      
    @staticmethod 
    async def sync_models():
        """
        Синхронизирует файловую структуру БД и файловой системы
        1) добавлет в бд модели из папки,
        2) загружает в папки модели из бд если есть ссылка на источник
        3) Иначе удаляет
        Результат выводится в консоль
        """
        
        # Сканирование хранилища и добавление в БД
        print("Сканирование хранилища и добавление в БД")
        for author_folder in ModelsFolder.local_dir_.iterdir():
            if author_folder.is_file():
                continue
            print("----", author_folder.name, "----")
            model_folder = [model_folder for model_folder in author_folder.iterdir() if model_folder.is_dir()]

            # работает для моделей от huggingface
            if len(model_folder) != 1:
                print("Имеет некорректную файловую структуру, пропускаю")
                continue
            model_folder = model_folder[0]
            
            model_name = f"{author_folder.name}/{model_folder.name}"
            query = models.select().where(models.c.name == model_name)
            existing_model = await database.fetch_one(query)
            if existing_model:
                print("Уже синхронизировано")
                continue

            query = models.insert().values(name=model_name, folder_path=model_folder.path)
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
            if Path.exists(model.folder_path):
                print("Уже синхронизировано")
                continue

            try:
                # т.к. snapshot_download не асинхронный
                await asyncio.to_thread(snapshot_download, model.name, local_dir=f"{model.full_path}")
            except Exception as e:
                print("Произошла ошибка при загрузке модели с huggingface:", e)


    @staticmethod
    async def get_models():
        """
        Возвращает все модели в БД
        """
        return await database.fetch_all(models.select())

    
    async def create_model(self, orig_model_id: int = None):
        """
        Загружает модель с huggingface и создает запись в бд
        orig_model_id: optional - номер модели-родителя
        ModelsFolder.model_name должен содержать путь до репозитория
        
        Raises:
            HTTP_409_CONFLICT: модель уже существует
            HTTP_400_BAD_REQUEST: репозитория не существует
            HTTP_406_NOT_ACCEPTABLE: не удалось подключиться к репозиторию
        """
        query = models.select().where(models.c.name == self.model_name)
        existing_model = await database.fetch_one(query)

        if existing_model:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                                    detail = f"Model {self.model_name} already exist!")
        print(f"downloading model: {self.model_name}")
        try:
            await asyncio.to_thread(snapshot_download, self.model_name, local_dir=f"{self.full_path}")
        except(RepositoryNotFoundError):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Repository {self.model_name} does not exist!")

        except(LocalEntryNotFoundError):
            raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, 
                        detail = "Can't connect to repository!")
    

        query = models.insert().values(name=self.model_name, folder_path=str(self.full_path),
                                        id_original_model=orig_model_id)
        await database.execute(query)


    async def delete_model(self):
        """
        Удаляет модель
        
        Raises:
            HTTPException:
                * HTTP_409_CONFLICT невозможно удалить, модель используется,
                * HTTP_400_BAD_REQUEST модели не существует
        """
        query = models.select().where(models.c.name == self.model_name)
        existing_model = await database.fetch_one(query)
        if existing_model is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Model {self.model_name} does not exist!")
        
        if Path.exists(self.full_path):
            try:
                shutil.rmtree(self.full_path)
            except(OSError):
                raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                        detail = f"Model {self.model_name} is currently in use!")
        query = models.delete().where(models.c.id_models == existing_model.id_models)
        await database.execute(query)


    async def get_model_info(self):
        """
        Возвращает часть информации из config.json
        
        Raises:
            HTTPException:
                * HTTP_409_CONFLICT файл config.json не найден,
                * HTTP_400_BAD_REQUEST модели не существует
        """
        query = models.select().where(models.c.name == self.model_name)
        model = await database.fetch_one(query)
        if model is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Model {self.model_name} does not exist!")
        if Path.exists(self.full_path):
            useful_fields = { # TODO: некоторые поля имеют вариации названий 
                "_name_or_path": "name",
                "n_layers": "n_layers",
                "activation": "activation",
                "architectures": "architectures",
                "num_hidden_layers": "num_hidden_layers",
                "hidden_size": "hidden_size",
                "hidden_act": "hidden_act",
                "id2label": "id2label",
                "model_type": "model_type",
                "vocab_size": "vocab_size"
            }
            try:
                with open(model.folder_path / Path("config.json")) as config:
                    data = json.load(config)

                    info = dict()
                    for key in useful_fields.keys():
                        if key in data:
                            # записывает значение в info с переименованием ключа
                            info[useful_fields[key]] = data[key]
                    return info
                    
            except OSError:
                raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                        detail = f"Config file not found!")
            
    
    async def get_labels(self):
        labels = None
        if not Path.exists(self.full_path):
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                        detail = f"Model folder not found!")
        try:
            async with aiofiles.open(self.full_path / "config.json", "r", encoding="utf-8") as config:
                content = await config.read()
                data = dict(json.loads(content)["id2label"])
                labels = set([data[str(i)].upper() for i in range(len(data))])
        except OSError:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                    detail = f"Config file not found!")
        return labels
            

    def __pred__(self, words, tokenizer, model):
        """
            Вся эта функция лишь для того, чтобы откллючить 
            разбинение слов на части токенизатором модели.

            Получает предсказание модели на тексте.
        """
        enc = tokenizer(
            words,
            is_split_into_words=True,
            return_tensors="pt",
            truncation=True
        )

        with no_grad():
            outputs = model(**enc)

        logits = outputs.logits[0]
        probs = softmax(logits, dim=-1)
        pred_ids = probs.argmax(dim=-1).tolist()
        word_ids = enc.word_ids(batch_index=0)

        words_r = []
        ner_r = []
        score_r = []

        seen_words = set()

        for token_idx, word_idx in enumerate(word_ids):
            if word_idx is None or word_idx in seen_words:
                continue

            seen_words.add(word_idx)

            pred_id = pred_ids[token_idx]
            label = model.config.id2label[pred_id]
            score = probs[token_idx, pred_id].item()

            words_r.append(words[word_idx])
            ner_r.append(label)
            score_r.append(score)

        return {                
                "words": words_r,
                "ner": ner_r,
                "score": score_r
                }


    async def run_model(self, project_id, dataset_repo: str, filepath: str, text_key: str = "words"):
        """
        Запускает модели на данных, 
        dataset_repo - датасет
        filepath - путь до файла .jsonl с данными
        text_key - ключ в файле, содержащий текст

        при создания файла со списком меток датасета ожидает
        что метки находятся по ключу "ner"
        
        Raises:
            HTTPException:
                * HTTP_409_CONFLICT ошибка чтения файла датасета
                * HTTP_400_BAD_REQUEST модели/датасета не существует
        """
        query = models.select().where(models.c.name == self.model_name)
        db_model = await database.fetch_one(query)
        if db_model is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Model {self.model_name} does not exist!")
        
        query = datasets.select().where(datasets.c.name == dataset_repo)
        db_dataset = await database.fetch_one(query)
        if db_dataset is None:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                                    detail = f"Dataset {dataset_repo} does not exist!")
                    
        dataset = DatasetsFolder()
        # Получение списка меток
        model_labels = await self.get_labels()
        dataset_labels = await dataset.get_labels_list(dataset_repo, filepath, "ner")

        model_diff = model_labels - dataset_labels # есть в модели но нет в датасете
        ds_diff = dataset_labels - model_labels # есть в датасете но нет в модели
        print("model_diff:", model_diff)
        print("ds_diff:", ds_diff)
        if len(ds_diff) > 0: # в датасете больше меток
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, 
                        detail = f"Dataset has labels {ds_diff} that model does not")

        tokenizer = AutoTokenizer.from_pretrained(self.full_path)
        model = AutoModelForTokenClassification.from_pretrained(self.full_path)
        nlp = pipeline("token-classification", model=model, tokenizer=tokenizer, ignore_labels=list(model_diff)) 
        # ignore_labels - не выдавать в результате слова с этими метками, aggregation_strategy='none', 'simple', 'first', 'average', 'max'

        json_data = await dataset.read_file(dataset_repo, filepath)
        data = []

        try:
            for line in json_data:
                if line != "":
                    data.append(json.loads(line))
        except Exception as e:
            raise HTTPException(status_code = status.HTTP_409_CONFLICT, 
                        detail = f"Exception occured when reading file: {e}")

        results = []
        for line in data:
            answer = self.__pred__(line[text_key], tokenizer, model)
            # print(line[text_key])
            # print()
            # print(results)
            # print()
            results.append(answer)
        metrics = await calcMetrics(data, results, text_key)
        await storeResults(metrics, project_id, db_dataset.id_datasets, db_model.id_models)
        return metrics


