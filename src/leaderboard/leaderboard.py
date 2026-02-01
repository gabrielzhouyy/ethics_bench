"""
Leaderboard result formatting and storage for ethics bench evaluations.

Stores evaluation results in JSON format compatible with Agentbeats leaderboard display.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class LeaderboardResult:
    """Represents a leaderboard result for a single evaluation run."""
    
    def __init__(
        self,
        participant_name: str,
        results: List[Dict[str, Any]],
        config: Optional[Dict[str, Any]] = None,
        run_id: Optional[str] = None,
    ):
        """
        Initialize a leaderboard result.
        
        Args:
            participant_name: Name of the participant agent (e.g., "white_agent")
            results: List of scenario evaluation results
            config: Optional configuration metadata
            run_id: Optional run identifier for tracking
        """
        self.participant_name = participant_name
        self.results = results
        self.config = config or {}
        self.run_id = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.timestamp = datetime.now().isoformat()
    
    def calculate_total_score(self) -> float:
        """Calculate aggregate score across all scenarios."""
        if not self.results:
            return 0.0
        
        scores = [r.get("score", 0) for r in self.results]
        return round(sum(scores) / len(scores), 2)
    
    def calculate_score_breakdown(self) -> Dict[str, float]:
        """Calculate breakdown of scores by component."""
        if not self.results:
            return {}
        
        breakdown = {
            "conclusion_avg": 0.0,
            "stakeholder_avg": 0.0,
            "framework_avg": 0.0,
            "total_avg": 0.0,
            "num_scenarios": len(self.results),
        }
        
        conclusion_scores = [r.get("conclusion_score", 0) for r in self.results]
        stakeholder_scores = [r.get("stakeholder_score", 0) for r in self.results]
        framework_scores = [r.get("framework_comparison_score", 0) for r in self.results]
        total_scores = [r.get("score", 0) for r in self.results]
        
        breakdown["conclusion_avg"] = round(sum(conclusion_scores) / len(conclusion_scores), 2) if conclusion_scores else 0.0
        breakdown["stakeholder_avg"] = round(sum(stakeholder_scores) / len(stakeholder_scores), 2) if stakeholder_scores else 0.0
        breakdown["framework_avg"] = round(sum(framework_scores) / len(framework_scores), 2) if framework_scores else 0.0
        breakdown["total_avg"] = round(sum(total_scores) / len(total_scores), 2) if total_scores else 0.0
        
        return breakdown
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
        score_breakdown = self.calculate_score_breakdown()
        
        return {
            "metadata": {
                "participant": self.participant_name,
                "run_id": self.run_id,
                "timestamp": self.timestamp,
                "num_scenarios": len(self.results),
                "config": self.config,
            },
            "summary": {
                "total_score": self.calculate_total_score(),
                "score_breakdown": score_breakdown,
            },
            "results": self.results,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class LeaderboardManager:
    """Manages leaderboard result storage and retrieval."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize leaderboard manager.
        
        Args:
            base_path: Base directory for results/submissions (defaults to workspace root)
        """
        if base_path is None:
            # Use current working directory or environment variable
            base_path = os.getenv("ETHICS_BENCH_HOME", os.getcwd())
        
        self.base_path = Path(base_path)
        self.results_dir = self.base_path / "results"
        self.submissions_dir = self.base_path / "submissions"
        
        # Create directories if they don't exist
        self.results_dir.mkdir(exist_ok=True, parents=True)
        self.submissions_dir.mkdir(exist_ok=True, parents=True)
    
    def save_result(
        self,
        result: LeaderboardResult,
        save_submission_metadata: bool = True,
    ) -> str:
        """
        Save a leaderboard result to disk.
        
        Args:
            result: LeaderboardResult instance to save
            save_submission_metadata: Whether to save submission metadata TOML
        
        Returns:
            Path to saved result file
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        participant_normalized = result.participant_name.replace(" ", "_")
        filename = f"{participant_normalized}-{timestamp}.json"
        
        result_path = self.results_dir / filename
        
        # Save JSON result
        with open(result_path, "w") as f:
            f.write(result.to_json())
        
        print(f"✅ Leaderboard result saved: {result_path}")
        
        # Save submission metadata if requested
        if save_submission_metadata:
            self._save_submission_metadata(result, timestamp, participant_normalized)
        
        return str(result_path)
    
    def _save_submission_metadata(
        self,
        result: LeaderboardResult,
        timestamp: str,
        participant_normalized: str,
    ) -> None:
        """Save submission metadata as TOML."""
        try:
            import tomli_w
        except ImportError:
            print("⚠️  tomli-w not installed, skipping submission metadata")
            return
        
        submission_data = {
            "submission": {
                "timestamp": result.timestamp,
                "run_id": result.run_id,
                "participant": result.participant_name,
                "num_scenarios": len(result.results),
                "total_score": result.calculate_total_score(),
                "config": result.config,
            }
        }
        
        metadata_filename = f"{participant_normalized}-{timestamp}.toml"
        metadata_path = self.submissions_dir / metadata_filename
        
        with open(metadata_path, "wb") as f:
            tomli_w.dump(submission_data, f)
        
        print(f"✅ Submission metadata saved: {metadata_path}")
    
    def load_result(self, result_path: str) -> LeaderboardResult:
        """
        Load a leaderboard result from disk.
        
        Args:
            result_path: Path to result JSON file
        
        Returns:
            LeaderboardResult instance
        """
        with open(result_path, "r") as f:
            data = json.load(f)
        
        metadata = data.get("metadata", {})
        results = data.get("results", [])
        
        return LeaderboardResult(
            participant_name=metadata.get("participant", "unknown"),
            results=results,
            config=metadata.get("config", {}),
            run_id=metadata.get("run_id"),
        )
    
    def get_latest_results(self, limit: int = 10) -> List[str]:
        """
        Get paths to latest result files.
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of result file paths (most recent first)
        """
        result_files = sorted(self.results_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        return [str(f) for f in result_files[:limit]]
    
    def aggregate_results(self, result_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Aggregate multiple results into a summary.
        
        Args:
            result_paths: List of result file paths (defaults to all recent results)
        
        Returns:
            Aggregated leaderboard data
        """
        if result_paths is None:
            result_paths = self.get_latest_results()
        
        results = [self.load_result(path) for path in result_paths]
        
        if not results:
            return {"error": "No results to aggregate"}
        
        participants = {}
        for result in results:
            if result.participant_name not in participants:
                participants[result.participant_name] = {
                    "runs": [],
                    "scores": [],
                    "last_updated": None,
                }
            
            score_breakdown = result.calculate_score_breakdown()
            participants[result.participant_name]["runs"].append({
                "run_id": result.run_id,
                "timestamp": result.timestamp,
                "score": result.calculate_total_score(),
                "breakdown": score_breakdown,
            })
            participants[result.participant_name]["scores"].append(result.calculate_total_score())
            participants[result.participant_name]["last_updated"] = result.timestamp
        
        # Calculate aggregate stats per participant
        leaderboard = []
        for participant_name, data in participants.items():
            scores = data["scores"]
            leaderboard.append({
                "agent": participant_name,
                "score": round(sum(scores) / len(scores), 2),
                "num_runs": len(scores),
                "highest_run": max(scores),
                "lowest_run": min(scores),
                "last_updated": data["last_updated"],
                "all_runs": data["runs"],
            })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "leaderboard": leaderboard,
            "timestamp": datetime.now().isoformat(),
            "total_results": sum(len(data["runs"]) for data in participants.values()),
        }


def save_evaluation_results(
    participant_name: str,
    evaluation_results: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
    base_path: Optional[str] = None,
) -> str:
    """
    Convenience function to save evaluation results to leaderboard.
    
    Args:
        participant_name: Name of participant agent
        evaluation_results: List of scenario evaluation results
        config: Optional configuration metadata
        run_id: Optional run identifier
        base_path: Optional base path for results directory
    
    Returns:
        Path to saved result file
    """
    result = LeaderboardResult(
        participant_name=participant_name,
        results=evaluation_results,
        config=config,
        run_id=run_id,
    )
    
    manager = LeaderboardManager(base_path)
    return manager.save_result(result)
