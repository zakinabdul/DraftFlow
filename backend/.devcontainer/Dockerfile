# .devcontainer/Dockerfile
FROM python:3.11-slim

# Recommended Python env settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System tools needed for dev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Set working directory (matches your workspace root)
WORKDIR /workspace

# Install Python deps early (requires build context to be the repository root)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Keep the container running indefinitely (devcontainer pattern)
CMD ["sleep", "infinity"]
