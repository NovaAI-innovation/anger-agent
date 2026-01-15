"""
Main agent runtime.

DESIGN REASONING:
- Agent is the main entry point for framework
- Orchestrates all subsystems (config, triggers, workflows, tools)
- Runs async event loop
- Handles shutdown gracefully
"""

import asyncio
import signal
import logging
from pathlib import Path
from runtime.config import Config, ConfigError
from runtime.logger import setup_logger, log_workflow_execution
from runtime.triggers import TriggerSystem
from runtime.workflows import WorkflowEngine, WorkflowContext
from runtime.tools import ToolRegistry
from runtime.hub import HubConnector


class Agent:
    """
    Main agent runtime.

    DESIGN: Orchestrates all subsystems and provides main event loop.
    - Loads configuration
    - Sets up logging
    - Initializes tools and workflows
    - Runs event loop listening for triggers
    - Executes workflows when triggered
    """

    def __init__(self, config_path: str = "config.yaml", agents_md_path: str = None):
        """
        Initialize agent.

        Args:
            config_path: Path to config.yaml
            agents_md_path: Path to AGENTS.md (optional)

        Raises:
            ConfigError: If config is invalid
        """
        # Load configuration
        try:
            self.config = Config(config_path, agents_md_path)
        except ConfigError as e:
            print(f"Error loading configuration: {e}")
            raise

        # Set up logging
        log_config = self.config.logging_config
        log_file = log_config.get("file", f"/tmp/{self.config.agent_id}.log")
        log_level = log_config.get("level", "info").upper()

        self.logger = setup_logger(self.config.agent_id, log_file, log_level)

        self.logger.info(f"Agent initialized: {self.config.agent_id}")
        self.logger.debug(f"Agent type: {self.config.agent_type}")

        # Initialize subsystems
        self.tool_registry = ToolRegistry()
        self.workflow_engine = WorkflowEngine(self.tool_registry, self.logger)
        self.trigger_system = TriggerSystem(self.logger)
        self.hub_connector = HubConnector(self.config, self.logger)

        # Register all triggers
        for trigger_def in self.config.triggers:
            trigger_id = trigger_def.get("id")
            self.trigger_system.register_trigger(trigger_id, trigger_def)

        # Track if running
        self._running = False

    async def run(self):
        """
        Start the agent and run event loop.

        DESIGN REASONING:
        - Initializes all subsystems
        - Starts listening for triggers
        - Enters async event loop
        - Handles graceful shutdown
        """
        self.logger.info("=" * 60)
        self.logger.info(f"Starting agent: {self.config.agent_id}")
        self.logger.info("=" * 60)

        self._running = True

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()

        def signal_handler(sig, frame):
            self.logger.info(f"Received signal {sig}, shutting down...")
            self._running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            # Initialize hub connector (stub in v0.1)
            await self.hub_connector.initialize()

            # Start trigger system
            await self.trigger_system.start(self._on_trigger)

            self.logger.info("Agent ready, waiting for events...")

            # Keep running until interrupted
            while self._running:
                await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Agent error: {e}", exc_info=True)
            raise

        finally:
            await self.shutdown()

    async def _on_trigger(self, trigger_event: dict):
        """
        Handle trigger event.

        Args:
            trigger_event: Event data from trigger system

        DESIGN: Routes event to appropriate workflow and executes it.
        """
        try:
            # Match event to trigger
            trigger_id = await self.trigger_system.match_trigger(trigger_event)

            if not trigger_id:
                self.logger.warning(f"No trigger matched event: {trigger_event}")
                return

            # Get workflow for this trigger
            workflow_id = await self.trigger_system.get_trigger_workflow(trigger_id)

            if not workflow_id:
                self.logger.warning(f"No workflow for trigger: {trigger_id}")
                return

            # Get workflow definition
            workflow_def = self.config.workflows.get(workflow_id)

            if not workflow_def:
                self.logger.error(f"Workflow not found: {workflow_id}")
                return

            # Create execution context
            context = WorkflowContext(workflow_id, trigger_event)

            # Execute workflow
            import time
            start_time = time.time()

            result = await self.workflow_engine.execute_workflow(
                workflow_id, workflow_def, context
            )

            duration_ms = (time.time() - start_time) * 1000

            # Log workflow result
            status = "success" if result.get("success") else "failed"
            log_workflow_execution(
                self.logger, workflow_id, trigger_id, status, duration_ms
            )

            # v0.5: Send result back via hub if needed

        except Exception as e:
            self.logger.error(f"Error handling trigger: {e}", exc_info=True)

    async def shutdown(self):
        """Shut down agent gracefully."""
        self.logger.info("Shutting down agent...")

        await self.trigger_system.stop()
        await self.hub_connector.shutdown()

        self.logger.info("Agent shutdown complete")

    def run_sync(self):
        """
        Run agent synchronously (blocking).

        DESIGN: Convenience method for normal usage.
        Handles asyncio event loop setup.
        """
        try:
            asyncio.run(self.run())
        except KeyboardInterrupt:
            self.logger.info("Agent interrupted by user")
        except Exception as e:
            self.logger.error(f"Agent failed: {e}")
            raise

    def __repr__(self) -> str:
        return f"Agent({self.config.agent_id}, type={self.config.agent_type})"


if __name__ == "__main__":
    # Allow running as: python -m runtime.agent
    agent = Agent()
    agent.run_sync()
