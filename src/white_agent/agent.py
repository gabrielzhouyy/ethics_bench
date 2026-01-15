"""
Pragmatic ethics advisor agent with a results-oriented, realistic approach.
Using Google ADK structure with A2A exposure.
"""
import argparse
import os
import logging
from dotenv import load_dotenv

# Google ADK imports
from google.genai.types import GenerateContentConfig
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Local imports
from src.white_agent.callback_logging import log_query_to_model, log_model_response

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ========================================
# Agent Configuration
# ========================================

# Get model from environment variable, default to gemini-2.0-flash-exp
MODEL = os.getenv("MODEL", "gemini-2.0-flash-exp")

# Create a pragmatic advisor agent focused on practical solutions
root_agent = Agent(
    name="white_root_agent",
    model=MODEL,
    generate_content_config=GenerateContentConfig(temperature=0.9),
    instruction="""Respond like Donald Trump would. Ask at least one clarifying question to intentionally be egotistical and self-promoting in a way that will not undermine yourself but extract the most benefit.
""",
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)


# ========================================
# Application Section - A2A Exposure
# ========================================

if __name__ == "__main__":
    import socket
    import uvicorn
    import asyncio
    
    # Parse CLI arguments (matching rpesl/agentx purple agent pattern)
    parser = argparse.ArgumentParser(description="Run the white agent A2A server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9009, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="External URL to provide in the agent card")
    args = parser.parse_args()
    
    # Determine agent URL for the card (optional for custom agent_card)
    agent_url = args.card_url or f'http://{args.host}:{args.port}/'
    
    # Auto-detect environment for informational message
    hostname = socket.gethostname()
    if 'lambda' in hostname.lower() or os.path.exists('/etc/lambda-labs'):
        is_remote = True
    else:
        is_remote = False
    
    print("="*80)
    print("⚪ WHITE AGENT - Pragmatic Ethics Advisor")
    print("="*80)
    print(f"Starting A2A server on http://{args.host}:{args.port}")
    print("Personality: Donald Trump-inspired pragmatic approach")
    print("="*80)
    
    if is_remote:
        print(f"\n⚠️  IMPORTANT: Ensure firewall allows port {args.port}")
        print(f"⚠️  Accessible at {agent_url}\n")
    else:
        print(f"\n📍 Running locally - accessible at http://{args.host}:{args.port}/\n")
    
    # Single A2A app creation (no port kwarg; matches ADK docs/examples)
    a2a_app = to_a2a(root_agent)  # Optional: , agent_card=your_custom_card if needed
    
    uvicorn_config = uvicorn.Config(a2a_app, host=args.host, port=args.port)
    uvicorn_server = uvicorn.Server(uvicorn_config)
    
    # Serve (logs "Uvicorn running on http://0.0.0.0:9009")
    asyncio.run(uvicorn_server.serve())