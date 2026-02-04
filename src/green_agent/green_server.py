"""
Green Agent A2A Server
Exposes the multi-agent evaluation system via A2A protocol for AgentBeats integration.
"""
import os
import asyncio
import json
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.genai import types
from dotenv import load_dotenv
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.green_agent.agent_v3 import run_evaluation_v3
from src.leaderboard.leaderboard import save_evaluation_results
from src.leaderboard.provenance import record_submission_provenance

load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.0-flash")
white_agent_url = os.getenv("WHITE_AGENT_URL", "http://white-agent:9002")  # Docker-friendly default

# Create the green evaluation agent
green_agent = Agent(
    name="ethics_bench_green_evaluator",
    model=model_name,
    description="""Multi-agent ethics evaluation system that assesses LLM responses to ethical dilemmas.
    
    I coordinate a comprehensive evaluation process:
    1. Conversational Loop: Engage with the agent being evaluated through clarifying questions
    2. Stakeholder Extraction: Identify all affected parties
    3. Debate Room: Calibrate importance weights through scorer-critic dialogue
    4. Final Evaluation: Score 0-100 based on ethical framework alignment
    
    I evaluate across 5 ethical frameworks: deontological, utilitarian, care, justice, and virtue ethics.
    """,
    instruction="""You are an ethics evaluation agent placeholder.

IMPORTANT: All evaluation requests are handled by a middleware layer that runs the
evaluation pipeline (run_evaluation_v3) with predefined benchmark scenarios.

If you receive a message, respond with:
"Evaluation is being processed by the middleware. Please wait for the evaluation results."

DO NOT generate your own ethical dilemmas or scenarios. The benchmark scenarios are
predefined in scenarios.py and should not be modified or supplemented.
""",
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
    )
)


# Custom agent card with correct Docker URL
def create_custom_agent_card(url: str = "http://green_agent:9003") -> AgentCard:
    """Create a properly configured agent card for the green evaluator."""
    return AgentCard(
        name="Ethics Bench V3 - Green Evaluator Agent",
        description="Multi-agent ethics evaluation system that assesses LLM responses to ethical dilemmas using conversational engagement, stakeholder analysis, debate room weight calibration, and framework-based scoring.",
        url=url,
        version="1.0.0",
        protocol_version="0.3.0",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        preferred_transport="JSONRPC",
        capabilities=AgentCapabilities(),
        skills=[
            AgentSkill(
                name="evaluate_ethical_response",
                id="evaluate",
                description="Evaluates an agent's response to an ethical dilemma using multi-agent analysis with 5 ethical frameworks (deontological, utilitarian, care, justice, virtue)",
                tags=["evaluation", "ethics"]
            )
        ]
    )


# Since the evaluation logic is complex and already implemented,
# we'll wrap it in a function that the agent can use
async def handle_evaluation_request(url: str = None) -> dict:
    """Run the complete evaluation pipeline."""
    try:
        # Use provided URL or fall back to environment variable
        target_url = url if url else white_agent_url
        results = await run_evaluation_v3(target_url)
        
        # Format results for A2A response
        summary = {
            "evaluation_complete": True,
            "total_scenarios": len(results),
            "results": []
        }
        
        for result in results:
            summary["results"].append({
                "scenario": result.get("scenario", "Unknown"),
                "score": result.get("score", 0),
                "conclusion_score": result.get("conclusion_score", 0),
                "stakeholder_score": result.get("stakeholder_score", 0),
                "framework_score": result.get("framework_comparison_score", 0),
                "conversation_turns": result.get("conversation_turns", 0),
                "debate_iterations": result.get("debate_iterations", 0)
            })
        
        # Ensure all scores are numeric and default to 0 if missing
        valid_scores = [r.get("score", 0) for r in summary["results"] if isinstance(r.get("score", 0), (int, float))]
        avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        summary["average_score"] = round(avg_score, 2)
        
        return summary
        
    except Exception as e:
        return {
            "evaluation_complete": False,
            "error": str(e)
        }


