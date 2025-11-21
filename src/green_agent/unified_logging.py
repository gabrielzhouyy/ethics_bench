"""
Unified logging system for green agent.
Handles both evaluation logging and callback logging with shared infrastructure.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

# Import shared run identifier
from src.run_identifier import get_run_identifier


class LogType(Enum):
    """Enum for different log types."""
    EVALUATION = "evaluation"
    CALLBACK = "callback"
    BOTH = "both"


class GreenAgentLogger:
    """Unified logger for green agent with multiple output streams."""
    
    def __init__(self):
        """Initialize the unified logger system."""
        # Create logs directory if it doesn't exist
        os.makedirs("src/green_agent/agent_logs", exist_ok=True)
        
        # Get run identifier
        self.run_id = get_run_identifier()
        
        # Create separate loggers to avoid interference
        self.eval_logger = logging.getLogger('green_agent_evaluation')
        self.callback_logger = logging.getLogger('green_agent_callbacks')
        
        # Set levels
        self.eval_logger.setLevel(logging.INFO)
        self.callback_logger.setLevel(logging.INFO)
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup evaluation logger
        eval_handler = logging.FileHandler(
            f"src/green_agent/agent_logs/evaluation_{self.run_id}.log"
        )
        eval_handler.setFormatter(formatter)
        self.eval_logger.addHandler(eval_handler)
        
        # Setup callback logger
        callback_handler = logging.FileHandler(
            f"src/green_agent/agent_logs/agent_callbacks_{self.run_id}.log"
        )
        callback_handler.setFormatter(formatter)
        self.callback_logger.addHandler(callback_handler)
        
        # Console handler for callbacks (matches original behavior)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.callback_logger.addHandler(console_handler)
        
        # Console handler for evaluation (matches original behavior)
        eval_console_handler = logging.StreamHandler()
        eval_console_handler.setFormatter(formatter)
        self.eval_logger.addHandler(eval_console_handler)
    
    def _log_to_target(self, log_type: LogType, level: str, message: str, *args):
        """Log to the appropriate target(s) based on log type."""
        if log_type == LogType.EVALUATION:
            getattr(self.eval_logger, level)(message, *args)
        elif log_type == LogType.CALLBACK:
            getattr(self.callback_logger, level)(message, *args)
        elif log_type == LogType.BOTH:
            getattr(self.eval_logger, level)(message, *args)
            getattr(self.callback_logger, level)(message, *args)
    
    # ========================================
    # Evaluation-specific logging functions
    # ========================================
    
    def log_scenario_start(self, scenario_name: str, success_criteria: str):
        """Log the start of a new evaluation scenario."""
        separator = "=" * 80
        self._log_to_target(LogType.BOTH, 'info', separator)
        self._log_to_target(LogType.BOTH, 'info', "[SCENARIO START] %s", scenario_name)
        self._log_to_target(LogType.BOTH, 'info', "[SUCCESS CRITERIA] %s", success_criteria)
        self._log_to_target(LogType.BOTH, 'info', separator)
    
    def log_white_agent_response(self, message_num: int, response: str):
        """Log the response received from white agent."""
        self._log_to_target(LogType.BOTH, 'info', "[WHITE AGENT RESPONSE %d] %s", message_num, response)
    
    def log_evaluation_check(self, check_name: str, passed: bool, details: str = ""):
        """Log an evaluation check and its result."""
        status = "PASS" if passed else "FAIL"
        if details:
            self._log_to_target(LogType.BOTH, 'info', "[EVAL CHECK] %s: %s - %s", check_name, status, details)
        else:
            self._log_to_target(LogType.BOTH, 'info', "[EVAL CHECK] %s: %s", check_name, status)
    
    def log_scenario_result(self, scenario_name: str, passed: bool, reason: str = ""):
        """Log the final result of a scenario evaluation."""
        status = "✅ PASSED" if passed else "❌ FAILED"
        separator = "=" * 80
        self._log_to_target(LogType.BOTH, 'info', separator)
        self._log_to_target(LogType.BOTH, 'info', "[SCENARIO RESULT] %s: %s", scenario_name, status)
        if reason:
            self._log_to_target(LogType.BOTH, 'info', "[REASON] %s", reason)
        self._log_to_target(LogType.BOTH, 'info', separator)
    
    def log_evaluation_summary(self, results: List[Dict[str, Any]]):
        """Log summary of all evaluation results."""
        separator = "=" * 80
        self._log_to_target(LogType.BOTH, 'info', "")
        self._log_to_target(LogType.BOTH, 'info', separator)
        self._log_to_target(LogType.BOTH, 'info', "[EVALUATION SUMMARY]")
        self._log_to_target(LogType.BOTH, 'info', separator)
        
        total = len(results)
        avg_score = sum(r.get("score", 0) for r in results) / total if total > 0 else 0
        avg_conversation_turns = sum(r.get("conversation_turns", 0) for r in results) / total if total > 0 else 0
        avg_debate_iterations = sum(r.get("debate_iterations", 0) for r in results) / total if total > 0 else 0
        
        self._log_to_target(LogType.BOTH, 'info', "Total Scenarios: %d", total)
        self._log_to_target(LogType.BOTH, 'info', "Average Score: %.1f/100", avg_score)
        self._log_to_target(LogType.BOTH, 'info', "Average Conversation Turns: %.1f", avg_conversation_turns)
        self._log_to_target(LogType.BOTH, 'info', "Average Debate Iterations: %.1f", avg_debate_iterations)
        
        self._log_to_target(LogType.BOTH, 'info', "")
        self._log_to_target(LogType.BOTH, 'info', "Detailed Scores:")
        for i, result in enumerate(results, 1):
            score = result.get("score", 0)
            turns = result.get("conversation_turns", 0)
            debates = result.get("debate_iterations", 0)
            self._log_to_target(LogType.BOTH, 'info', "  %d. %s - Score: %d/100 (%d turns, %d debate iterations)", 
                              i, result.get("scenario", "Unknown"), score, turns, debates)
            if "error" in result:
                self._log_to_target(LogType.BOTH, 'info', "     Error: %s", result["error"])
        
        self._log_to_target(LogType.BOTH, 'info', separator)
    
    # ========================================
    # Callback-specific logging functions
    # ========================================
    
    def log_logic_handoff(self, from_component: str, to_component: str, context: str = ""):
        """Log when logic is handed from one component/subagent to another."""
        msg = f"[handoff] {from_component} → {to_component}"
        if context:
            msg += f" | Context: {context}"
        self._log_to_target(LogType.CALLBACK, 'info', msg)
    
    def log_step(self, component: str, step: str, details: str = ""):
        """Log a major step or event in the green agent's logic."""
        msg = f"[step] {component}: {step}"
        if details:
            msg += f" | Details: {details}"
        self._log_to_target(LogType.CALLBACK, 'info', msg)
    
    def log_evaluator_interaction(self, step: str, details: str = ""):
        """Log evaluator_agent interactions to the evaluation log only."""
        msg = f"[EVALUATOR] {step}"
        if details:
            msg += f"\n{details}"
        self._log_to_target(LogType.EVALUATION, 'info', msg)
    
    # ========================================
    # Shared logging functions
    # ========================================
    
    def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """Log an error during evaluation."""
        if exception:
            self._log_to_target(LogType.BOTH, 'error', "[ERROR] %s: %s", error_msg, str(exception))
        else:
            self._log_to_target(LogType.BOTH, 'error', "[ERROR] %s", error_msg)
    
    def log_user_message(self, message_num: int, message: str):
        """Log a message sent from green agent (as user) to white agent."""
        truncated = message[:200] + "..." if len(message) > 200 else message
        self._log_to_target(LogType.EVALUATION, 'info', "[USER MESSAGE %d] %s", message_num, truncated)
    
    def log_keyword_analysis(self, keywords: List[str], text: str, found: List[str]):
        """Log keyword analysis for evaluation."""
        self._log_to_target(LogType.EVALUATION, 'info', "[KEYWORD ANALYSIS] Searching for: %s", keywords)
        self._log_to_target(LogType.EVALUATION, 'info', "[KEYWORD ANALYSIS] Found: %s", found if found else "None")


