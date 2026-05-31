:: ЗАПУСКАТЬ ИЗ ПАПКИ /backend в среде для Python .venv
@echo off
chcp 65001 >nul

call set PARENT_DIR=%CD%
set PARENT_DIR=%PARENT_DIR:\= %
set LAST_WORD=
for %%i in (%PARENT_DIR%) do set LAST_WORD=%%i

if not "%LAST_WORD%"=="backend" (
    echo ОШИБКА: Текущая директория "%LAST_WORD%" не является "backend"
    echo Пожалуйста, запустите этот файл из папки "backend"
    pause
    exit /b 1
)

start "AUTH Service 8001" uvicorn services.service_auth:app --host localhost --port 8001 --reload
start "DATASETS Service 8002" uvicorn services.service_datasets:app --host localhost --port 8002 --reload
start "MODELS Service 8003" uvicorn services.service_models:app --host localhost --port 8003 --reload
start "PROJECTS Service 8004" uvicorn services.service_projects:app --host localhost --port 8004 --reload