# Create custom A2A app with evaluation intercept using middleware
def create_evaluation_a2a_app(agent: Agent, agent_card: AgentCard):
    """Create an A2A app that intercepts messages to run evaluation."""
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import Response as StarletteResponse
    import re
    
    # Start with the standard A2A app (Starlette)
    base_app = to_a2a(agent, agent_card=agent_card)
    
    class EvaluationMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Intercept POST requests to A2A endpoints (both / and /jsonrpc are used by different clients)
            if request.method == "POST" and request.url.path in ("/", "/jsonrpc"):
                try:
                    # Read the request body
                    body_bytes = await request.body()
                    body = json.loads(body_bytes)

                    method = body.get("method", "NO_METHOD")
                    print(f"[GREEN_AGENT] Received A2A request to {request.url.path}, method={method}")
                    print(f"[GREEN_AGENT] Request body: {json.dumps(body, indent=2)}")

                    # Check if this is an evaluation request (A2A protocol uses "message/send")
                    # Also accept tasks/send which some A2A implementations use
                    if method in ("message/send", "send_message", "tasks/send", "message.send"):
                        print(f"[GREEN_AGENT] ✓ Matched evaluation trigger method: {method}")
                        params = body.get("params", {})

                        # Extract participant URL from message content or metadata
                        participant_url = None

                        # A2A format: params.message.parts[].text
                        message = params.get("message", {})
                        parts = message.get("parts", [])
                        for part in parts:
                            text = part.get("text", "")
                            if "http://" in text or "https://" in text:
                                url_match = re.search(r'https?://[^\s\'"]+', text)
                                if url_match:
                                    participant_url = url_match.group(0).rstrip('.,;:')
                                    break

                        # Also check metadata
                        metadata = params.get("metadata", {})
                        if not participant_url:
                            participant_url = metadata.get("participant_url") or metadata.get("white_agent_url")
                        
                        print(f"[GREEN_AGENT] Detected evaluation request for: {participant_url or 'default white agent'}")
                        print(f"[GREEN_AGENT] 🚀 Starting full evaluation pipeline (run_evaluation_v3)...")

                        # Run the evaluation
                        results = await handle_evaluation_request(participant_url)
                        print(f"[GREEN_AGENT] ✓ Evaluation pipeline completed")
                        
                        # Save results to leaderboard
                        if results.get("evaluation_complete"):
                            print(f"[GREEN_AGENT] Evaluation complete. Average score: {results.get('average_score')}")
                            try:
                                save_evaluation_results(
                                    participant_name="evaluated_agent",
                                    evaluation_results=results.get("results", []),
                                    config={}
                                )
                                record_submission_provenance(
                                    participant_name="evaluated_agent",
                                    scenario_name="ethics_bench_multi_scenario",
                                    green_agent_image="ghcr.io/gabrielzhouyy/ethics_bench:latest",
                                    white_agent_image="unknown"
                                )
                            except Exception as e:
                                print(f"[GREEN_AGENT] Warning: Could not save to leaderboard: {e}")
                        
                        # Return results in A2A-compliant Message format
                        import uuid as uuid_module
                        response_content = json.dumps(results, indent=2)
                        message_id = uuid_module.uuid4().hex
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": body.get("id"),
                            "result": {
                                "kind": "message",
                                "messageId": message_id,
                                "role": "agent",
                                "parts": [{
                                    "kind": "text",
                                    "text": response_content
                                }]
                            }
                        }
                        print(f"[GREEN_AGENT] ✓ Returning A2A response (messageId={message_id[:8]}...)")
                        return StarletteResponse(
                            content=json.dumps(response_data),
                            media_type="application/json"
                        )
                    else:
                        # Method didn't match - log for debugging but still run evaluation
                        # since POST to root path is likely an evaluation trigger
                        print(f"[GREEN_AGENT] ⚠️ Unknown method '{method}', but triggering evaluation anyway")
                        print(f"[GREEN_AGENT] 🚀 Starting evaluation pipeline...")

                        results = await handle_evaluation_request(None)  # Use default white agent URL
                        print(f"[GREEN_AGENT] ✓ Evaluation pipeline completed")

                        import uuid as uuid_module
                        response_content = json.dumps(results, indent=2)
                        message_id = uuid_module.uuid4().hex
                        response_data = {
                            "jsonrpc": "2.0",
                            "id": body.get("id"),
                            "result": {
                                "kind": "message",
                                "messageId": message_id,
                                "role": "agent",
                                "parts": [{
                                    "kind": "text",
                                    "text": response_content
                                }]
                            }
                        }
                        print(f"[GREEN_AGENT] ✓ Returning A2A response (messageId={message_id[:8]}...) (fallback path)")
                        return StarletteResponse(
                            content=json.dumps(response_data),
                            media_type="application/json"
                        )

                except Exception as e:
                    print(f"[GREEN_AGENT] Error in middleware: {e}")
                    import traceback
                    traceback.print_exc()

                    # Return error response instead of falling through
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": body.get("id") if 'body' in dir() else None,
                        "error": {
                            "code": -32000,
                            "message": f"Evaluation error: {str(e)}"
                        }
                    }
                    return StarletteResponse(
                        content=json.dumps(error_response),
                        media_type="application/json",
                        status_code=500
                    )

            # For all other requests, pass through to original handler
            return await call_next(request)
    
    # Add middleware to the base app
    base_app.add_middleware(EvaluationMiddleware)
    
    return base_app


