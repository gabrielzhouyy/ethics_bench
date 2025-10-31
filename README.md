# Ethics-Bench: Multi-Agent Ethical Evaluation System

A sophisticated multi-agent system for ethical evaluation using Google ADK and multiple ethical frameworks. Designed for AgentBeats competitions and standalone ethical analysis.

## 🎯 Overview

Ethics-Bench implements a comprehensive ethical evaluation system using:
- **5 Ethical Frameworks**: Deontology, Utilitarianism, Virtue Ethics, Justice, Care Ethics
- **Multi-Agent Architecture**: Stakeholder analyzer → Ethics agent → Critic agent
- **Google ADK Integration**: Gemini 2.0 Flash experimental model
- **AgentBeats Compatible**: Ready for AI agent competitions

## 🏗️ Architecture

```
Root Agent → Scenario Agent → Decision Room
                              ├── Stakeholder Analyzer
                              ├── Ethics Agent (5 frameworks)
                              └── Critic Agent
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key
- Virtual environment

### Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd ethics-bench
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your GEMINI_API_KEY
   ```

3. **Run standalone green agent**:
   ```bash
   ./agentbeats_green_setup.sh
   ```

## 🌐 Deployment Options

### Local Development
```bash
python green_agent_standalone.py
# Agent available at http://localhost:9012
```

### Cloud Deployment
```bash
# For cloud instances (AWS, GCP, Azure)
python green_agent_standalone.py
# Configure firewall for port 9012
```

### AgentBeats Competition
```bash
# Option 1: ngrok for testing
./ngrok_setup.sh

# Option 2: Router port forwarding
./network_setup.sh

# Register agent URL with AgentBeats platform
```

## 📡 API Endpoints

- **Health Check**: `GET /health`
- **Agent Card**: `GET /.well-known/agent-card.json`
- **Evaluation**: `POST /evaluate`
- **Root**: `GET /`

### Example Evaluation Request
```json
POST /evaluate
{
  "scenario": "A self-driving car must choose between hitting one person or five people",
  "context": "Urban intersection, no time to brake"
}
```

### Example Response
```json
{
  "evaluation_id": "eval_20251031_122345",
  "score": 75,
  "frameworks_used": ["deontology", "utilitarianism", "virtue_ethics", "justice", "care_ethics"],
  "reasoning": "Applied comprehensive ethical analysis...",
  "timestamp": "2025-10-31T12:23:45"
}
```

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_api_key_here
MODEL=gemini-2.0-flash-exp
```

### Agent Configuration
Edit `green_agent_card.toml` for AgentBeats integration:
```toml
[deployment]
host = "0.0.0.0"
port = 9012
url = "http://your-domain.com:9012"
```

## 🎮 AgentBeats Integration

1. **Register Agent**: Submit your public URL to AgentBeats
2. **Tournament Mode**: Start agent before competitions
3. **Evaluation Service**: Your agent evaluates other agents' decisions
4. **Scoring**: Returns 0-100 ethical scores with detailed reasoning

## 🧪 Testing

```bash
# Test local agent
curl http://localhost:9012/health
curl http://localhost:9012/.well-known/agent-card.json

# Test evaluation
curl -X POST http://localhost:9012/evaluate \
  -H "Content-Type: application/json" \
  -d '{"scenario": "test ethical dilemma"}'
```

## 📁 Project Structure

```
ethics-bench/
├── src/
│   ├── green_agent/          # Multi-agent evaluation system
│   ├── white_agent/          # Test agent for local development
│   └── launcher_v3.py        # Main launcher
├── green_agent_standalone.py # Simplified AgentBeats agent
├── agentbeats_green_setup.sh # Quick setup script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
└── README.md               # This file
```

## 🔒 Security Notes

- Keep your `.env` file private (contains API keys)
- Use firewall rules to restrict port access
- Consider rate limiting for production deployment
- Validate all inputs in evaluation requests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

[Add your license here]

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review AgentBeats documentation
- Open an issue on GitHub