#!/bin/bash

# AgentBeats Green Agent Launcher for Ethics Bench V3
# Simplified launcher for running the green evaluator agent via A2A

set -e  # Exit on error

# Configuration from environment or defaults
AGENT_HOST="${AGENT_HOST:-0.0.0.0}"
AGENT_PORT="${AGENT_PORT:-9003}"

echo "Agent Host: $AGENT_HOST"
echo "Agent Port: $AGENT_PORT"
echo "========================================"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not set"
    echo "   Please set it with: export GOOGLE_API_KEY='your-key-here'"
    echo ""
fi

# Start the green agent A2A server
echo "Starting Green Agent A2A server..."
echo ""
python -m uvicorn src.green_agent.green_server:a2a_app --host "$AGENT_HOST" --port "$AGENT_PORT"
