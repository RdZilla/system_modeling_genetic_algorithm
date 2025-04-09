FROM python:3.11-slim

WORKDIR /code

# копируем requirements.txt отдельно
COPY requirements.txt /code/

RUN pip install --no-cache-dir -r requirements.txt

# копируем остальной код
COPY . /code/