#!/bin/bash
# Cloud Deployment Script for Ethics-Bench Green Agent

set -e  # Exit on any error

echo "🚀 ETHICS-BENCH CLOUD DEPLOYMENT"
echo "================================="

# Configuration
PYTHON_VERSION="3.10"
VENV_NAME=".venv"
SERVICE_PORT=9012

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  This script should not be run as root"
   exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv git curl
elif command -v yum >/dev/null 2>&1; then
    sudo yum update -y
    sudo yum install -y python3 python3-pip git curl
elif command -v brew >/dev/null 2>&1; then
    brew update
    brew install python3 git curl
else
    echo "❌ Unsupported package manager. Please install Python 3.10+, git, and curl manually."
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if ! python3 -c "import sys; assert sys.version_info >= (3, 10)"; then
    echo "❌ Python 3.10+ required"
    exit 1
fi

# Create virtual environment
echo "🔧 Setting up virtual environment..."
if [ -d "$VENV_NAME" ]; then
    echo "Virtual environment already exists, removing..."
    rm -rf "$VENV_NAME"
fi

python3 -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "❗ IMPORTANT: Edit .env file with your configuration:"
    echo "   - Set GEMINI_API_KEY to your Google API key"
    echo "   - Update PUBLIC_URL to your cloud instance URL"
    echo ""
    echo "Example commands:"
    echo "   nano .env"
    echo "   export GEMINI_API_KEY='your-key-here'"
    echo "   export PUBLIC_URL='http://$(curl -s ifconfig.me):9012'"
    echo ""
    read -p "Press Enter after configuring .env file..."
fi

# Test the agent
echo "🧪 Testing agent startup..."
timeout 10s python green_agent_standalone.py || true

# Configure firewall (if ufw is available)
if command -v ufw >/dev/null 2>&1; then
    echo "🔥 Configuring firewall..."
    sudo ufw allow $SERVICE_PORT/tcp
    echo "Firewall rule added for port $SERVICE_PORT"
fi

# Create systemd service (optional)
read -p "🔧 Create systemd service for auto-start? (y/N): " create_service
if [[ $create_service =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/ethics-bench.service"
    WORK_DIR=$(pwd)
    USER=$(whoami)
    
    sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Ethics-Bench Green Agent
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment=PATH=$WORK_DIR/$VENV_NAME/bin
ExecStart=$WORK_DIR/$VENV_NAME/bin/python $WORK_DIR/green_agent_standalone.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable ethics-bench
    
    echo "✅ Systemd service created. Commands:"
    echo "   Start:  sudo systemctl start ethics-bench"
    echo "   Stop:   sudo systemctl stop ethics-bench"
    echo "   Status: sudo systemctl status ethics-bench"
    echo "   Logs:   sudo journalctl -u ethics-bench -f"
fi

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "🚀 To start the agent:"
echo "   source $VENV_NAME/bin/activate"
echo "   python green_agent_standalone.py"
echo ""
echo "🌐 Agent will be available at:"
echo "   http://$(curl -s ifconfig.me 2>/dev/null || echo 'your-server-ip'):$SERVICE_PORT"
echo ""
echo "🔧 Configuration:"
echo "   Edit .env for API keys and settings"
echo "   Check firewall allows port $SERVICE_PORT"
echo ""
echo "📚 Documentation:"
echo "   API docs: http://your-server:$SERVICE_PORT/docs"
echo "   Agent card: http://your-server:$SERVICE_PORT/.well-known/agent-card.json"