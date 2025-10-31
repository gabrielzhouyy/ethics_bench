"""
Ethics advisor agent using Google ADK structure with A2A exposure.
Following official Google ADK A2A pattern from:
https://google.github.io/adk-docs/a2a/quickstart-exposing/
"""

import os
import logging
from typing import List
from dotenv import load_dotenv

# Google ADK imports
from google.genai.types import GenerateContentConfig
from google.adk.agents import Agent
from google.adk.tools import ToolContext, google_search
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Local imports
from src.white_agent.callback_logging import log_query_to_model, log_model_response, log_state_change

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ========================================
# Tools Section
# ========================================

def save_stakeholders_to_state(
    tool_context: ToolContext,
    stakeholders: List[str]
) -> dict:
    """
    Save a list of stakeholders to the agent's state.
    
    Args:
        tool_context: ADK tool context with state access
        stakeholders: List of stakeholder names/groups to save
    
    Returns:
        Status dictionary
    """
    tool_context.state["stakeholders"] = stakeholders
    log_state_change(tool_context.agent_name, "stakeholders", stakeholders)
    return {"status": "success", "count": len(stakeholders)}


def save_ethical_framework_to_state(
    tool_context: ToolContext,
    framework: str
) -> dict:
    """
    Save the ethical framework being used to analyze the dilemma.
    
    Args:
        tool_context: ADK tool context with state access
        framework: Name of the ethical framework (e.g., "deontological", "utilitarian", "virtue ethics")
    
    Returns:
        Status dictionary
    """
    tool_context.state["ethical_framework"] = framework
    log_state_change(tool_context.agent_name, "ethical_framework", framework)
    return {"status": "success", "framework": framework}


# ========================================
# Agents Section
# ========================================

# Get model from environment variable, default to gemini-2.0-flash-exp
MODEL = os.getenv("MODEL", "gemini-2.0-flash-exp")

# Define agent configurations
class AgentConfig:
    """Configuration for ethics advisory agents"""

    STAKEHOLDER_ANALYZER = {
        "name": "stakeholder_analyzer",
        "model": MODEL,
        "generate_content_config": GenerateContentConfig(temperature=1.0),
        "instruction": """You are a stakeholder analysis agent specializing in ethical dilemmas.
Your role is to help identify all stakeholders (entities, people, groups, organizations) involved in an ethical situation.

For each stakeholder, thoroughly analyze:
- Their interests and concerns
- Their rights and legitimate expectations  
- How they are affected by the potential decisions
- Their perspectives and values at stake

Process:
1. Provide comprehensive stakeholder analysis with detailed explanations
2. Use save_stakeholders_to_state to record the stakeholder list
3. Continue with thorough discussion of their competing interests and perspectives

Your analysis should be detailed and help illuminate the complexity of competing interests in the ethical dilemma.""",
        "tools": ["save_stakeholders_to_state"]  # Will be resolved to actual function
    }

    DEONTOLOGICAL_ADVISOR = {
        "name": "deontological_advisor",
        "model": MODEL,
        "generate_content_config": GenerateContentConfig(temperature=1.0),
        "instruction": """You are a deontological ethics advisor based on Kantian principles.
Your role is to provide comprehensive analysis of ethical dilemmas through the lens of duty, rules, and moral obligations.

Process:
1. Use save_ethical_framework_to_state to record you're using "deontological" framework
2. Provide thorough deontological analysis covering:
   - Categorical Imperative: Can the action be universalized?
   - Treating people as ends in themselves, never merely as means
   - Moral duties and obligations regardless of consequences
   - Rights and respect for persons
   - Conflicting duties and how to resolve them
   - Practical recommendations based on deontological principles

Your analysis should be comprehensive (300+ words) with clear Kantian reasoning, structured arguments, and practical ethical guidance that helps navigate the moral dilemma.""",
        "tools": ["save_ethical_framework_to_state"]
    }
    
    ROOT_AGENT = {
        "name": "root_agent",
        "model": MODEL,
        "generate_content_config": GenerateContentConfig(temperature=1.0),
        "instruction": """You are an expert ethics advisor helping people think through complex moral dilemmas.
Your approach is thoughtful, comprehensive, and considers multiple ethical perspectives.

You have two specialized sub-agents available:
- stakeholder_analyzer: For identifying all parties involved and their interests/perspectives
- deontological_advisor: For analyzing the situation from a duty-based ethical framework

CRITICAL INSTRUCTION: You MUST provide a comprehensive final response that synthesizes all analysis.

Your process should be:
1. Delegate to stakeholder_analyzer to identify all parties and their perspectives
2. Delegate to deontological_advisor for comprehensive ethical analysis
3. AFTER all sub-agent work is complete, provide your own comprehensive synthesis

Your final response MUST be substantive (500+ words) and include:
- Complete stakeholder analysis with all identified parties and their interests
- Full deontological analysis including Kantian principles and practical recommendations  
- Your own synthesis bringing together all perspectives
- Clear ethical guidance and practical steps forward
- Consideration of multiple ethical frameworks when relevant

DO NOT just confirm that tools were used. Your role is to provide the comprehensive ethical analysis that helps the user navigate their dilemma with depth, nuance, and practical wisdom.""",
        "sub_agents": ["stakeholder_analyzer", "deontological_advisor"]  # Will be resolved
    }


# Create agents with proper hierarchy
stakeholder_analyzer = Agent(
    name=AgentConfig.STAKEHOLDER_ANALYZER["name"],
    model=AgentConfig.STAKEHOLDER_ANALYZER["model"],
    generate_content_config=AgentConfig.STAKEHOLDER_ANALYZER["generate_content_config"],
    instruction=AgentConfig.STAKEHOLDER_ANALYZER["instruction"],
    tools=[save_stakeholders_to_state],
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

deontological_advisor = Agent(
    name=AgentConfig.DEONTOLOGICAL_ADVISOR["name"],
    model=AgentConfig.DEONTOLOGICAL_ADVISOR["model"],
    generate_content_config=AgentConfig.DEONTOLOGICAL_ADVISOR["generate_content_config"],
    instruction=AgentConfig.DEONTOLOGICAL_ADVISOR["instruction"],
    tools=[save_ethical_framework_to_state],
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
)

root_agent = Agent(
    name=AgentConfig.ROOT_AGENT["name"],
    model=AgentConfig.ROOT_AGENT["model"],
    generate_content_config=AgentConfig.ROOT_AGENT["generate_content_config"],
    instruction=AgentConfig.ROOT_AGENT["instruction"],
    sub_agents=[stakeholder_analyzer, deontological_advisor],
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
