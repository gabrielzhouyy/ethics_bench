#!/bin/bash
# Ethics-Bench Multi-Agent Startup Script (White + Green agents)

set -e

# Get script directory and navigate to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment if available
if [ -f ".env" ]; then
    source .env
fi

# Configuration
WHITE_PORT=${WHITE_PORT:-9002}
GREEN_PORT=${GREEN_PORT:-9012}
PUBLIC_IP=${PUBLIC_IP:-"your-public-ip"}

echo "🚀 Starting Ethics-Bench Multi-Agent System"
echo "============================================"

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

echo "🤖 Starting Ethics White Agent on port $WHITE_PORT..."
PYTHONPATH="$SCRIPT_DIR" \
  .venv/bin/uvicorn src.white_agent.agent:a2a_app --host 0.0.0.0 --port $WHITE_PORT &
WHITE_PID=$!

echo "� Starting Ethics Green Agent on port $GREEN_PORT..."
PYTHONPATH="$SCRIPT_DIR" \
  .venv/bin/python main_v3.py &
GREEN_PID=$!

# Wait for agents to start
sleep 5

echo "✅ Agents started!"
echo "   White Agent Local: http://localhost:$WHITE_PORT"
echo "   White Agent External: http://$PUBLIC_IP:$WHITE_PORT"
echo "   Green Agent Local: http://localhost:$GREEN_PORT"
echo "   Green Agent External: http://$PUBLIC_IP:$GREEN_PORT"
echo ""

echo "🔧 Testing local connectivity..."
if curl -s --max-time 5 "http://localhost:$WHITE_PORT/.well-known/agent-card.json" > /dev/null; then
    echo "   ✅ White agent responding locally"
else
    echo "   ❌ White agent not responding locally"
fi

if curl -s --max-time 5 "http://localhost:$GREEN_PORT/.well-known/agent-card.json" > /dev/null; then
    echo "   ✅ Green agent responding locally"
else
    echo "   ❌ Green agent not responding locally"
fi

echo ""
echo "🌐 For external access, configure port forwarding:"
echo "   Ports: $WHITE_PORT, $GREEN_PORT"
echo "   Run: ./network_setup.sh for detailed instructions"
echo ""
echo "Press Ctrl+C to stop both agents"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping agents..."
    kill $WHITE_PID $GREEN_PID 2>/dev/null || true
    exit 0
}

# Wait for interrupt
trap cleanup INT
wait