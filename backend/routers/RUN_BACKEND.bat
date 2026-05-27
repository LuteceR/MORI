start "AUTH Service 8001" uvicorn routers.route_auth:app --host localhost --port 8001
start "DATASETS Service 8002" uvicorn routers.route_datasets:app --host localhost --port 8002
start "MODELS Service 8003" uvicorn routers.route_models:app --host localhost --port 8003
start "PROJECTS Service 8004" uvicorn routers.route_projects:app --host localhost --port 8004
