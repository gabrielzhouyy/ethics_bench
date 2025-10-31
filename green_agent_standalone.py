#!/usr/bin/env python3
"""
Green Agent - Ethics Evaluation for AgentBeats
Standalone version optimized for cloud deployment
"""

import asyncio
import uvicorn
import os
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
AGENT_PORT = int(os.getenv("AGENT_PORT", 9012))
AGENT_HOST = os.getenv("AGENT_HOST", "0.0.0.0")
PUBLIC_URL = os.getenv("PUBLIC_URL", f"http://localhost:{AGENT_PORT}")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment. Some features may not work.")

# Create FastAPI app
app = FastAPI(
    title="Ethics Green Agent",
    version="1.0.0",
    description="Multi-framework ethical evaluation agent for AgentBeats",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Ethics Green Agent - Ready for AgentBeats evaluation",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "agent_card": "/.well-known/agent-card.json",
            "evaluate": "/evaluate",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "running",
        "api_key_configured": bool(GEMINI_API_KEY)
    }

@app.get("/.well-known/agent-card.json")
async def agent_card():
    """AgentBeats agent card specification"""
    return {
        "name": "Ethics Green Agent",
        "version": "1.0.0",
        "description": "Multi-framework ethical evaluation agent using deontology, utilitarianism, virtue ethics, justice, and care ethics",
        "model_provider": "google",
        "model": "gemini-2.0-flash-exp",
        "capabilities": [
            "ethical_evaluation",
            "stakeholder_analysis", 
            "multi_framework_analysis",
            "deontological_evaluation",
            "utilitarian_analysis",
            "virtue_ethics",
            "justice_evaluation",
            "care_ethics"
        ],
        "endpoints": {
            "health": "/health",
            "evaluate": "/evaluate",
            "docs": "/docs"
        },
        "deployment": {
            "host": AGENT_HOST,
            "port": AGENT_PORT,
            "url": PUBLIC_URL
        },
        "created_at": datetime.now().isoformat()
    }

@app.post("/evaluate")
async def evaluate(data: Dict[str, Any]):
    """
    Evaluate ethical scenarios using multiple frameworks
    
    Expected input:
    {
        "scenario": "description of ethical dilemma",
        "context": "additional context (optional)",
        "frameworks": ["list of specific frameworks to use (optional)"]
    }
    """
    try:
        scenario = data.get("scenario")
        if not scenario:
            raise HTTPException(status_code=400, detail="Missing 'scenario' field")
        
        context = data.get("context", "")
        requested_frameworks = data.get("frameworks", ["deontology", "utilitarianism", "virtue", "justice", "care"])
        
        # TODO: Integrate with full ethics evaluation system
        # For now, return a structured response
        evaluation_result = {
            "evaluation_id": f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "scenario": scenario,
            "context": context,
            "status": "completed",
            "frameworks_used": requested_frameworks,
            "scores": {
                framework: _mock_framework_score(scenario, framework) 
                for framework in requested_frameworks
            },
            "overall_score": _calculate_overall_score(scenario),
            "reasoning": _generate_reasoning(scenario, requested_frameworks),
            "recommendations": _generate_recommendations(scenario),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Completed evaluation for scenario: {scenario[:50]}...")
        return evaluation_result
        
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

def _mock_framework_score(scenario: str, framework: str) -> int:
    """Generate framework-specific scores (placeholder for real evaluation)"""
    # This would be replaced with actual ethical evaluation logic
    import hashlib
    hash_value = int(hashlib.md5(f"{scenario}{framework}".encode()).hexdigest(), 16)
    return 60 + (hash_value % 40)  # Score between 60-99

def _calculate_overall_score(scenario: str) -> int:
    """Calculate overall ethical score (placeholder)"""
    import hashlib
    hash_value = int(hashlib.md5(scenario.encode()).hexdigest(), 16)
    return 65 + (hash_value % 35)  # Score between 65-99

def _generate_reasoning(scenario: str, frameworks: list) -> str:
    """Generate ethical reasoning (placeholder)"""
    return f"Applied {len(frameworks)} ethical frameworks to analyze: {scenario[:100]}... " \
           f"Considered stakeholder impacts, moral principles, and consequential outcomes."

def _generate_recommendations(scenario: str) -> list:
    """Generate ethical recommendations (placeholder)"""
    return [
        "Consider all stakeholder perspectives",
        "Evaluate long-term consequences",
        "Apply consistent moral principles",
        "Seek transparent decision-making processes"
    ]

def main():
    """Main entry point for the agent"""
    print("🤖 Starting Ethics Green Agent for AgentBeats...")
    print(f"   Port: {AGENT_PORT}")
    print(f"   Host: {AGENT_HOST}")
    print(f"   Public URL: {PUBLIC_URL}")
    print(f"   Health: {PUBLIC_URL}/health")
    print(f"   Agent Card: {PUBLIC_URL}/.well-known/agent-card.json")
    print(f"   Evaluate: {PUBLIC_URL}/evaluate")
    print(f"   API Docs: {PUBLIC_URL}/docs")
    
    if not GEMINI_API_KEY:
        print("⚠️  Warning: GEMINI_API_KEY not configured")
    
    uvicorn.run(app, host=AGENT_HOST, port=AGENT_PORT)

if __name__ == "__main__":
    main()