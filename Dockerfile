FROM python:3.11.9-slim-bullseye

RUN pip install --no-cache-dir --upgrade pip

WORKDIR /code/app

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD . .

CMD ["python", "main.py"]