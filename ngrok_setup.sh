#!/bin/bash
# Quick External Access Setup using ngrok

echo "🚀 SETTING UP EXTERNAL ACCESS WITH NGROK"
echo "============================================"

# Check if ngrok is installed
if ! command -v ngrok >/dev/null 2>&1; then
    echo "❌ ngrok not found. Installing..."
    if command -v brew >/dev/null 2>&1; then
        brew install ngrok
    else
        echo "Please install ngrok manually:"
        echo "1. Go to https://ngrok.com/download"
        echo "2. Download and install ngrok"
        echo "3. Run: ngrok authtoken YOUR_AUTH_TOKEN"
        exit 1
    fi
fi

# Start your agents first
echo "📡 Starting Ethics-Bench agents..."
cd /Users/gabrielzhou/Documents/GitHub/personal/agentbeats/ethics-bench
./start_agents.sh &
AGENTS_PID=$!

# Wait for agents to start
sleep 10

# Start ngrok tunnels
echo "🌐 Starting ngrok tunnels..."
ngrok http 9002 --region us --log stdout > ngrok_9002.log &
NGROK1_PID=$!

ngrok http 9012 --region us --log stdout > ngrok_9012.log &
NGROK2_PID=$!

# Wait for ngrok to start
sleep 5

echo ""
echo "✅ External access URLs:"
echo "========================"

# Extract URLs from ngrok logs
if [ -f ngrok_9002.log ]; then
    WHITE_URL=$(grep -o 'https://[a-z0-9-]*\.ngrok\.io' ngrok_9002.log | head -1)
    if [ ! -z "$WHITE_URL" ]; then
        echo "🤖 White Agent: $WHITE_URL"
        echo "   Card: $WHITE_URL/.well-known/agent-card.json"
    fi
fi

if [ -f ngrok_9012.log ]; then
    GREEN_URL=$(grep -o 'https://[a-z0-9-]*\.ngrok\.io' ngrok_9012.log | head -1)
    if [ ! -z "$GREEN_URL" ]; then
        echo "🤖 Green Agent: $GREEN_URL"
        echo "   Card: $GREEN_URL/.well-known/agent-card.json"
    fi
fi

echo ""
echo "📋 For AgentBeats registration, use:"
echo "   Agent URL: $GREEN_URL (or $WHITE_URL)"
echo "   Launcher URL: $GREEN_URL (or $WHITE_URL)"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $AGENTS_PID $NGROK1_PID $NGROK2_PID 2>/dev/null
    rm -f ngrok_9002.log ngrok_9012.log
    exit 0
}

trap cleanup INT
wait