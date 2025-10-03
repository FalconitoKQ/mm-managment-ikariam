# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLASK_APP=run.py \
    PORT=5000

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip wheel && pip install -r /app/requirements.txt

COPY . /app
RUN mkdir -p /app/db
ENV SQLALCHEMY_DATABASE_URI="sqlite:////app/db/db_usersv.db"

EXPOSE 5000
CMD python /app/run.py

