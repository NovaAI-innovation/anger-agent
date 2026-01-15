#!/usr/bin/env python3
"""Quick test runner for document_categorizer agent."""

import sys
import os
import tempfile
from pathlib import Path

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, framework_dir)

from runtime.agent import Agent


def main():
    """Start the agent with document categorizer config."""
    config_path = os.path.join(current_dir, 'config.yaml')
    agents_md_path = os.path.join(current_dir, 'AGENTS.md')

    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        inbox_path = os.path.join(tmpdir, 'inbox')
        errors_path = os.path.join(tmpdir, 'errors')
        processed_path = os.path.join(tmpdir, 'processed')
        review_path = os.path.join(tmpdir, 'review')

        os.makedirs(inbox_path, exist_ok=True)
        os.makedirs(errors_path, exist_ok=True)
        os.makedirs(processed_path, exist_ok=True)
        os.makedirs(review_path, exist_ok=True)

        # Set environment variables for testing
        os.environ['INBOX_PATH'] = inbox_path
        os.environ['ERRORS_PATH'] = errors_path
        os.environ['PROCESSED_PATH'] = processed_path
        os.environ['REVIEW_PATH'] = review_path

        try:
            print(f"Starting Document Categorizer Agent")
            print(f"Config: {config_path}")
            print(f"Inbox: {inbox_path}")
            print(f"Errors: {errors_path}")
            print(f"Processed: {processed_path}")
            print(f"Review: {review_path}")
            print()

            agent = Agent(config_path=config_path, agents_md_path=agents_md_path)
            print(f"Agent initialized: {agent.config.agent_id}")
            print(f"Agent type: {agent.config.agent_type}")
            print()
            print("Agent ready, waiting for files in inbox...")
            print("To test, create text files in the inbox folder.")
            print("Press Ctrl+C to stop.")
            print()

            agent.run_sync()
        except KeyboardInterrupt:
            print("\n\nAgent stopped by user")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
