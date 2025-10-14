# Python base (venv and user)
FROM python:3.13 AS base

# Install dependencies and dumb-init
RUN apt-get update && apt-get install -y build-essential curl dumb-init && rm -rf /var/lib/apt/lists/*

RUN useradd -m edapi && \
    mkdir /app/ && \
    chown -R edapi /app/
USER edapi

# Install Poetry
ENV PATH="${PATH}:/home/edapi/.local/bin"
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.in-project true

# Dependencies
WORKDIR /app/
COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry install --no-interaction --no-ansi --no-root --only main


# Prod image (app and default config)
FROM python:3.13-slim as prod

COPY --from=base /usr/bin/dumb-init /usr/bin/
COPY --from=base /app /app

WORKDIR /app/

# User
RUN useradd -m edapi && \
    chown -R edapi /app/
USER edapi

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# App
COPY app /app/app
COPY app /app/migrations
COPY static /app/static

# Default log level
ENV LOG_LEVEL=WARNING

# Expose and run app
EXPOSE 8080
CMD ["dumb-init", "/app/.venv/bin/gunicorn", "edapi.app:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080", "--log-file=-"]
