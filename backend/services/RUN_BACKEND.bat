@echo off
chcp 65001 >nul

:: Определяем папку с venv (проверяем .venv и venv)
set VENV_DIR=
if exist "%CD%\.venv\Scripts\activate.bat" set VENV_DIR=.venv
if exist "%CD%\venv\Scripts\activate.bat" set VENV_DIR=venv

if "%VENV_DIR%"=="" (
    echo Ошибка: не найдена папка .venv или venv в %CD%
    pause
    exit /b 1
)

set ACTIVATE=%CD%\%VENV_DIR%\Scripts\activate.bat
set BACKEND_PATH=%CD%\backend

start "AUTH 8001" cmd /k "cd /d %BACKEND_PATH% && call "%ACTIVATE%" && set PYTHONPATH=%BACKEND_PATH% && granian --interface asgi services.service_auth:app --port 8001"
start "DATASETS 8002" cmd /k "cd /d %BACKEND_PATH% && call "%ACTIVATE%" && set PYTHONPATH=%BACKEND_PATH% && granian --interface asgi services.service_datasets:app --port 8002"
start "MODELS 8003" cmd /k "cd /d %BACKEND_PATH% && call "%ACTIVATE%" && set PYTHONPATH=%BACKEND_PATH% && granian --interface asgi services.service_models:app --port 8003"
start "PROJECTS 8004" cmd /k "cd /d %BACKEND_PATH% && call "%ACTIVATE%" && set PYTHONPATH=%BACKEND_PATH% && granian --interface asgi services.service_projects:app --port 8004"

echo Все сервисы запущены.