from sqlalchemy import create_engine, MetaData, Table
from databases import Database

import psycopg2

from pydantic_settings import BaseSettings, SettingsConfigDict

class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="settings/.env", env_file_encoding="utf-8", extra="ignore"
    )
    bd_addr: str
    bd_port: str
    bd_name: str
    bd_user: str
    bd_password: str
    secret_key: str


# Считываем конфиг из .env
config = ConfigBase()

SECRET_KEY = config.secret_key

DATABASE_URL = f"postgresql+psycopg2://{config.bd_user}:{config.bd_password}@{config.bd_addr}:{config.bd_port}/{config.bd_name}"

database = Database(DATABASE_URL)
metadata = MetaData()

engine = create_engine(
    DATABASE_URL
)

