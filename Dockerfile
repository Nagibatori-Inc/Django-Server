FROM python:3.9.15-slim-buster AS builder

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    git \
    bash \
    curl \
    build-essential \
    libpq-dev

RUN git config --global user.email "you@example.com" &&  \
    git config --global user.name "Your Name"

RUN pip install -U pip && \
    curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry config virtualenvs.create false && \
    poetry lock  && \
    poetry install --no-ansi --no-root --no-cache

COPY . /app