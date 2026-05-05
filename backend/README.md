### Установка
Создание виртуальной среды и зугрузка зависимостей
```
cd backend
python -m venv .venv
pip install -r requirements.txt
```


### ЗАПУСК
```fastapi dev``` - вкл. автоперезагрузка при изменении, подробные ошибки, запуск сервера с документацией (/docs)

```granian --interface asgi app:app``` - альтернативный вариант

```fastapi run``` - простой запуск

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