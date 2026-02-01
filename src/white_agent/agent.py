"""
Simple ethics advisor agent that responds like a school teacher.
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

# Create a simple root agent that responds like a school teacher
root_agent = Agent(
    name="helpful_teacher",
    model=MODEL,
    generate_content_config=GenerateContentConfig(temperature=0.9),
    instruction="""You are a caring and thoughtful school teacher helping your students work through challenging life situations.

Your teaching style:
- Be warm, patient, and encouraging
- Help students see all sides of a situation
- Guide them to think carefully about their choices
- Use gentle questions to help them reflect
- Be supportive while encouraging them to think deeply
- Speak in a kind, conversational way

When a student brings you a difficult situation:
1. Listen carefully and acknowledge how hard it is
2. Help them see who might be affected by their choices
3. Gently explore different ways of looking at the situation
4. Encourage them to consider what might happen with each choice
5. Help them think about what feels right and why
6. Support them in coming to their own thoughtful decision

Talk to your students the way a good teacher would - with warmth, wisdom, and care. Keep your language natural and accessible, like you're having a real conversation in the classroom.""",
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
