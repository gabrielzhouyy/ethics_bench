#!/bin/bash
# AgentBeats Green Agent Quick Setup Script

set -e

echo "🤖 AGENTBEATS GREEN AGENT SETUP"
echo "================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables if .env exists
if [ -f ".env" ]; then
    source .env
fi

# Configuration
AGENT_PORT=${AGENT_PORT:-9012}
AGENT_HOST=${AGENT_HOST:-"0.0.0.0"}
PUBLIC_URL=${PUBLIC_URL:-"http://localhost:$AGENT_PORT"}

echo "1. ✅ Starting Green Agent..."

# Kill any existing processes on the port
lsof -ti:$AGENT_PORT | xargs kill -9 2>/dev/null || true
sleep 1

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run setup first:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Start the green agent
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    PYTHON_CMD=".venv/Scripts/python.exe"
else
    echo "❌ Python not found in virtual environment"
    exit 1
fi

$PYTHON_CMD green_agent_standalone.py &
GREEN_PID=$!

# Wait for startup
sleep 3

echo "2. 🔧 Testing Local Access..."
if curl -s --max-time 5 "http://localhost:$AGENT_PORT/.well-known/agent-card.json" > /dev/null; then
    echo "   ✅ Green agent responding locally"
    echo "   📍 Local URL: http://localhost:$AGENT_PORT"
    echo "   🃏 Agent Card: http://localhost:$AGENT_PORT/.well-known/agent-card.json"
    echo "   📖 API Docs: http://localhost:$AGENT_PORT/docs"
else
    echo "   ❌ Green agent not responding"
    kill $GREEN_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "3. 🌐 For AgentBeats Registration:"
echo "   Agent URL: $PUBLIC_URL"
echo "   Launcher URL: $PUBLIC_URL"
echo ""
echo "4. 📡 External Access Options:"
echo "   a) Router port forwarding: ./network_setup.sh"
echo "   b) ngrok tunneling: ./ngrok_setup.sh"
echo "   c) Cloud deployment: ./deploy.sh"
echo ""
echo "5. 🏁 Registration:"
echo "   https://agentbeats.com/register"
echo ""
echo "Agent running with PID $GREEN_PID"
echo "Press Ctrl+C to stop"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping agent..."
    kill $GREEN_PID 2>/dev/null || true
    exit 0
}

# Wait for interrupt
trap cleanup INT
wait $GREEN_PID