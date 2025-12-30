# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim
WORKDIR /app

# 1. Copy dependencies
COPY --from=builder /install /usr/local

# 2. Copy the contents of the 'backend' directory
# This results in: /app/app/main.py
COPY . .

# 3. Environment & Security setup
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* && \
    useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# 4. THE FIX: The path is now 'app.main:app'
# 'app' (folder) -> 'main' (file) -> 'app' (FastAPI variable)
ENV PYTHONPATH=/app
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]