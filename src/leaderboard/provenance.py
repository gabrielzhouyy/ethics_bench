"""
Record provenance information for leaderboard submissions.

Captures docker image digests, GitHub Actions metadata, and other reproducibility information.
"""

import json
import os
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def get_docker_image_digest(image_name: str) -> Optional[str]:
    """
    Get the SHA256 digest of a Docker image.
    
    Args:
        image_name: Full image name (e.g., ghcr.io/gabrielzhouyy/ethics_bench:latest)
    
    Returns:
        SHA256 digest or None if unable to retrieve
    """
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.RepoDigests}}", image_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            digests = result.stdout.strip().strip("[]").split()
            if digests:
                # Return first digest (usually has SHA256)
                return digests[0]
    except Exception as e:
        print(f"⚠️  Could not get docker digest for {image_name}: {e}")
    
    return None


def get_git_commit_info() -> Dict[str, str]:
    """
    Get git commit information if running in a git repository.
    
    Returns:
        Dictionary with git commit info
    """
    info = {}
    try:
        # Get current commit hash
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        if commit:
            info["commit"] = commit
        
        # Get current branch
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        if branch:
            info["branch"] = branch
        
        # Get repository URL
        repo_url = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        if repo_url:
            info["repository"] = repo_url
    except Exception as e:
        print(f"⚠️  Could not get git info: {e}")
    
    return info


def get_github_actions_context() -> Dict[str, str]:
    """
    Get GitHub Actions context if running in GitHub Actions.
    
    Returns:
        Dictionary with GitHub Actions info
    """
    info = {}
    
    # Check if running in GitHub Actions
    if os.getenv("GITHUB_ACTIONS"):
        info["ci_system"] = "github_actions"
        info["workflow"] = os.getenv("GITHUB_WORKFLOW", "")
        info["run_id"] = os.getenv("GITHUB_RUN_ID", "")
        info["run_number"] = os.getenv("GITHUB_RUN_NUMBER", "")
        info["actor"] = os.getenv("GITHUB_ACTOR", "")
        info["ref"] = os.getenv("GITHUB_REF", "")
        info["sha"] = os.getenv("GITHUB_SHA", "")
    
    return info


def record_submission_provenance(
    participant_name: str,
    scenario_name: str,
    green_agent_image: str,
    white_agent_image: str,
    config: Optional[Dict[str, Any]] = None,
    base_path: Optional[str] = None,
) -> str:
    """
    Record full provenance information for a submission.
    
    Args:
        participant_name: Name of participant agent
        scenario_name: Name of scenario tested
        green_agent_image: Green agent docker image name
        white_agent_image: White agent docker image name
        config: Optional additional configuration
        base_path: Optional base path for submissions directory
    
    Returns:
        Path to saved provenance file
    """
    if base_path is None:
        base_path = os.getcwd()
    
    submissions_dir = Path(base_path) / "submissions"
    submissions_dir.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    participant_normalized = participant_name.replace(" ", "_")
    
    provenance = {
        "timestamp": datetime.now().isoformat(),
        "participant": participant_name,
        "scenario": scenario_name,
        "images": {
            "green_agent": {
                "name": green_agent_image,
                "digest": get_docker_image_digest(green_agent_image),
            },
            "white_agent": {
                "name": white_agent_image,
                "digest": get_docker_image_digest(white_agent_image),
            },
        },
        "git": get_git_commit_info(),
        "github_actions": get_github_actions_context(),
        "config": config or {},
    }
    
    # Save provenance as JSON
    provenance_filename = f"provenance-{participant_normalized}-{timestamp}.json"
    provenance_path = submissions_dir / provenance_filename
    
    with open(provenance_path, "w") as f:
        json.dump(provenance, f, indent=2)
    
    print(f"✅ Provenance recorded: {provenance_path}")
    
    return str(provenance_path)


def get_submission_hash(submission_data: Dict[str, Any]) -> str:
    """
    Generate a hash of submission data for integrity verification.
    
    Args:
        submission_data: Dictionary of submission data
    
    Returns:
        SHA256 hash of submission
    """
    # Convert to deterministic JSON string
    json_str = json.dumps(submission_data, sort_keys=True, default=str)
    return hashlib.sha256(json_str.encode()).hexdigest()
