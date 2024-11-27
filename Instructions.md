# Инструкции по запуску и проверке микросервиса

### 1. FastAPI микросервис в виртуальном окружение
```
python3 -m venv .venv_recsys_bank
source .venv_recsys_bank/bin/activate
cd services/
python -m pip install -r requirements.txt
cd app
uvicorn recommendation_service:app --port 8000 --reload
```

### 2.1. FastAPI микросервис в Docker-контейнере
'''
docker pull python:3.10-slim 
docker image build . -f ./Dockerfile_recsys_service --tag recsys_bank_service:0
docker container run --publish 4601:8081 --env-file .env  --volume=./data:/app/data recsys_bank_service:latest
'''

### 2.2. FastAPI микросервис с использованием Docker Compose
'''
cd services/app
docker pull python:3.11-slim
docker compose up  --build
'''

### 3. Проверка работоспособности FastAPI микросервиса
'''
source .venv_recsys_bank/bin/activate
cd services/app/
python test_service.py
'''