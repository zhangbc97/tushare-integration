FROM python:3.10.11-slim-bullseye

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install --no-cache-dir --upgrade pip

WORKDIR /code/app

ADD . .

RUN pip install -r requirements.txt