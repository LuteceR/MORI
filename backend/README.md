### Установка
Создание виртуальной среды и зугрузка зависимостей
```
cd backend
python -m venv .venv
pip install -r requirements.txt
```


### ЗАПУСК
```uvicorn services.service_auth:app --host localhost --port 8001```
```uvicorn services.service_datasets:app --host localhost --port 8002```
```uvicorn services.service_models:app --host localhost --port 8003```
```uvicorn services.service_projects:app --host localhost --port 8004```

### ЗАПУСК в Docker
Сборка образа (из корня репозитория):
```
docker build -t mori-backend ./backend
```

Запуск с настройками PostgreSQL из `backend/settings/.env` и постоянным хранилищем:
```
docker run --rm -p 8000:8000 --env-file backend/settings/.env -e STORAGE_FULL_PATH=/app/userdata -v mori-backend-data:/app/userdata mori-backend
```
Значения `BD_ADDR`, `BD_PORT`, `BD_NAME`, `BD_USER`, `BD_PASSWORD` и `SECRET_KEY` должны быть заданы в env-файле. Адрес PostgreSQL должен быть доступен из контейнера. Данные из `backend/folder` в образ не включаются; подключите их отдельно в `/app/userdata`, если они нужны.

Для получения секретного ключа (выполнить в git):\
```openssl rand -hex 32```

или для windows (в PowerShell):\
```(1..32 | %{ [byte](Get-Random -Max 256) } | ForEach { '{0:x2}' -f $_ }) -join ''```

### ЗАПУСК с granian
```
pip install granian
granian --interface asgi app_granian:app --access-log
```
access-log для вывода входящих запросов

### ЗАПУСК в локальной сети
Для этого надо установить в .env фронтенда адреса и порты сервисов бекэнда,\
Выполнить запуск сервисов без параметра --reload, можно добавить "--workers 2" но оно кажется не работает\
Отключить брандмауер для данной сети\
Запустить фронтенд:
```npx nuxt dev -- --host```
### Сайт доступен локально по адресу:

http://127.0.0.1:8000

http://127.0.0.1:8000/docs

http://127.0.0.1:8000/redoc (альтернатива)

### Доп информация

Модуль для построения дерева зависимостей
```
pip install pipdeptree

pipdeptree -d 0
```

-d - глубина дерева при 0 вывод самих модулей, без их зависимостей