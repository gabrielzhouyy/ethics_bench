#!/bin/bash
# Deployment script for Lambda Labs or local deployment
# Works on: Lambda Labs (129.159.45.125) or localhost

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect environment
if [[ $(hostname) == *"lambda"* ]] || [[ -f /etc/lambda-labs ]]; then
    DEPLOY_ENV="lambda"
    PUBLIC_IP="129.159.45.125"
else
    DEPLOY_ENV="local"
    PUBLIC_IP="localhost"
fi

echo "=========================================="
echo "Ethics Bench Deployment"
echo "Environment: $DEPLOY_ENV"
echo "IP: $PUBLIC_IP"
echo "=========================================="

# Check if ports are available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $1 is already in use"
        lsof -ti:$1 | xargs kill -9 2>/dev/null
        echo "✅ Cleared port $1"
    else
        echo "✅ Port $1 is available"
    fi
}

echo ""
echo "Checking ports..."
check_port 9002
check_port 9003

echo ""
echo "=========================================="
echo "Starting White Agent (Port 9002)"
echo "=========================================="
cd "$SCRIPT_DIR"
source .venv/bin/activate

# Start white agent with uvicorn in background
uvicorn src.white_agent.agent:a2a_app --host 0.0.0.0 --port 9002 > /dev/null 2>&1 &
WHITE_PID=$!
echo "White Agent PID: $WHITE_PID"

# Wait for white agent to start
echo "Waiting for white agent to initialize..."
sleep 5

# Check if white agent is running
if curl -s http://localhost:9002/.well-known/agent-card.json > /dev/null; then
    echo "✅ White agent is running"
else
    echo "❌ White agent failed to start"
    exit 1
fi

echo ""
echo "=========================================="
echo "Starting Green Agent (Port 9003)"
echo "=========================================="

# Start green agent with uvicorn in background
uvicorn src.green_agent.green_server:a2a_app --host 0.0.0.0 --port 9003 > /dev/null 2>&1 &
GREEN_PID=$!
echo "Green Agent PID: $GREEN_PID"

# Wait for green agent to start
echo "Waiting for green agent to initialize..."
sleep 5

# Check if green agent is running
if curl -s http://localhost:9003/.well-known/agent-card.json > /dev/null; then
    echo "✅ Green agent is running"
else
    echo "❌ Green agent failed to start"
    kill $WHITE_PID
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "=========================================="
echo "White Agent: http://$PUBLIC_IP:9002"
echo "Green Agent: http://$PUBLIC_IP:9003"
echo ""
echo "Agent Card URLs:"
echo "  White: http://$PUBLIC_IP:9002/.well-known/agent-card.json"
echo "  Green: http://$PUBLIC_IP:9003/.well-known/agent-card.json"
echo ""
echo "PIDs:"
echo "  White Agent: $WHITE_PID"
echo "  Green Agent: $GREEN_PID"
echo ""
echo "To stop agents:"
echo "  kill $WHITE_PID $GREEN_PID"
echo "=========================================="
if [[ "$DEPLOY_ENV" == "lambda" ]]; then
    echo ""
    echo "⚠️  FIREWALL REQUIREMENTS:"
    echo "  Ensure Lambda Labs firewall allows:"
    echo "  - Port 9002 (White Agent)"
    echo "  - Port 9003 (Green Agent)"
    echo "=========================================="
fi
