"""
Main entry point for V3 multi-agent evaluation system.

Run with: python main_v3.py
"""
import asyncio
from src.launcher_v3 import launch_evaluation_v3

if __name__ == "__main__":
    asyncio.run(launch_evaluation_v3())
