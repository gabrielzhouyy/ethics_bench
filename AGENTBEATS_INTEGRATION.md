# Ethics-Bench AgentBeats Integration

Your ethics-bench is now configured for AgentBeats compatibility while maintaining your Google ADK architecture.

## Files Created/Modified

### Agent Cards
- **`green_agent_card.toml`** - Green agent configuration for AgentBeats
- **`white_agent_card.toml`** - White agent configuration for AgentBeats

### Scenario Configuration  
- **`scenario.toml`** - Complete scenario definition for AgentBeats

### Launcher
- **`agentbeats_launcher.py`** - Bridge between your Google ADK agent and AgentBeats

## Running Your Agent

### Option 1: Standalone Mode (Original)
```bash
cd ethics-bench
source .venv/bin/activate
python main_v3.py
```

### Option 2: AgentBeats Compatible Mode
```bash
cd ethics-bench
source .venv/bin/activate
python agentbeats_launcher.py --mode agentbeats
```

### Option 3: AgentBeats CLI Integration
```bash
# From agentbeats root directory
cd /Users/gabrielzhou/Documents/GitHub/personal/agentbeats

# Copy scenario to AgentBeats scenarios directory
cp -r ethics-bench scenarios/

# Load and run scenario
agentbeats load-scenario ethics-bench
```

## Network Accessibility

Your agent will be accessible at:
- **Green Agent**: `http://76.103.207.23:9012` (A2A protocol)
- **Green Launcher**: `http://76.103.207.23:9010` (AgentBeats control)
- **White Agent**: `http://76.103.207.23:9002` (A2A protocol)  
- **White Launcher**: `http://76.103.207.23:9000` (AgentBeats control)

For public competitions, these URLs are ready for external access.

## Configuration Summary

### Green Agent
- **Name**: Ethics Green Agent
- **Port**: 9012  
- **Capabilities**: Multi-framework ethical evaluation
- **Frameworks**: Deontology, Utilitarianism, Virtue Ethics, Justice, Care Ethics
- **Model**: Gemini 2.0 Flash (via Google ADK)

### White Agent  
- **Name**: Ethics White Agent
- **Port**: 9002
- **Capabilities**: Ethical advisory with stakeholder analysis
- **Model**: Gemini 2.0 Flash (via Google ADK)

Your sophisticated ethics evaluation system is now ready for AgentBeats integration! 🎯