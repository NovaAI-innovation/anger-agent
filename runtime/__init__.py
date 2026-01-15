"""
Agent Framework Runtime

A lightweight, configuration-driven agent system where behavior is defined
entirely through AGENTS.md (documentation) and config.yaml (specification).

Core Concept:
- Agents are instances of a universal template
- Configuration specifies identity, triggers, and behavior
- Workflows define step-by-step execution logic
- Tools are reusable capabilities agents can invoke
"""

__version__ = "0.1.0"
__author__ = "Agent Framework Team"

from runtime.agent import Agent

__all__ = ["Agent"]
