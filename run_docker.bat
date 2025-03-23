@echo off
echo Stopped all containers...
docker-compose down

set WORKER_NUMBER=1

echo Starting services with %WORKER_NUMBER% worker Celery...
docker-compose up --scale celery=%WORKER_NUMBER% --build -d

echo All containers are running!
docker ps