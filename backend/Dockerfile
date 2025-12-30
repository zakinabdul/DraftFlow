# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Fix: Assuming requirements.txt is inside the backend folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim

WORKDIR /app

# 1. Copy dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
COPY backend/ . 

# 2. Setup Environment
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Tell Python to look in the appuser's local folder for packages
ENV PYTHONPATH=/home/appuser/.local/lib/python3.11/site-packages

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m appuser

# 3. Permissions fix: Ensure appuser owns their home directory and app files
RUN chown -R appuser:appuser /home/appuser /app

USER appuser

EXPOSE 8000

# 4. Use dynamic Port for Render and ensure main:app is found
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]