"""
Tests for configuration loading and validation.

Tests that:
- Config loads correctly from YAML
- Validation catches missing required fields
- Environment variable interpolation works
- Config accessors return correct values
"""

import pytest
import tempfile
import os
from pathlib import Path
from runtime.config import Config, ConfigError


class TestConfigLoading:
    """Test loading and parsing config.yaml"""

    def test_load_valid_config(self):
        """Test loading a valid config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "task_executor"
triggers:
  - id: "test_trigger"
    type: "file_watch"
    path: "/tmp"
workflows:
  test_workflow:
    steps:
      - id: "step1"
        action: "log"
""")
            config = Config(str(config_path))
            assert config.agent_id == "test_agent"
            assert config.agent_type == "task_executor"

    def test_missing_agent_id(self):
        """Test that missing agent_id raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_type: "task_executor"
""")
            with pytest.raises(ConfigError, match="agent_id"):
                Config(str(config_path))

    def test_missing_agent_type(self):
        """Test that missing agent_type raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
""")
            with pytest.raises(ConfigError, match="agent_type"):
                Config(str(config_path))

    def test_invalid_agent_type(self):
        """Test that invalid agent_type raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "invalid_type"
""")
            with pytest.raises(ConfigError, match="Invalid agent_type"):
                Config(str(config_path))

    def test_file_not_found(self):
        """Test that missing config file raises error"""
        with pytest.raises(ConfigError, match="not found"):
            Config("/nonexistent/path.yaml")


class TestEnvironmentVariableInterpolation:
    """Test ${VAR} interpolation with environment variables"""

    def test_simple_env_var(self):
        """Test simple environment variable interpolation"""
        os.environ["TEST_VAR"] = "test_value"
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "task_executor"
environment:
  MY_PATH: "${TEST_VAR}"
""")
            config = Config(str(config_path))
            assert config.environment["MY_PATH"] == "test_value"

    def test_missing_env_var(self):
        """Test that missing environment variable raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "task_executor"
environment:
  MY_PATH: "${NONEXISTENT_VAR}"
""")
            with pytest.raises(ConfigError, match="NONEXISTENT_VAR"):
                Config(str(config_path))

    def test_nested_interpolation(self):
        """Test environment variable in nested structures"""
        os.environ["TEST_PATH"] = "/tmp/test"
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "task_executor"
triggers:
  - id: "watch"
    type: "file_watch"
    path: "${TEST_PATH}"
""")
            config = Config(str(config_path))
            assert config.triggers[0]["path"] == "/tmp/test"


class TestConfigAccessors:
    """Test config accessor methods"""

    def get_test_config(self):
        """Create a test config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "task_executor"
triggers:
  - id: "trigger1"
    type: "file_watch"
workflows:
  workflow1:
    steps:
      - id: "step1"
tools:
  - name: "file.read"
    enabled: true
logging:
  level: "debug"
  file: "/tmp/test.log"
""")
            return Config(str(config_path))

    def test_agent_id_property(self):
        """Test agent_id property"""
        config = self.get_test_config()
        assert config.agent_id == "test_agent"

    def test_agent_type_property(self):
        """Test agent_type property"""
        config = self.get_test_config()
        assert config.agent_type == "task_executor"

    def test_triggers_property(self):
        """Test triggers property"""
        config = self.get_test_config()
        triggers = config.triggers
        assert len(triggers) == 1
        assert triggers[0]["id"] == "trigger1"

    def test_workflows_property(self):
        """Test workflows property"""
        config = self.get_test_config()
        workflows = config.workflows
        assert "workflow1" in workflows

    def test_tools_property(self):
        """Test tools property"""
        config = self.get_test_config()
        tools = config.tools
        assert len(tools) == 1
        assert tools[0]["name"] == "file.read"

    def test_logging_config_property(self):
        """Test logging_config property"""
        config = self.get_test_config()
        log_config = config.logging_config
        assert log_config["level"] == "debug"
        assert log_config["file"] == "/tmp/test.log"

    def test_get_method(self):
        """Test get() method for arbitrary keys"""
        config = self.get_test_config()
        assert config.get("agent_id") == "test_agent"
        assert config.get("nonexistent", "default") == "default"


class TestAGENTSMDLoading:
    """Test AGENTS.md loading"""

    def test_load_agents_md(self):
        """Test that AGENTS.md is loaded if present"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "task_executor"
""")
            agents_md_path = Path(tmpdir) / "AGENTS.md"
            agents_md_path.write_text("# Test Agent\n\nThis is a test agent.")

            config = Config(str(config_path), str(agents_md_path))
            assert "Test Agent" in config.agents_md_content

    def test_agents_md_optional(self):
        """Test that AGENTS.md is optional"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test_agent"
agent_type: "task_executor"
""")
            config = Config(str(config_path))
            assert config.agents_md_content == ""
