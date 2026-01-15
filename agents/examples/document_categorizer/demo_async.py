#!/usr/bin/env python3
"""Async demo showing the agent responding to inbox files in real-time."""

import sys
import os
import asyncio
import tempfile
import json
import time
from pathlib import Path

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, framework_dir)

from runtime.agent import Agent


async def add_files_over_time(inbox_path, interval=2):
    """Add test files to inbox over time to trigger the agent."""
    files_to_add = [
        ("error_report.txt", "System error occurred during processing. Database connection failed."),
        ("success_report.txt", "Operation completed successfully. All tests passed."),
        ("warning_notice.txt", "Please be advised of pending system maintenance scheduled."),
        ("unknown_doc.txt", "Lorem ipsum dolor sit amet consectetur adipiscing elit."),
    ]

    print(f"\n[Test] Adding files to inbox every {interval} seconds...")
    print(f"[Test] Inbox: {inbox_path}\n")

    for filename, content in files_to_add:
        await asyncio.sleep(interval)
        filepath = os.path.join(inbox_path, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"[Test] Added: {filename}")


async def display_results_async(inbox_path, errors_path, processed_path, review_path):
    """Display results with async delay."""
    await asyncio.sleep(2)

    print("\n" + "="*60)
    print("CATEGORIZATION RESULTS")
    print("="*60)

    folders = {
        "[ERRORS]": errors_path,
        "[PROCESSED - Success]": processed_path,
        "[REVIEW - Other]": review_path,
    }

    for label, folder_path in folders.items():
        print(f"\n{label}:")
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if not f.endswith('.meta.json')]
            if files:
                for file in files:
                    print(f"  {file}")
                    meta_file = os.path.join(folder_path, f"{file}.meta.json")
                    if os.path.exists(meta_file):
                        try:
                            with open(meta_file) as f:
                                meta = json.load(f)
                                print(f"    Category: {meta.get('category', 'N/A')}")
                                tags = meta.get('tags', [])
                                if isinstance(tags, list):
                                    print(f"    Tags: {', '.join(tags)}")
                                else:
                                    print(f"    Tags: {tags}")
                                print(f"    Confidence: {meta.get('confidence', 'N/A')}")
                        except (json.JSONDecodeError, ValueError):
                            pass
            else:
                print("  (no files processed yet)")
        else:
            print("  (folder not found)")

    print("\n" + "="*60)


async def main():
    """Run the async demo."""
    config_path = os.path.join(current_dir, 'config.yaml')
    agents_md_path = os.path.join(current_dir, 'AGENTS.md')

    # Create test directories
    with tempfile.TemporaryDirectory() as tmpdir:
        inbox_path = os.path.join(tmpdir, 'inbox')
        errors_path = os.path.join(tmpdir, 'errors')
        processed_path = os.path.join(tmpdir, 'processed')
        review_path = os.path.join(tmpdir, 'review')

        os.makedirs(inbox_path)
        os.makedirs(errors_path)
        os.makedirs(processed_path)
        os.makedirs(review_path)

        # Set environment variables
        os.environ['INBOX_PATH'] = inbox_path
        os.environ['ERRORS_PATH'] = errors_path
        os.environ['PROCESSED_PATH'] = processed_path
        os.environ['REVIEW_PATH'] = review_path

        print("Document Categorizer Agent - Async Demo")
        print("="*60)
        print(f"Inbox:     {inbox_path}")
        print(f"Errors:    {errors_path}")
        print(f"Processed: {processed_path}")
        print(f"Review:    {review_path}")

        # Create agent
        try:
            agent = Agent(config_path=config_path, agents_md_path=agents_md_path)
            print(f"\nAgent initialized: {agent.config.agent_id}")
            print(f"Agent type: {agent.config.agent_type}")
            print("="*60)
        except Exception as e:
            print(f"Error initializing agent: {e}")
            import traceback
            traceback.print_exc()
            return

        # Run agent and file adder concurrently
        agent_task = asyncio.create_task(run_agent_for_duration(agent, duration=12))
        file_adder_task = asyncio.create_task(add_files_over_time(inbox_path, interval=2))

        try:
            await asyncio.gather(agent_task, file_adder_task)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        # Display results
        await display_results_async(inbox_path, errors_path, processed_path, review_path)


async def run_agent_for_duration(agent, duration):
    """Run agent for specified duration then stop."""
    print("Starting agent (async event loop)...\n")
    agent._running = True

    # Run the agent's main loop with timeout
    try:
        await asyncio.wait_for(agent.run(), timeout=duration)
    except asyncio.TimeoutError:
        print("\n[Test] Stopping agent after timeout...")
        agent._running = False
    except KeyboardInterrupt:
        print("\n[Test] Agent interrupted by user")
        agent._running = False
    except Exception as e:
        print(f"\nAgent error: {e}")
        agent._running = False


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
