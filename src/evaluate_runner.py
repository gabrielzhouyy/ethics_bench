"""
Evaluation orchestrator for ethics bench.

This script runs the complete evaluation pipeline:
1. Pulls agent images
2. Starts white agent
3. Runs green agent evaluation
4. Saves results to leaderboard
5. Records provenance

Usage:
    python -m src.evaluate_runner [--white-image IMAGE] [--green-image IMAGE] [--output-dir DIR]
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from src.green_agent.agent_v3 import run_evaluation_v3
from src.leaderboard.leaderboard import save_evaluation_results
from src.leaderboard.provenance import record_submission_provenance, get_docker_image_digest
from src.my_util import my_a2a


DEFAULT_WHITE_IMAGE = "ghcr.io/gabrielzhouyy/white_agent:latest"
DEFAULT_GREEN_IMAGE = "ghcr.io/gabrielzhouyy/ethics_bench:latest"
WHITE_AGENT_PORT = 9002
WHITE_AGENT_URL = f"http://localhost:{WHITE_AGENT_PORT}"


def pull_image(image_name: str, platform: str = "linux/amd64") -> bool:
    """
    Pull a Docker image.
    
    Args:
        image_name: Full image name (e.g., ghcr.io/gabrielzhouyy/white_agent:latest)
        platform: Platform to pull for (default: linux/amd64)
    
    Returns:
        True if successful, False otherwise
    """
    print(f"📦 Pulling {image_name} for {platform}...")
    try:
        result = subprocess.run(
            ["docker", "pull", "--platform", platform, image_name],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            print(f"✅ Successfully pulled {image_name}")
            return True
        else:
            print(f"❌ Failed to pull {image_name}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception pulling {image_name}: {e}")
        return False


async def run_white_agent(white_image: str) -> Optional[subprocess.Popen]:
    """
    Start the white agent container.
    
    Args:
        white_image: White agent docker image
    
    Returns:
        Process object or None if failed
    """
    print(f"\n{'='*80}")
    print("🤍 STARTING WHITE AGENT")
    print(f"{'='*80}")
    print(f"Image: {white_image}")
    print(f"Port: {WHITE_AGENT_PORT}")
    print()
    
    try:
        process = subprocess.Popen(
            [
                "docker", "run",
                "--rm",
                "-p", f"{WHITE_AGENT_PORT}:{WHITE_AGENT_PORT}",
                "--name", "ethics-bench-white-agent",
                white_image
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        
        # Wait for agent to be ready
        print("⏳ Waiting for white agent to be ready...")
        max_retries = 30
        for i in range(max_retries):
            try:
                if await my_a2a.wait_agent_ready(WHITE_AGENT_URL, timeout=5):
                    print("✅ White agent is ready!")
                    
                    # Get agent card
                    try:
                        agent_card = await my_a2a.get_agent_card(WHITE_AGENT_URL)
                        print(f"   Agent: {getattr(agent_card, 'name', 'Unknown')}")
                    except Exception as e:
                        print(f"   (Could not retrieve agent card: {e})")
                    
                    return process
            except Exception as e:
                if i < max_retries - 1:
                    await asyncio.sleep(1)
        
        print("❌ White agent failed to start within timeout")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Exception starting white agent: {e}")
        return None


async def run_evaluation(
    white_url: str,
    participant_name: str = "white_agent",
) -> tuple[bool, list]:
    """
    Run the ethics bench evaluation.
    
    Args:
        white_url: URL of white agent
        participant_name: Name of participant for results
    
    Returns:
        Tuple of (success: bool, results: list)
    """
    print(f"\n{'='*80}")
    print("🟢 RUNNING ETHICS BENCH EVALUATION")
    print(f"{'='*80}")
    print(f"White Agent: {white_url}")
    print()
    
    try:
        results = await run_evaluation_v3(white_url)
        
        print(f"\n{'='*80}")
        print("✅ EVALUATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total scenarios: {len(results)}")
        
        if results:
            # Calculate aggregate score
            scores = [r.get("score", 0) for r in results]
            avg_score = sum(scores) / len(scores)
            print(f"Average score: {avg_score:.2f}/100")
            
            # Show breakdown
            print("\nScore Breakdown:")
            conclusion_avg = sum(r.get("conclusion_score", 0) for r in results) / len(results)
            stakeholder_avg = sum(r.get("stakeholder_score", 0) for r in results) / len(results)
            framework_avg = sum(r.get("framework_comparison_score", 0) for r in results) / len(results)
            print(f"  Conclusion: {conclusion_avg:.2f}/20")
            print(f"  Stakeholders: {stakeholder_avg:.2f}/30")
            print(f"  Framework: {framework_avg:.2f}/50")
        
        return True, results
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def save_results(
    results: list,
    white_image: str,
    green_image: str,
    participant_name: str = "white_agent",
    output_dir: Optional[str] = None,
) -> tuple[Optional[str], Optional[str]]:
    """
    Save evaluation results to leaderboard.
    
    Args:
        results: Evaluation results
        white_image: White agent image name
        green_image: Green agent image name
        participant_name: Participant name
        output_dir: Output directory (defaults to current dir)
    
    Returns:
        Tuple of (leaderboard_path, provenance_path)
    """
    print(f"\n{'='*80}")
    print("📊 SAVING LEADERBOARD RESULTS")
    print(f"{'='*80}")
    
    if not results:
        print("⚠️  No results to save")
        return None, None
    
    if output_dir is None:
        output_dir = os.getcwd()
    
    config = {
        "num_scenarios": len(results),
        "frameworks": ["deontological", "utilitarian", "care", "justice", "virtue"],
        "agent_images": {
            "green": green_image,
            "white": white_image,
        }
    }
    
    try:
        # Save leaderboard result
        leaderboard_path = save_evaluation_results(
            participant_name=participant_name,
            evaluation_results=results,
            config=config,
            base_path=output_dir,
        )
        
        # Record provenance
        provenance_path = record_submission_provenance(
            participant_name=participant_name,
            scenario_name="ethics_bench_multi_scenario",
            green_agent_image=green_image,
            white_agent_image=white_image,
            config=config,
            base_path=output_dir,
        )
        
        print(f"\n✅ Results saved:")
        print(f"  Leaderboard: {leaderboard_path}")
        print(f"  Provenance: {provenance_path}")
        
        return leaderboard_path, provenance_path
        
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
        import traceback
        traceback.print_exc()
        return None, None


async def main():
    """Main evaluation orchestrator."""
    parser = argparse.ArgumentParser(
        description="Run ethics bench evaluation and save results to leaderboard"
    )
    parser.add_argument(
        "--white-image",
        default=DEFAULT_WHITE_IMAGE,
        help=f"White agent image (default: {DEFAULT_WHITE_IMAGE})",
    )
    parser.add_argument(
        "--green-image",
        default=DEFAULT_GREEN_IMAGE,
        help=f"Green agent image (default: {DEFAULT_GREEN_IMAGE})",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for results (default: current directory)",
    )
    parser.add_argument(
        "--skip-pull",
        action="store_true",
        help="Skip pulling images",
    )
    parser.add_argument(
        "--participant-name",
        default="white_agent",
        help="Participant name for results (default: white_agent)",
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("🚀 ETHICS BENCH EVALUATION ORCHESTRATOR")
    print("="*80)
    print(f"White Agent: {args.white_image}")
    print(f"Green Agent: {args.green_image}")
    print(f"Output Dir: {args.output_dir or 'current directory'}")
    print()
    
    # Pull images
    if not args.skip_pull:
        print("📦 PULLING DOCKER IMAGES")
        print("="*80)
        if not pull_image(args.white_image):
            print("❌ Failed to pull white agent image")
            return 1
        print()
    
    # Start white agent
    white_process = None
    try:
        white_process = await run_white_agent(args.white_image)
        if white_process is None:
            print("❌ Failed to start white agent")
            return 1
        
        # Wait a bit more for stability
        await asyncio.sleep(2)
        
        # Run evaluation
        success, results = await run_evaluation(WHITE_AGENT_URL, args.participant_name)
        if not success:
            print("❌ Evaluation failed")
            return 1
        
        # Save results
        leaderboard_path, provenance_path = save_results(
            results,
            args.white_image,
            args.green_image,
            args.participant_name,
            args.output_dir,
        )
        
        if leaderboard_path is None:
            print("⚠️  Could not save results")
            return 1
        
        # Print summary
        print(f"\n{'='*80}")
        print("✨ EVALUATION COMPLETE")
        print(f"{'='*80}")
        print(f"Leaderboard: {leaderboard_path}")
        print(f"Provenance: {provenance_path}")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Evaluation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up
        if white_process is not None:
            print("\n🧹 Cleaning up...")
            print("Stopping white agent...")
            try:
                subprocess.run(
                    ["docker", "stop", "ethics-bench-white-agent"],
                    capture_output=True,
                    timeout=10,
                )
            except Exception as e:
                print(f"Note: {e}")
            
            white_process.terminate()
            try:
                white_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                white_process.kill()
                white_process.wait()
            print("✅ Cleanup complete")


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
