"""
Configuration loading and validation.

DESIGN REASONING:
- Loads both config.yaml (behavior) and AGENTS.md (documentation)
- Validates config against schema
- Interpolates environment variables
- Provides clean API for accessing config values
- Fails fast with helpful error messages
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class ConfigError(Exception):
    """Raised when config is invalid or missing"""
    pass


class Config:
    """
    Encapsulates agent configuration loaded from config.yaml and AGENTS.md.

    DESIGN: Single source of truth for agent configuration.
    Provides type-safe access to config values with sensible defaults.
    """

    def __init__(self, config_path: str, agents_md_path: Optional[str] = None):
        """
        Load and validate configuration.

        Args:
            config_path: Path to config.yaml
            agents_md_path: Path to AGENTS.md (optional)

        Raises:
            ConfigError: If config is invalid or missing
        """
        self.config_path = Path(config_path)
        self.agents_md_path = Path(agents_md_path) if agents_md_path else self.config_path.parent / "AGENTS.md"

        # Load and validate
        self.config_data = self._load_yaml(self.config_path)
        self.agents_md_content = self._load_agents_md()

        # Validate structure
        self._validate_config()

        # Interpolate environment variables
        self._interpolate_environment_variables()

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file and handle errors gracefully."""
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")

        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise ConfigError(f"Config must be a YAML object, got {type(data)}")
            return data
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in {path}: {e}")

    def _load_agents_md(self) -> str:
        """Load AGENTS.md documentation (optional)."""
        if self.agents_md_path.exists():
            with open(self.agents_md_path, 'r') as f:
                return f.read()
        return ""

    def _validate_config(self):
        """
        Validate config structure.

        DESIGN REASONING:
        - Fail fast with helpful error messages
        - Validate required fields at load time
        - Allow optional fields with defaults
        """
        required_fields = ["agent_id", "agent_type"]
        for field in required_fields:
            if field not in self.config_data:
                raise ConfigError(f"Missing required field: {field}")

        valid_types = ["task_executor", "llm_inference", "hybrid", "mcp_tool_server"]
        if self.config_data["agent_type"] not in valid_types:
            raise ConfigError(
                f"Invalid agent_type: {self.config_data['agent_type']}. "
                f"Must be one of: {', '.join(valid_types)}"
            )

    def _interpolate_environment_variables(self):
        """
        Replace ${ENV_VAR} with actual environment variable values.

        DESIGN REASONING:
        - Allows secrets/paths to be passed at runtime
        - Only interpolates OS environment variables at load time
        - Preserves runtime placeholders (${trigger.*}, ${step.*}) for workflow execution
        - Fails with helpful error if var not found
        """
        def replace_env_vars(obj):
            if isinstance(obj, str):
                # Find all ${VAR_NAME} patterns
                import re
                pattern = r'\$\{([^}]+)\}'

                def replacer(match):
                    var_name = match.group(1)

                    # Only interpolate UPPERCASE variables (OS environment variable convention)
                    # Skip everything else - lowercase/mixed case are runtime placeholders:
                    # - ${file_content}, ${parsed_data}, etc. are step outputs
                    # - ${trigger.*}, ${step.*}, etc. are runtime context
                    # These are all interpolated during workflow execution, not at config load time
                    if not var_name.isupper():
                        return match.group(0)  # Return unchanged

                    # Interpolate UPPERCASE OS environment variables
                    if var_name not in os.environ:
                        raise ConfigError(
                            f"Environment variable not set: {var_name}. "
                            f"Set it with: export {var_name}=value"
                        )
                    return os.environ[var_name]

                return re.sub(pattern, replacer, obj)
            elif isinstance(obj, dict):
                return {k: replace_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_env_vars(item) for item in obj]
            else:
                return obj

        self.config_data = replace_env_vars(self.config_data)

    # Accessor methods

    @property
    def agent_id(self) -> str:
        """Agent identifier"""
        return self.config_data["agent_id"]

    @property
    def agent_type(self) -> str:
        """Agent type (task_executor, llm_inference, hybrid, mcp_tool_server)"""
        return self.config_data["agent_type"]

    @property
    def triggers(self) -> list:
        """List of triggers"""
        return self.config_data.get("triggers", [])

    @property
    def workflows(self) -> Dict[str, Dict]:
        """Dictionary of workflows"""
        return self.config_data.get("workflows", {})

    @property
    def tools(self) -> list:
        """List of enabled tools"""
        return self.config_data.get("tools", [])

    @property
    def environment(self) -> Dict[str, str]:
        """Environment variables section"""
        return self.config_data.get("environment", {})

    @property
    def logging_config(self) -> Dict:
        """Logging configuration"""
        return self.config_data.get("logging", {
            "level": "info",
            "format": "json"
        })

    @property
    def hub_config(self) -> Dict:
        """Hub connectivity configuration"""
        return self.config_data.get("hub", {})

    def get(self, key: str, default: Any = None) -> Any:
        """Get arbitrary config value"""
        keys = key.split(".")
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default

    def __repr__(self) -> str:
        return f"Config(agent_id={self.agent_id}, type={self.agent_type})"
