FROM python:3.12.0

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /courses_service

RUN pip install --upgrade pip

COPY requirements.txt /courses_service/
RUN pip install -r /courses_service/requirements.txt

COPY . /courses_service/