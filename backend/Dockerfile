# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies to a local folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: Final Runtime ---
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed python packages and the app code
COPY --from=builder /root/.local /root/.local
COPY . .

# Ensure the local bin is in the PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime-only system dependencies (e.g., libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m appuser

# Security: Run as a non-root user
USER appuser

# Expose the port FastAPI/Gunicorn will run on
EXPOSE 8000

# Production-grade server (Uvicorn with workers or Gunicorn)
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]