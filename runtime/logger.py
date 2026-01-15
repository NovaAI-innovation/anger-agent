"""
Structured logging for agents.

DESIGN REASONING:
- Uses JSON format for machine-parseable logs
- Includes context (agent_id, workflow, step) in every log
- Supports rotation to prevent disk bloat
- Structured fields enable filtering/searching
"""

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from pythonjsonlogger import jsonlogger


class StructuredFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds context to all logs.

    DESIGN: Ensures every log entry includes agent_id, timestamp, and context
    so that logs are easily queryable and correlated with specific events.
    """

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        # Ensure timestamp is always present
        log_record['timestamp'] = datetime.utcnow().isoformat()


def setup_logger(agent_id: str, log_file: str = None, log_level: str = "INFO") -> logging.Logger:
    """
    Set up structured logger for an agent.

    Args:
        agent_id: Name of the agent (for context)
        log_file: Path to log file (optional, defaults to console)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance

    DESIGN REASONING:
    - Creates logger once per agent (thread-safe)
    - Outputs both to console (for user visibility) and file (for audit)
    - JSON format for file (machine-parseable), readable for console
    - Structured fields include agent_id automatically
    """
    logger = logging.getLogger(agent_id)
    logger.setLevel(getattr(logging, log_level))

    # Create formatters
    json_formatter = StructuredFormatter(
        '%(timestamp)s %(level)s %(message)s %(agent_id)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (simple format for readability)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler (JSON format for parsing)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)

    # Add agent_id to all log records
    class AgentIdFilter(logging.Filter):
        def filter(self, record):
            record.agent_id = agent_id
            return True

    logger.addFilter(AgentIdFilter())

    return logger


def log_step_execution(logger: logging.Logger, step_id: str, action: str,
                      status: str, details: dict = None):
    """
    Log workflow step execution with consistent format.

    Args:
        logger: Logger instance
        step_id: Workflow step identifier
        action: Tool/action being executed
        status: Execution status (success, failed, skipped)
        details: Additional context dict

    DESIGN REASONING:
    - Consistent format across all step logs
    - Includes step_id, action, status for easy filtering
    - Details dict allows extensibility without changing format
    """
    message = f"Step[{step_id}] {action} → {status}"

    log_level = logging.WARNING if status == "failed" else logging.INFO

    extra = {"step": step_id, "action": action, "status": status}
    if details:
        extra.update(details)

    logger.log(log_level, message, extra=extra)


def log_workflow_execution(logger: logging.Logger, workflow_id: str,
                          trigger_event: str, status: str, duration_ms: float = None):
    """
    Log workflow execution summary.

    Args:
        logger: Logger instance
        workflow_id: Workflow identifier
        trigger_event: What triggered the workflow
        status: Overall status (success, failed)
        duration_ms: Execution time in milliseconds

    DESIGN REASONING:
    - Summary log at workflow level
    - Enables performance tracking (duration_ms)
    - Correlates trigger event with workflow execution
    """
    message = f"Workflow[{workflow_id}] triggered by {trigger_event} → {status}"
    if duration_ms:
        message += f" ({duration_ms:.2f}ms)"

    log_level = logging.WARNING if status == "failed" else logging.INFO

    extra = {
        "workflow": workflow_id,
        "trigger": trigger_event,
        "status": status,
        "duration_ms": duration_ms
    }

    logger.log(log_level, message, extra=extra)
