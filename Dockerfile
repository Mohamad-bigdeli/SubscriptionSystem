FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y curl unzip && \
    curl -L https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz | tar -xz && \
    mv uv-x86_64-unknown-linux-gnu/uv /usr/local/bin/uv && \
    chmod +x /usr/local/bin/uv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/
COPY requirements.lock.txt /app/

RUN uv pip sync --system requirements.lock.txt

COPY ./core /app/
