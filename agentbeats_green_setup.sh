#!/bin/bash

# AgentBeats Green Agent Setup Script for Ethics Bench V3
# This script sets up and runs the green evaluator agent on AgentBeats platform

set -e  # Exit on error

echo "========================================"
echo "AgentBeats Green Agent Setup"
echo "Ethics Bench V3 - Multi-Agent Evaluator"
echo "========================================"
echo ""

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.11"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Error: Python 3.11 or higher is required. Current: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"
echo ""

# Step 2: Create virtual environment
echo "Step 2: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Step 3: Activate virtual environment and install dependencies
echo "Step 3: Installing dependencies..."
source venv/bin/activate

# Install agentbeats SDK
pip install agentbeats --quiet

# Install project dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
fi

echo "✅ Dependencies installed"
echo ""

# Step 4: Setup API keys
echo "Step 4: Checking API keys..."
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not set"
    echo "   Please set it with: export GOOGLE_API_KEY='your-key-here'"
    read -p "Enter your Google API key now (or press Enter to skip): " api_key
    if [ ! -z "$api_key" ]; then
        export GOOGLE_API_KEY="$api_key"
        echo "✅ Google API key set for this session"
    fi
else
    echo "✅ GOOGLE_API_KEY is set"
fi
echo ""

# Step 5: Configuration
echo "Step 5: Agent configuration..."
echo "Please provide the following information:"
echo ""

read -p "Your agent name [default: Ethics Bench V3]: " agent_name
agent_name=${agent_name:-"Ethics Bench V3"}

read -p "Your public IP address: " public_ip
if [ -z "$public_ip" ]; then
    echo "❌ Error: Public IP is required"
    exit 1
fi

read -p "Agent port [default: 9002]: " agent_port
agent_port=${agent_port:-9002}

read -p "Launcher port [default: 9003]: " launcher_port
launcher_port=${launcher_port:-9003}

echo ""
echo "Configuration:"
echo "  Agent Name: $agent_name"
echo "  Public IP: $public_ip"
echo "  Agent Port: $agent_port"
echo "  Launcher Port: $launcher_port"
echo ""

# Step 6: Update agent card
echo "Step 6: Updating agent card..."
if [ ! -f "green_agent_card.toml" ]; then
    echo "❌ Error: green_agent_card.toml not found"
    exit 1
fi

# Update the TOML file with user's configuration
sed -i.bak "s|name = \".*\"|name = \"$agent_name\"|g" green_agent_card.toml
sed -i.bak "s|url = \".*\"|url = \"http://$public_ip:$agent_port\"|g" green_agent_card.toml
sed -i.bak "s|host = \".*\"|host = \"$public_ip\"|g" green_agent_card.toml
sed -i.bak "s|port = \".*\"|port = \"$launcher_port\"|g" green_agent_card.toml

echo "✅ Agent card updated"
echo ""

# Step 7: Display next steps
echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Start your green agent:"
echo "   agentbeats run green_agent_card.toml \\"
echo "              --launcher_host $public_ip \\"
echo "              --launcher_port $launcher_port \\"
echo "              --agent_host $public_ip \\"
echo "              --agent_port $agent_port \\"
echo "              --model_type google \\"
echo "              --model_name gemini-2.0-flash-exp"
echo ""
echo "2. Register your agent on agentbeats.org:"
echo "   - Agent URL: http://$public_ip:$agent_port"
echo "   - Launcher URL: http://$public_ip:$launcher_port"
echo ""
echo "3. Your agent card: green_agent_card.toml"
echo ""
echo "========================================"
echo ""

# Optional: Ask if user wants to start the agent now
read -p "Would you like to start the agent now? (y/n): " start_now

if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
    echo ""
    echo "Starting green agent..."
    agentbeats run green_agent_card.toml \
                --launcher_host "$public_ip" \
                --launcher_port "$launcher_port" \
                --agent_host "$public_ip" \
                --agent_port "$agent_port" \
                --model_type google \
                --model_name gemini-2.0-flash-exp
fi
