"""
Pragmatic ethics advisor agent with a results-oriented, realistic approach.
Using Google ADK structure with A2A exposure.
"""

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

# Expose the agent via A2A protocol using official Google ADK pattern
# This creates a FastAPI app that serves the agent at port 9002
# Agent card will be available at: http://localhost:9002/.well-known/agent-card.json
a2a_app = to_a2a(root_agent, port=9002)

# To run this agent:
# uvicorn src.white_agent.agent:a2a_app --host localhost --port 9002
