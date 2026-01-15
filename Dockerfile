# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Avoid interactive prompts and ensure Unicode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONPATH=/app

WORKDIR /app

# Install system deps for building wheels if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first for better caching
COPY requirements.txt ./

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create logs directories to avoid permission issues
RUN mkdir -p src/green_agent/agent_logs src/white_agent/agent_logs

# Expose port 9009 (used by both agents internally)
EXPOSE 9009

# Default command can be overridden by docker-compose
CMD ["python", "main_v3.py"]
