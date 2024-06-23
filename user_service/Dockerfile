FROM python:3.12.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /user_service

RUN pip install --upgrade pip

COPY ../requirements.txt /user_service/
RUN pip install -r /user_service/requirements.txt

COPY . /user_service/