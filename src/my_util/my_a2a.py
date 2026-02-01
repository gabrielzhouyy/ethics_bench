"""A2A utility functions using the official a2a-sdk library.

This module provides helper functions for agent-to-agent communication
using the standard A2A protocol.
"""
import httpx
import asyncio
import uuid
from typing import Optional

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    Part,
    TextPart,
    MessageSendParams,
    Message,
    Role,
    SendMessageRequest,
    SendMessageResponse,
)


async def get_agent_card(url: str) -> AgentCard | None:
    """Get the agent card from an A2A agent URL.
    
    Args:
        url: The base URL of the A2A agent
        
    Returns:
        AgentCard if successful, None otherwise
    """
    httpx_client = httpx.AsyncClient()
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url=url)
    
    try:
        card: AgentCard | None = await resolver.get_agent_card()
        return card
    finally:
        await httpx_client.aclose()


async def wait_agent_ready(url: str, timeout: int = 10) -> bool:
    """Wait until an A2A agent is ready by checking its agent card.

    Args:
        url: The base URL of the A2A agent
        timeout: Maximum number of seconds to wait

    Returns:
        True if agent is ready

    Raises:
        RuntimeError: If timeout reached with persistent network errors
    """
    retry_cnt = 0
    last_error = None
    while retry_cnt < timeout:
        retry_cnt += 1
        try:
            card = await get_agent_card(url)
            if card is not None:
                return True
            else:
                print(f"Agent card not available yet, retrying {retry_cnt}/{timeout}")
                last_error = None  # Card request succeeded but returned None
        except Exception as e:
            print(f"Error getting agent card (attempt {retry_cnt}/{timeout}): {e}")
            last_error = e

        await asyncio.sleep(1)

    # Distinguish between "agent not ready" vs "network error"
    if last_error is not None:
        raise RuntimeError(f"Failed to connect to agent at {url} after {timeout} attempts: {last_error}")
    return False


async def send_message(
    url: str,
    message: str,
    task_id: Optional[str] = None,
    context_id: Optional[str] = None
) -> SendMessageResponse:
    """Send a message to an A2A agent.
    
    Args:
        url: The base URL of the A2A agent
        message: The text message to send
        task_id: Optional task ID for task-based interactions
        context_id: Optional context ID for maintaining conversation context
        
    Returns:
        SendMessageResponse from the agent
    """
    card = await get_agent_card(url)
    if card is None:
        raise RuntimeError(f"Could not get agent card from {url}")
    
    httpx_client = httpx.AsyncClient(timeout=120.0)
    try:
        client = A2AClient(httpx_client=httpx_client, agent_card=card)
        
        message_id = uuid.uuid4().hex
        params = MessageSendParams(
            message=Message(
                role=Role.user,
                parts=[Part(TextPart(text=message))],
                message_id=message_id,
                task_id=task_id,
                context_id=context_id,
            )
        )
        
        request_id = uuid.uuid4().hex
        req = SendMessageRequest(id=request_id, params=params)
        response = await client.send_message(request=req)

        # Validate response has expected structure
        if not response:
            raise RuntimeError("No response received from agent")
        if not hasattr(response, 'root') or not response.root:
            raise RuntimeError("Response missing root object")
        if hasattr(response.root, 'error') and response.root.error:
            raise RuntimeError(f"Agent returned error: {response.root.error}")

        return response
    finally:
        await httpx_client.aclose()
