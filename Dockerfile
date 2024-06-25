FROM python:3.11.9-slim-bullseye

ARG PIP_SOURCE=https://pypi.org/simple

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /code/app

ADD requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir --index-url $PIP_SOURCE

ADD . .

CMD ["python", "main.py"]