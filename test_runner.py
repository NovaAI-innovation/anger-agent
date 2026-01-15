#!/usr/bin/env python3
"""Quick test runner for file_validator agent with test config."""

import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from runtime.agent import Agent

def main():
    """Start the agent with test config."""
    config_path = os.path.join(current_dir, 'test_config.yaml')
    agents_md_path = os.path.join(current_dir, 'agents/examples/file_validator/AGENTS.md')

    try:
        print(f"Loading config from: {config_path}")
        agent = Agent(config_path=config_path, agents_md_path=agents_md_path)
        print(f"Agent started: {agent.config.agent_id}")
        agent.run_sync()
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
