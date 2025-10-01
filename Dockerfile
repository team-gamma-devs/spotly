FROM python:3.12-slim as builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Install dependencies for building only
RUN apt-get update && apt-get install -y \
    curl build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="$POETRY_HOME/bin:$PATH"
WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root --no-ansi

# Final lightweight image
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    PYTHONPATH=/app

# Install only runtime essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser ./app ./app

USER appuser

EXPOSE 8000

# Optimized gunicorn for Free Tier (only 2 workers!)
CMD gunicorn app.main:app \
    --bind 0.0.0.0:${APP_PORT} \
    --workers ${WORKERS} \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 100 \
    --max-requests 500 \
    --max-requests-jitter 50 \
    --timeout 30 \
    --graceful-timeout 20 \
    --keep-alive 3 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL}
