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

# Create directories for results and logs
RUN mkdir -p src/green_agent/agent_logs results submissions

# Expose green agent port
EXPOSE 9003

# Run green agent server
CMD ["python", "-m", "src.green_agent.green_server", "--host", "0.0.0.0", "--port", "9003"]
