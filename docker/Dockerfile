FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app_cae
WORKDIR /app_cae

RUN pip3 install --upgrade pip
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
