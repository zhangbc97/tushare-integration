FROM python:3.10.11-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /code/app

ADD . .

RUN pip install -r requirements.txt