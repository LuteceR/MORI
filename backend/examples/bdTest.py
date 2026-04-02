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


# Считываем конфиг из .env
config = ConfigBase()

db_params = {
    "host": config.bd_addr,
    "database": config.bd_name,
    "user": config.bd_user,
    "password": config.bd_password,
    "port": config.bd_port
}

def printUsers():
    # Выполнить запрос
    cur.execute("SELECT * FROM users")

    # Retrieve query results
    records = cur.fetchall() # или cur.fetchone()
    print(records)

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

printUsers()

cur.close()
conn.close()