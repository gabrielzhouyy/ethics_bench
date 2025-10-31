#!/usr/bin/env python3
"""
AgentBeats-compatible launcher for Ethics Green Agent
Integrates your Google ADK agent with AgentBeats infrastructure
"""

import os
import sys
import asyncio
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

# Import your existing agent
from src.green_agent.agent_v3 import run_evaluation_v3

# AgentBeats imports (if available)
try:
    from agentbeats import BeatsAgent
    AGENTBEATS_AVAILABLE = True
except ImportError:
    print("AgentBeats not available, running in standalone mode")
    AGENTBEATS_AVAILABLE = False

class EthicsGreenAgentLauncher:
    """Launcher that bridges your Google ADK agent with AgentBeats"""
    
    def __init__(self, 
                 launcher_host="0.0.0.0", 
                 launcher_port=9010,
                 agent_host="0.0.0.0", 
                 agent_port=9012):
        self.launcher_host = launcher_host
        self.launcher_port = launcher_port
        self.agent_host = agent_host
        self.agent_port = agent_port
        
    async def start_agent_server(self):
        """Start your existing Google ADK agent server"""
        print(f"🚀 Starting Ethics Green Agent on {self.agent_host}:{self.agent_port}")
        
        # Import and run your existing agent
        from src.white_agent.agent import a2a_app
        
        # Start uvicorn server
        config = uvicorn.Config(
            app=a2a_app,
            host=self.agent_host,
            port=self.agent_port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def start_launcher_server(self):
        """Start launcher server for AgentBeats communication"""
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        launcher_app = FastAPI(title="Ethics Green Agent Launcher")
        
        @launcher_app.get("/health")
        async def health():
            return {"status": "healthy", "agent": "ethics-green-agent"}
        
        @launcher_app.post("/reset")
        async def reset():
            """AgentBeats reset endpoint"""
            return {"status": "reset", "message": "Agent ready for new evaluation"}
        
        @launcher_app.get("/status")
        async def status():
            return {
                "status": "running",
                "agent_url": f"http://76.103.207.23:{self.agent_port}",
                "launcher_url": f"http://76.103.207.23:{self.launcher_port}",
                "public_agent_url": f"http://76.103.207.23:{self.agent_port}",
                "public_launcher_url": f"http://76.103.207.23:{self.launcher_port}"
            }
        
        print(f"🎛️  Starting Launcher on {self.launcher_host}:{self.launcher_port}")
        
        config = uvicorn.Config(
            app=launcher_app,
            host=self.launcher_host,
            port=self.launcher_port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run_standalone(self):
        """Run your original standalone evaluation"""
        print("🔬 Running standalone ethics evaluation...")
        asyncio.run(run_evaluation_v3())
    
    async def run_agentbeats_mode(self):
        """Run in AgentBeats-compatible mode"""
        print("🤝 Running in AgentBeats mode...")
        
        # Start both launcher and agent servers concurrently
        await asyncio.gather(
            self.start_launcher_server(),
            self.start_agent_server()
        )

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ethics Green Agent Launcher")
    parser.add_argument("--mode", choices=["standalone", "agentbeats"], 
                       default="standalone", help="Running mode")
    parser.add_argument("--launcher-host", default="0.0.0.0", help="Launcher host")
    parser.add_argument("--launcher-port", type=int, default=9010, help="Launcher port")
    parser.add_argument("--agent-host", default="0.0.0.0", help="Agent host")
    parser.add_argument("--agent-port", type=int, default=9012, help="Agent port")
    
    args = parser.parse_args()
    
    launcher = EthicsGreenAgentLauncher(
        launcher_host=args.launcher_host,
        launcher_port=args.launcher_port,
        agent_host=args.agent_host,
        agent_port=args.agent_port
    )
    
    # Check environment
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment")
        print("   Make sure your .env file contains: GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    
    try:
        if args.mode == "standalone":
            launcher.run_standalone()
        else:
            asyncio.run(launcher.run_agentbeats_mode())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()