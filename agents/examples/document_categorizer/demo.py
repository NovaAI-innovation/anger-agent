#!/usr/bin/env python3
"""Demo script for document_categorizer agent."""

import sys
import os
import time
import tempfile
import json
import asyncio
from pathlib import Path

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, framework_dir)

from runtime.config import Config
from runtime.logger import setup_logger
from runtime.tools import ToolRegistry
from runtime.workflows import WorkflowEngine, WorkflowContext


def create_demo_files(inbox_path):
    """Create sample documents for categorization."""
    samples = [
        ("error_report.txt", "System error occurred during processing. Database connection failed."),
        ("success_report.txt", "Operation completed successfully. All tests passed."),
        ("warning_notice.txt", "Please be advised of pending system maintenance scheduled."),
        ("unknown_doc.txt", "Lorem ipsum dolor sit amet consectetur adipiscing elit."),
    ]

    for filename, content in samples:
        filepath = os.path.join(inbox_path, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"[OK] Created: {filename}")


async def process_files(config_path, inbox_path, errors_path, processed_path, review_path):
    """Process files using the agent's workflow engine."""
    # Set environment variables
    os.environ['INBOX_PATH'] = inbox_path
    os.environ['ERRORS_PATH'] = errors_path
    os.environ['PROCESSED_PATH'] = processed_path
    os.environ['REVIEW_PATH'] = review_path

    # Load config
    config = Config(config_path, os.path.join(current_dir, 'AGENTS.md'))
    print(f"\nAgent config loaded: {config.agent_id}")

    # Set up logging
    logger = setup_logger(config.agent_id, f"{current_dir}/demo.log", "INFO")

    # Initialize workflow engine
    tool_registry = ToolRegistry()
    workflow_engine = WorkflowEngine(tool_registry, logger)

    # Get the workflow definition
    workflow_def = config.workflows.get("categorize_and_route")
    if not workflow_def:
        print("ERROR: Workflow 'categorize_and_route' not found in config")
        return

    # Process each file in inbox
    files = [f for f in os.listdir(inbox_path) if f.endswith('.txt')]
    print(f"\nProcessing {len(files)} files...")

    for filename in files:
        filepath = os.path.join(inbox_path, filename)
        print(f"\n  Processing: {filename}")

        # Create trigger event
        trigger_event = {
            "file_path": filepath,
            "file_name": filename,
            "timestamp": "2026-01-15T10:50:29Z"
        }

        # Create workflow context
        context = WorkflowContext("categorize_and_route", trigger_event)

        # Execute workflow
        try:
            result = await workflow_engine.execute_workflow(
                "categorize_and_route", workflow_def, context
            )
            if result.get("success"):
                print(f"    [DONE] Successfully processed")
            else:
                print(f"    [ERROR] Processing failed: {result.get('error')}")
        except Exception as e:
            print(f"    [ERROR] Exception: {e}")

    # Give file system time to sync
    await asyncio.sleep(1)


def display_results(inbox_path, errors_path, processed_path, review_path):
    """Display the categorization results."""
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
                                print(f"    Tags: {', '.join(meta.get('tags', []))}")
                                print(f"    Confidence: {meta.get('confidence', 'N/A')}")
                        except json.JSONDecodeError:
                            print(f"    (metadata file is empty or invalid)")
            else:
                print("  (empty)")
        else:
            print("  (folder not found)")

    print("\n" + "="*60)


async def main_async():
    """Run the demo asynchronously."""
    config_path = os.path.join(current_dir, 'config.yaml')

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

        print("Document Categorizer Agent - Demo")
        print("="*60)
        print("\n1. Creating sample documents...")
        create_demo_files(inbox_path)

        print("\n2. Processing files with agent...")
        await process_files(config_path, inbox_path, errors_path, processed_path, review_path)

        print("\n3. Displaying results...")
        display_results(inbox_path, errors_path, processed_path, review_path)


def main():
    """Entry point."""
    try:
        asyncio.run(main_async())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
