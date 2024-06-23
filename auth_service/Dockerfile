FROM python:3.12.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /auth_service

RUN pip install --upgrade pip

COPY ../requirements.txt /auth_service/
RUN pip install -r /auth_service/requirements.txt

COPY . /auth_service/