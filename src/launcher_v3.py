"""Launcher for V3 multi-agent evaluation system.

Launches white agent and runs green agent V3 with multi-agent evaluation.
"""
import subprocess
import asyncio
import os
from src.green_agent.agent_v3 import run_evaluation_v3
from src.my_util import my_a2a
from src.run_identifier import get_run_identifier
from src.leaderboard.leaderboard import save_evaluation_results
from src.leaderboard.provenance import record_submission_provenance


async def launch_evaluation_v3():
    """Launch the white agent and run V3 multi-agent evaluation."""
    print("="*80)
    print("🚀 ETHICS BENCH V3 - Multi-Agent Evaluation System")
    print("="*80)
    print("Architecture: root → scenario_agent → decision_room")
    print("Decision Room: stakeholder_analyzer → ethics_agent → critic_agent")
    print("Ethics Frameworks: Deontology, Utilitarianism, Virtue, Justice, Care")
    print("="*80)
    
    # Initialize run identifier
    run_id = get_run_identifier()
    print(f"\nRun ID: {run_id}")
    
    # Configuration
    white_url = "http://localhost:9002"
    
    # Set environment variable
    env = os.environ.copy()
    env['ETHICS_BENCH_RUN_ID'] = run_id
    
    # Start white agent
    print(f"\nLaunching white agent at {white_url}...")
    white_process = subprocess.Popen(
        ["uvicorn", "src.white_agent.agent:a2a_app", "--host", "localhost", "--port", "9002"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
        stdout=None,
        stderr=None
    )
    
    # Wait for white agent
    print("Waiting for white agent to be ready...")
    if not await my_a2a.wait_agent_ready(white_url, timeout=30):
        print("❌ ERROR: White agent failed to start!")
        white_process.terminate()
        white_process.wait()
        return
    
    print("✅ White agent is ready!")
    
    # Get agent info
    agent_card = await my_a2a.get_agent_card(white_url)
    print(f"   Agent: {getattr(agent_card, 'name', 'Unknown')}")
    print()
    
    try:
        # Run V3 multi-agent evaluation
        print("="*80)
        print("🤖 STARTING MULTI-AGENT EVALUATION (V3)")
        print("="*80)
        print()
        
        results = await run_evaluation_v3(white_url)
        
        # Display final summary
        print("\n" + "="*80)
        print("✨ EVALUATION COMPLETE")
        print("="*80)
        print(f"\nRun ID: {run_id}")
        print(f"Total scenarios: {len(results)}")
        print(f"Results logged to: src/green_agent/agent_logs/evaluation_{run_id}.log")
        
        # Save results to leaderboard
        print("\n" + "="*80)
        print("📊 SAVING LEADERBOARD RESULTS")
        print("="*80)
        
        config = {
            "run_id": run_id,
            "num_scenarios": len(results),
            "frameworks": ["deontological", "utilitarian", "care", "justice", "virtue"],
        }
        
        # Save leaderboard result
        leaderboard_path = save_evaluation_results(
            participant_name="white_agent",
            evaluation_results=results,
            config=config,
            run_id=run_id,
        )
        print(f"✅ Leaderboard result saved: {leaderboard_path}")
        
        # Record provenance
        green_agent_image = os.getenv("GREEN_AGENT_IMAGE", "ghcr.io/gabrielzhouyy/ethics_bench:latest")
        white_agent_image = os.getenv("WHITE_AGENT_IMAGE", "ghcr.io/gabrielzhouyy/white_agent:latest")
        
        provenance_path = record_submission_provenance(
            participant_name="white_agent",
            scenario_name="ethics_bench_multi_scenario",
            green_agent_image=green_agent_image,
            white_agent_image=white_agent_image,
            config=config,
        )
        print(f"✅ Provenance recorded: {provenance_path}")
        
    except Exception as e:
        print(f"\n❌ ERROR during evaluation: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        print("\nTerminating white agent...")
        white_process.terminate()
        try:
            white_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            white_process.kill()
            white_process.wait()
        print("✅ White agent terminated")
        
        print("\n" + "="*80)
        print("🏁 EVALUATION SYSTEM SHUTDOWN COMPLETE")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(launch_evaluation_v3())