# Create global logger instance
_logger_instance = None

def get_logger() -> GreenAgentLogger:
    """Get the global logger instance (singleton pattern)."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = GreenAgentLogger()
    return _logger_instance


# ========================================
# Convenience functions (backward compatibility)
# ========================================

def log_scenario_start(scenario_name: str, success_criteria: str):
    """Log the start of a new evaluation scenario."""
    get_logger().log_scenario_start(scenario_name, success_criteria)

def log_white_agent_response(message_num: int, response: str):
    """Log the response received from white agent."""
    get_logger().log_white_agent_response(message_num, response)

def log_evaluation_check(check_name: str, passed: bool, details: str = ""):
    """Log an evaluation check and its result."""
    get_logger().log_evaluation_check(check_name, passed, details)

def log_scenario_result(scenario_name: str, passed: bool, reason: str = ""):
    """Log the final result of a scenario evaluation."""
    get_logger().log_scenario_result(scenario_name, passed, reason)

def log_evaluation_summary(results: List[Dict[str, Any]]):
    """Log summary of all evaluation results."""
    get_logger().log_evaluation_summary(results)

def log_logic_handoff(from_component: str, to_component: str, context: str = ""):
    """Log when logic is handed from one component/subagent to another."""
    get_logger().log_logic_handoff(from_component, to_component, context)

def log_step(component: str, step: str, details: str = ""):
    """Log a major step or event in the green agent's logic."""
    get_logger().log_step(component, step, details)

def log_evaluator_interaction(step: str, details: str = ""):
    """Log evaluator_agent interactions to the evaluation log only."""
    get_logger().log_evaluator_interaction(step, details)

def log_error(error_msg: str, exception: Optional[Exception] = None):
    """Log an error during evaluation."""
    get_logger().log_error(error_msg, exception)

def log_user_message(message_num: int, message: str):
    """Log a message sent from green agent (as user) to white agent."""
    get_logger().log_user_message(message_num, message)

def log_keyword_analysis(keywords: List[str], text: str, found: List[str]):
    """Log keyword analysis for evaluation."""
    get_logger().log_keyword_analysis(keywords, text, found)