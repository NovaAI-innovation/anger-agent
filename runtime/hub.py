"""
Hub connector for agent communication.

DESIGN REASONING:
- v0.1: Stub implementation (validates config but doesn't connect)
- v0.5: Will implement actual WebSocket connection to hub
- Provides consistent interface for sending/receiving messages
- Async-ready for future integration
"""

import logging
from typing import Dict, Any, Optional
from runtime.config import Config


class HubConnector:
    """
    Stub connector to hub mesh.

    DESIGN: In v0.1, this is a no-op that logs messages.
    Future versions will:
    - Connect via WebSocket to hub
    - Send/receive messages from other agents
    - Support seed-phrase authentication
    """

    def __init__(self, config: Config, logger: logging.Logger):
        """
        Initialize hub connector.

        Args:
            config: Agent configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.connected = False

    async def initialize(self):
        """
        Initialize connection to hub.

        DESIGN: Currently a stub. In v0.5, will:
        - Read hub config (endpoint, seed_phrase)
        - Establish WebSocket connection
        - Authenticate with seed phrase
        - Set up message handlers
        """
        hub_config = self.config.hub_config

        if not hub_config.get("enabled", True):
            self.logger.info("Hub connector disabled in config")
            return

        self.logger.info("Hub connector initialized (stub - v0.5 will connect)")
        self.logger.debug(f"Hub config: {hub_config}")

        # v0.1: Just log that we're ready
        # v0.5: Will actually connect
        self.connected = False

    async def send_message(self, destination: str, message: Dict[str, Any]):
        """
        Send message to another agent.

        Args:
            destination: Target agent (e.g., "agent_b@hub_c")
            message: Message payload

        DESIGN: v0.1 just queues, v0.5 will send via WebSocket
        """
        self.logger.info(
            f"Message queued for hub (v0.5 will send): "
            f"to={destination}, message={message}"
        )

        # v0.1: Just log it
        # v0.5: Send via hub

    async def receive_messages(self):
        """
        Receive messages from hub.

        Returns:
            Async generator of messages

        DESIGN: v0.1 returns nothing, v0.5 will stream from WebSocket
        """
        # v0.1: No messages
        # v0.5: Will yield messages from hub
        return
        yield  # Make it a generator

    async def shutdown(self):
        """Shut down hub connection."""
        if self.connected:
            self.logger.info("Shutting down hub connection")
            self.connected = False

    def __repr__(self) -> str:
        return f"HubConnector(status={'connected' if self.connected else 'disconnected'})"
