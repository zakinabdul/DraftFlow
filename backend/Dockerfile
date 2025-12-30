# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim
WORKDIR /app

# 1. Copy dependencies
COPY --from=builder /install /usr/local

# 2. Copy EVERYTHING from the backend folder
# This copies the 'app/' folder into '/app/app/'
COPY . .

# 3. Environment & Security
# We set PYTHONPATH to /app so 'import app' works
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# 4. The Command
# We use 'app.main:app' because:
# app (folder) -> main (file) -> app (FastAPI instance)
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]