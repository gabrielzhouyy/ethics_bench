#!/bin/bash
# Pre-commit preparation script
# Cleans up repository before pushing to GitHub

set -e

echo "🔧 PREPARING ETHICS-BENCH FOR GITHUB"
echo "===================================="

# Remove sensitive files
echo "🔒 Removing sensitive files..."
if [ -f ".env" ]; then
    echo "   Keeping .env for local development (already in .gitignore)"
fi

# Remove any log files
find . -name "*.log" -delete 2>/dev/null || true
find . -name "ngrok_*.log" -delete 2>/dev/null || true

# Remove cache files
echo "🧹 Cleaning cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove temporary files
rm -f *.tmp *.temp 2>/dev/null || true

# Check for required files
echo "✅ Checking required files..."
required_files=(
    "README.md"
    "requirements.txt"
    ".env.example"
    ".gitignore"
    "green_agent_standalone.py"
    "deploy.sh"
    "Makefile"
    "Dockerfile"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ❌ Missing: $file"
    fi
done

# Test syntax of Python files
echo "🐍 Checking Python syntax..."
python3 -m py_compile green_agent_standalone.py
python3 -m py_compile test_agent.py
echo "   ✓ Python syntax OK"

# Test shell scripts
echo "🐚 Checking shell scripts..."
for script in *.sh; do
    if [ -f "$script" ]; then
        bash -n "$script"
        echo "   ✓ $script"
    fi
done

# Create a deployment checklist
echo "📋 Creating deployment checklist..."
cat > DEPLOYMENT_CHECKLIST.md << 'EOF'
# Deployment Checklist

## Pre-deployment
- [ ] Configure `.env` with GEMINI_API_KEY
- [ ] Test locally with `make test`
- [ ] Review firewall/security settings

## Cloud Deployment
- [ ] Clone repository: `git clone <repo-url>`
- [ ] Run setup: `./deploy.sh`
- [ ] Configure public IP in `.env`
- [ ] Test external access

## AgentBeats Registration
- [ ] Start agent: `make run`
- [ ] Verify agent card: `curl http://your-ip:9012/.well-known/agent-card.json`
- [ ] Register at AgentBeats platform
- [ ] Test evaluation endpoint

## Monitoring
- [ ] Check logs: `sudo journalctl -u ethics-bench -f`
- [ ] Monitor performance
- [ ] Verify uptime during competitions
EOF

echo ""
echo "🎯 REPOSITORY READY FOR GITHUB!"
echo "==============================="
echo ""
echo "📦 Files prepared:"
echo "   - README.md (comprehensive documentation)"
echo "   - .env.example (configuration template)"
echo "   - .gitignore (proper exclusions)"
echo "   - deploy.sh (cloud deployment script)"
echo "   - Makefile (easy management commands)"
echo "   - Dockerfile (containerized deployment)"
echo "   - test_agent.py (functionality testing)"
echo ""
echo "🚀 Next steps:"
echo "   1. git add ."
echo "   2. git commit -m 'Clean ethics-bench for production deployment'"
echo "   3. git push origin main"
echo ""
echo "☁️  Cloud deployment:"
echo "   1. git clone <your-repo-url>"
echo "   2. cd ethics-bench"
echo "   3. ./deploy.sh"
echo ""
echo "🎮 AgentBeats usage:"
echo "   1. make install"
echo "   2. make env  # Edit .env with your API key"
echo "   3. make run"
echo "   4. Register at AgentBeats platform"