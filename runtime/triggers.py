"""
Trigger system for event detection.

DESIGN REASONING:
- Triggers are events that cause workflows to execute
- Multiple trigger types (file_watch, message, schedule)
- v0.1 implements file_watch only
- Extensible for future trigger types
- Async event loop for non-blocking detection
"""

import os
import asyncio
import logging
from pathlib import Path
from fnmatch import fnmatch
from typing import Any, Dict, Callable, Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class TriggerHandler(FileSystemEventHandler):
    """
    Handles file system events from watchdog.

    DESIGN: Converts file system events into trigger events.
    """

    def __init__(self, trigger_callback: Callable, paths: List[str],
                 patterns: List[str], logger: logging.Logger, event_loop=None):
        """
        Initialize handler.

        Args:
            trigger_callback: Async callback when trigger fires
            paths: Paths to watch
            patterns: Glob patterns to match
            logger: Logger instance
            event_loop: asyncio event loop for scheduling callbacks from watchdog thread
        """
        super().__init__()
        self.trigger_callback = trigger_callback
        self.paths = paths
        self.patterns = patterns
        self.logger = logger
        self.event_loop = event_loop
        self.seen_files = set()  # Track seen files to avoid duplicates

    def on_created(self, event):
        """Handle file creation."""
        import os
        file_path = event.src_path

        # Skip directories
        if os.path.isdir(file_path):
            return

        # Check if path matches any watched paths
        if not self._path_matches(file_path):
            return

        # Check if filename matches pattern
        filename = Path(file_path).name
        if not self._pattern_matches(filename):
            return

        self.logger.info(f"File event detected: {file_path}")

        # Fire trigger (non-blocking)
        # Use run_coroutine_threadsafe because this is called from watchdog's thread
        if self.event_loop and self.event_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._fire_trigger("file_created", file_path),
                self.event_loop
            )

    def on_modified(self, event):
        """Handle file modification."""
        # Skip for file_watch (only care about creation)
        pass

    def _path_matches(self, file_path: str) -> bool:
        """Check if file path is in watched paths."""
        for path in self.paths:
            if file_path.startswith(path):
                return True
        return False

    def _pattern_matches(self, filename: str) -> bool:
        """Check if filename matches any pattern."""
        for pattern in self.patterns:
            if fnmatch(filename, pattern):
                return True
        return False

    async def _fire_trigger(self, trigger_type: str, file_path: str):
        """Fire the trigger callback."""
        try:
            await self.trigger_callback({
                "type": trigger_type,
                "file_path": file_path,
                "file_name": Path(file_path).name,
                "file_stem": Path(file_path).stem
            })
        except Exception as e:
            self.logger.error(f"Error firing trigger: {e}")


class TriggerSystem:
    """
    Manages all triggers and event detection.

    DESIGN: Central hub for all trigger types.
    Watches for events and routes to workflows.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize trigger system.

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.triggers: Dict[str, Dict] = {}
        self.file_observer: Optional[Observer] = None
        self.trigger_handlers: List[TriggerHandler] = []

    def register_trigger(self, trigger_id: str, trigger_def: Dict):
        """
        Register a trigger.

        Args:
            trigger_id: Unique trigger identifier
            trigger_def: Trigger definition from config
        """
        self.triggers[trigger_id] = trigger_def
        self.logger.info(f"Registered trigger: {trigger_id} ({trigger_def.get('type')})")

    async def start(self, trigger_callback: Callable):
        """
        Start listening for triggers.

        Args:
            trigger_callback: Async function to call when trigger fires

        DESIGN REASONING:
        - Sets up file watcher for all file_watch triggers
        - Will support other trigger types (message, schedule) in future
        - Non-blocking via asyncio
        """
        self.logger.info("Starting trigger system...")

        # Set up file watchers for file_watch triggers
        file_watch_triggers = {
            tid: tdef for tid, tdef in self.triggers.items()
            if tdef.get("type") == "file_watch"
        }

        if file_watch_triggers:
            await self._setup_file_watchers(file_watch_triggers, trigger_callback)

        self.logger.info("Trigger system ready")

    async def stop(self):
        """Stop listening for triggers."""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        self.logger.info("Trigger system stopped")

    async def _setup_file_watchers(self, triggers: Dict, trigger_callback: Callable):
        """
        Set up file watchers for all file_watch triggers.

        DESIGN:
        - Groups triggers by path (one watcher per path)
        - Applies patterns to filter events
        - Routes events to trigger callback
        """
        # Group by path
        paths_to_watch = {}
        for trigger_id, trigger_def in triggers.items():
            path = trigger_def.get("path")
            patterns = trigger_def.get("patterns", ["*"])

            if path not in paths_to_watch:
                paths_to_watch[path] = {
                    "patterns": [],
                    "triggers": []
                }

            paths_to_watch[path]["patterns"].extend(patterns)
            paths_to_watch[path]["triggers"].append(trigger_id)

        # Get the current event loop for use by file watchers
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        # Create watcher
        self.file_observer = Observer()

        # Add handlers for each path
        for path, config in paths_to_watch.items():
            # Ensure path exists
            Path(path).mkdir(parents=True, exist_ok=True)

            # Create handler
            handler = TriggerHandler(
                trigger_callback,
                [path],
                config["patterns"],
                self.logger,
                loop
            )

            self.trigger_handlers.append(handler)

            # Register handler
            self.file_observer.schedule(handler, path, recursive=False)

            self.logger.info(
                f"Watching {path} for patterns: {config['patterns']}"
            )

        # Start observer in thread
        self.file_observer.start()

    async def match_trigger(self, trigger_event: Dict) -> Optional[str]:
        """
        Match an event to a trigger.

        Args:
            trigger_event: Event data

        Returns:
            Trigger ID if match found, None otherwise

        DESIGN: Routes events to appropriate trigger definitions.
        """
        # Find trigger that matches this event
        for trigger_id, trigger_def in self.triggers.items():
            trigger_type = trigger_def.get("type")

            if trigger_type == "file_watch":
                # Already matched by file watcher
                return trigger_id

        return None

    async def get_trigger_workflow(self, trigger_id: str) -> Optional[str]:
        """Get the workflow to execute for a trigger."""
        trigger_def = self.triggers.get(trigger_id)
        if trigger_def:
            return trigger_def.get("workflow_id")
        return None
