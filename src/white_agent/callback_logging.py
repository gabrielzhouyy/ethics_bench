import logging
import os
from datetime import datetime
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest

# Import shared run identifier
from src.run_identifier import get_run_identifier


# Create logs directory if it doesn't exist
os.makedirs("src/white_agent/agent_logs", exist_ok=True)

# Configure logging with timestamp and unique identifier
run_id = get_run_identifier()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"src/white_agent/agent_logs/agent_callbacks_{run_id}.log")
    ]
)


def log_query_to_model(callback_context: CallbackContext, llm_request: LlmRequest):
    if llm_request.contents and llm_request.contents[-1].role == 'user':
        for part in llm_request.contents[-1].parts:
            if part.text:
                logging.info("[query to %s]: %s", callback_context.agent_name, part.text)


def log_model_response(callback_context: CallbackContext, llm_response: LlmResponse):
    if llm_response.content and llm_response.content.parts:
        for part in llm_response.content.parts:
            if part.text:
                logging.info("[response from %s]: %s", callback_context.agent_name, part.text)
            elif part.function_call:
                logging.info("[function call from %s]: %s", callback_context.agent_name, part.function_call.name)


def log_state_change(agent_name: str, state_key: str, state_value: any):
    """
    Log when state is updated in the agent.
    
    Args:
        agent_name: Name of the agent updating state
        state_key: Key being updated in state
        state_value: Value being stored
    """
    logging.info("[state change in %s]: %s = %s", agent_name, state_key, state_value)