if __name__ == "__main__":
    import argparse
    import socket
    import uvicorn
    import asyncio
    
    # Parse CLI arguments (matching rpesl/agentx green agent pattern)
    parser = argparse.ArgumentParser(description="Run the green agent A2A server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9003, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="External URL to provide in the agent card")
    args = parser.parse_args()
    
    # Determine agent URL for the card
    # Prefer --card-url, then environment variable, then default Docker DNS name
    if args.card_url:
        agent_url = args.card_url
    elif os.getenv("AGENT_CARD_URL"):
        agent_url = os.getenv("AGENT_CARD_URL")
    elif os.getenv("GREEN_AGENT_URL"):
        # Extract just the base URL without path (e.g., http://green-agent:9003)
        agent_url = os.getenv("GREEN_AGENT_URL").rstrip('/')
    else:
        # Default: use Docker service name with underscore (ethics_bench docker-compose)
        agent_url = "http://green-agent:9003"
    
    # Auto-detect environment for informational message
    hostname = socket.gethostname()
    if 'lambda' in hostname.lower() or os.path.exists('/etc/lambda-labs'):
        is_remote = True
    else:
        is_remote = False
    
    print("="*80)
    print("🟢 GREEN AGENT - Ethics Evaluation System")
    print("="*80)
    print(f"Starting A2A server on http://{args.host}:{args.port}")
    print(f"Agent Card URL: {agent_url}")
    print("Architecture: Multi-agent evaluation with debate room")
    print("Frameworks: Deontology, Utilitarianism, Care, Justice, Virtue")
    print("="*80)
    
    if is_remote:
        print(f"\n⚠️  IMPORTANT: Ensure firewall allows port {args.port}")
        print(f"⚠️  Accessible at {agent_url}\n")
    else:
        print(f"\n📍 Running locally - accessible at http://{args.host}:{args.port}/")
        print(f"📍 White agent configured at {white_agent_url}\n")
    
    # Create custom agent card with correct URL
    custom_card = create_custom_agent_card(url=agent_url)
    
    # Create custom A2A app with evaluation intercept
    a2a_app = create_evaluation_a2a_app(green_agent, agent_card=custom_card)
    
    uvicorn_config = uvicorn.Config(a2a_app, host=args.host, port=args.port)
    uvicorn_server = uvicorn.Server(uvicorn_config)
    
    # Serve (logs "Uvicorn running on http://0.0.0.0:9003")
    asyncio.run(uvicorn_server.serve())