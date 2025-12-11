# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Avoid interactive prompts and ensure Unicode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

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

# Create logs directory to avoid permission issues
RUN mkdir -p src/green_agent/agent_logs

# Expose white agent port (internal visibility; optional)
EXPOSE 9002

# Default command: run the evaluation launcher
CMD ["python", "main_v3.py"]
