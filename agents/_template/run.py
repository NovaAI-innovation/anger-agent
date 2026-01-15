#!/usr/bin/env python3
"""
Run this agent.

This is the entry point for your agent.
It loads the local config.yaml and runs the event loop.

To run:
    python run.py

Or from parent directory:
    ./scripts/run.sh [agent_name]

NO MODIFICATIONS NEEDED - all customization is in config.yaml!
"""

import sys
import os

# Add parent directories to path so we can import runtime
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, project_root)

from runtime.agent import Agent


def main():
    """Start the agent."""
    # Get config path (in same directory as this script)
    config_path = os.path.join(current_dir, 'config.yaml')
    agents_md_path = os.path.join(current_dir, 'AGENTS.md')

    # Create and run agent
    try:
        agent = Agent(config_path=config_path, agents_md_path=agents_md_path)
        agent.run_sync()
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
