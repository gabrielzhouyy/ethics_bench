"""
Shared run identifier generator for correlating logs across agents.
Creates a unique adjective-noun pair for each evaluation run.
"""

import random
import os
from datetime import datetime


# Predefined lists of adjectives and nouns
ADJECTIVES = [
    "crimson", "iron", "shadow", "blazing", "silent",
    "stormborn", "ashen", "scarlet", "wild", "frozen",
    "golden", "raging", "midnight", "burning", "ancient",
    "sacred", "fallen", "radiant", "dark", "furious",
    "reckless", "thundering", "ghostly", "vengeful", "eternal",
    "shattered", "howling", "lone", "hidden", "infinite",
    "cinder", "restless", "cold", "grim", "untamed","fire"
]

NOUNS = [
    "phoenix", "dragon", "wolf", "raven", "lion",
    "storm", "flame", "blade", "shadow", "thunder",
    "titan", "spirit", "ember", "fang", "ghost",
    "mountain", "river", "tempest", "ice", "fire",
    "moon", "star", "sun", "night", "dawn",
    "serpent", "hawk", "rider", "giant", "warrior",
    "beast", "wing", "heart", "soul", "crown","clock"
]


class RunIdentifier:
    """Singleton class to maintain consistent run identifier across the evaluation."""
    
    _instance = None
    _identifier = None
    _timestamp = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RunIdentifier, cls).__new__(cls)
        return cls._instance
    
    def get_identifier(self) -> str:
        """
        Get or create the run identifier for this evaluation run.
        Format: {timestamp}_{adjective}_{noun}
        
        First checks for ETHICS_BENCH_RUN_ID environment variable to ensure
        consistency across subprocess boundaries.
        
        Returns:
            String identifier for this run
        """
        if self._identifier is None:
            # Check if run ID was set via environment variable (for subprocess consistency)
            env_run_id = os.environ.get('ETHICS_BENCH_RUN_ID')
            if env_run_id:
                self._identifier = env_run_id
                # Extract timestamp from identifier
                self._timestamp = '_'.join(env_run_id.split('_')[:2])
            else:
                # Generate new identifier
                self._timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                adjective = random.choice(ADJECTIVES)
                noun = random.choice(NOUNS)
                self._identifier = f"{self._timestamp}_{adjective}_{noun}"
        
        return self._identifier
    
    def get_timestamp(self) -> str:
        """Get just the timestamp portion."""
        if self._timestamp is None:
            self.get_identifier()
        return self._timestamp
    
    def reset(self):
        """Reset the identifier (useful for testing or new runs)."""
        self._identifier = None
        self._timestamp = None


def get_run_identifier() -> str:
    """
    Convenience function to get the current run identifier.
    
    Returns:
        String identifier for this run
    """
    return RunIdentifier().get_identifier()


def get_timestamp() -> str:
    """
    Convenience function to get the current run timestamp.
    
    Returns:
        Timestamp string for this run
    """
    return RunIdentifier().get_timestamp()
