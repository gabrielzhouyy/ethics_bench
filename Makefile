# Ethics-Bench Makefile
# Simplifies common development and deployment tasks

.PHONY: help install test run clean deploy docker

# Default target
help:
	@echo "Ethics-Bench Management Commands"
	@echo "================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install     - Install dependencies and setup environment"
	@echo "  make env         - Create .env file from template"
	@echo ""
	@echo "Development Commands:"
	@echo "  make run         - Start green agent locally"
	@echo "  make run-full    - Start both white and green agents"
	@echo "  make test        - Run agent tests"
	@echo "  make clean       - Clean up temporary files"
	@echo ""
	@echo "Deployment Commands:"
	@echo "  make deploy      - Deploy to cloud instance"
	@echo "  make ngrok       - Start with ngrok tunneling"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker      - Build and run in Docker"
	@echo "  make docker-build - Build Docker image only"

# Setup virtual environment and install dependencies
install:
	@echo "📦 Setting up Ethics-Bench environment..."
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "✅ Installation complete!"

# Create environment file
env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "📝 Created .env file from template"; \
		echo "⚠️  Please edit .env with your configuration"; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Start green agent only
run: env
	@echo "🚀 Starting Green Agent..."
	.venv/bin/python green_agent_standalone.py

# Start both agents
run-full: env
	@echo "🚀 Starting both agents..."
	./start_agents.sh

# Run tests
test:
	@echo "🧪 Testing agent functionality..."
	.venv/bin/python test_agent.py

# Quick setup and run
quick: install env run

# Clean up temporary files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/green_agent/__pycache__/
	rm -rf src/white_agent/__pycache__/
	rm -rf .pytest_cache/
	rm -f ngrok_*.log
	rm -f *.tmp
	@echo "✅ Cleanup complete"

# Deploy to cloud
deploy:
	@echo "☁️  Deploying to cloud..."
	./deploy.sh

# Start with ngrok
ngrok:
	@echo "🌐 Starting with ngrok tunneling..."
	./ngrok_setup.sh

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t ethics-bench .

docker: docker-build
	@echo "🐳 Running in Docker..."
	docker run -p 9012:9012 --env-file .env ethics-bench

# Development server with auto-reload
dev: env
	@echo "🔧 Starting development server..."
	.venv/bin/uvicorn green_agent_standalone:app --host 0.0.0.0 --port 9012 --reload

# Check agent status
status:
	@echo "📊 Checking agent status..."
	@curl -s http://localhost:9012/health | python3 -m json.tool 2>/dev/null || echo "Agent not responding"

# Install git hooks for development
hooks:
	@echo "🪝 Installing git hooks..."
	@if [ -d .git ]; then \
		echo "#!/bin/bash\nmake test" > .git/hooks/pre-commit; \
		chmod +x .git/hooks/pre-commit; \
		echo "✅ Pre-commit hook installed"; \
	else \
		echo "❌ Not a git repository"; \
	fi