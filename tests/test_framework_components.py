"""
Tests for the core agent framework components.
"""

import pytest
import tempfile
import json
from pathlib import Path

# Import agent components
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, project_root)

from runtime.config import Config, ConfigError


class TestWorkflowDesign:
    """Test that workflow configurations are valid and executable"""

    def test_workflow_structure(self):
        """Test that workflow has correct structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"

workflows:
  simple_workflow:
    steps:
      - id: "step1"
        action: "log"
        params:
          message: "Hello"

tools:
  - name: "log"
    enabled: true

logging:
  level: "info"
""")
            config = Config(str(config_path))

            # Verify workflow exists
            assert "simple_workflow" in config.workflows

            # Verify steps
            workflow = config.workflows["simple_workflow"]
            assert len(workflow["steps"]) == 1
            assert workflow["steps"][0]["action"] == "log"

    def test_conditional_workflow(self):
        """Test conditional branching in workflows"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"

workflows:
  conditional_flow:
    steps:
      - id: "check"
        action: "conditional"
        condition: "${result.valid} == true"
        if_true:
          - id: "success"
            action: "log"
            params:
              message: "Valid!"
        if_false:
          - id: "failure"
            action: "log"
            params:
              message: "Invalid!"

tools:
  - name: "log"
    enabled: true

logging:
  level: "info"
""")
            config = Config(str(config_path))

            # Verify conditional step
            workflow = config.workflows["conditional_flow"]
            conditional_step = workflow["steps"][0]

            assert conditional_step["action"] == "conditional"
            assert "if_true" in conditional_step
            assert "if_false" in conditional_step
            assert len(conditional_step["if_true"]) == 1
            assert len(conditional_step["if_false"]) == 1

    def test_variable_interpolation_syntax(self):
        """Test that variable placeholders are preserved"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"

workflows:
  var_workflow:
    steps:
      - id: "read"
        action: "file.read"
        params:
          path: "${trigger.file_path}"

tools:
  - name: "file.read"
    enabled: true

logging:
  level: "info"
""")
            config = Config(str(config_path))

            # Verify placeholders are preserved (not interpolated at load time)
            workflow = config.workflows["var_workflow"]
            step = workflow["steps"][0]

            # Should preserve runtime placeholders
            assert "${trigger.file_path}" in step["params"]["path"]


class TestAgentConfiguration:
    """Test agent configuration loading and validation"""

    def test_minimal_valid_config(self):
        """Test minimal valid configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "minimal"
agent_type: "task_executor"
""")
            config = Config(str(config_path))

            assert config.agent_id == "minimal"
            assert config.agent_type == "task_executor"

    def test_missing_agent_id(self):
        """Test error on missing agent_id"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_type: "task_executor"
""")
            with pytest.raises(ConfigError, match="agent_id"):
                Config(str(config_path))

    def test_missing_agent_type(self):
        """Test error on missing agent_type"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
""")
            with pytest.raises(ConfigError, match="agent_type"):
                Config(str(config_path))

    def test_invalid_agent_type(self):
        """Test error on invalid agent_type"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "unknown_type"
""")
            with pytest.raises(ConfigError, match="Invalid agent_type"):
                Config(str(config_path))

    def test_metadata_section(self):
        """Test that metadata is preserved"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"

metadata:
  version: "1.0"
  description: "Test agent"
  author: "Test User"
""")
            config = Config(str(config_path))

            metadata = config.config_data.get("metadata", {})
            assert metadata["version"] == "1.0"
            assert metadata["description"] == "Test agent"

    def test_trigger_configuration(self):
        """Test trigger configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"

triggers:
  - id: "file_trigger"
    type: "file_watch"
    path: "/tmp/inbox"
    patterns: ["*.json"]
    workflow_id: "process"
""")
            config = Config(str(config_path))

            assert len(config.triggers) == 1
            trigger = config.triggers[0]
            assert trigger["id"] == "file_trigger"
            assert trigger["type"] == "file_watch"
            assert trigger["path"] == "/tmp/inbox"
            assert trigger["patterns"] == ["*.json"]

    def test_tools_configuration(self):
        """Test tool configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"

tools:
  - name: "file.read"
    enabled: true
  - name: "file.write"
    enabled: true
  - name: "json.validate"
    enabled: true
""")
            config = Config(str(config_path))

            assert len(config.tools) == 3
            tool_names = [t["name"] for t in config.tools]
            assert "file.read" in tool_names
            assert "file.write" in tool_names
            assert "json.validate" in tool_names

    def test_logging_configuration(self):
        """Test logging configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"

logging:
  level: "debug"
  file: "/tmp/test.log"
  format: "json"
""")
            config = Config(str(config_path))

            log_config = config.logging_config
            assert log_config["level"] == "debug"
            assert log_config["file"] == "/tmp/test.log"
            assert log_config["format"] == "json"

    def test_logging_defaults(self):
        """Test logging configuration defaults"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("""
agent_id: "test"
agent_type: "task_executor"
""")
            config = Config(str(config_path))

            log_config = config.logging_config
            assert "level" in log_config
            assert log_config["level"] == "info"


class TestFileValidatorConfiguration:
    """Test the specific file_validator example configuration"""

    def test_file_validator_config_loads(self):
        """Test that the file_validator example config loads correctly"""
        # Find the actual file_validator config
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        config_path = framework_root / "agents/examples/file_validator/config.yaml"

        if not config_path.exists():
            pytest.skip(f"file_validator example not found at {config_path}")

        # Set required environment variables
        os.environ["INBOX_PATH"] = "/tmp/agent_inbox"
        os.environ["PROCESSED_PATH"] = "/tmp/agent_processed"
        os.environ["ERRORS_PATH"] = "/tmp/agent_errors"
        os.environ["SCHEMA_PATH"] = "./schema.json"

        try:
            config = Config(str(config_path))

            assert config.agent_id == "file_validator"
            assert config.agent_type == "task_executor"
        finally:
            # Clean up environment variables
            for var in ["INBOX_PATH", "PROCESSED_PATH", "ERRORS_PATH", "SCHEMA_PATH"]:
                os.environ.pop(var, None)

    def test_file_validator_has_validate_workflow(self):
        """Test that file_validator has validation workflow"""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        config_path = framework_root / "agents/examples/file_validator/config.yaml"

        if not config_path.exists():
            pytest.skip(f"file_validator example not found at {config_path}")

        # Set required environment variables
        os.environ["INBOX_PATH"] = "/tmp/agent_inbox"
        os.environ["PROCESSED_PATH"] = "/tmp/agent_processed"
        os.environ["ERRORS_PATH"] = "/tmp/agent_errors"
        os.environ["SCHEMA_PATH"] = "./schema.json"

        try:
            config = Config(str(config_path))

            assert "validate_and_process" in config.workflows
            workflow = config.workflows["validate_and_process"]

            # Check for key steps
            step_ids = [step["id"] for step in workflow["steps"]]
            assert "read_file" in step_ids
            assert "parse_json" in step_ids
            assert "validate" in step_ids
            assert "check_validation" in step_ids
        finally:
            # Clean up environment variables
            for var in ["INBOX_PATH", "PROCESSED_PATH", "ERRORS_PATH", "SCHEMA_PATH"]:
                os.environ.pop(var, None)

    def test_file_validator_schema_exists(self):
        """Test that file_validator schema file exists"""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        schema_path = framework_root / "agents/examples/file_validator/schema.json"

        if not schema_path.exists():
            pytest.skip(f"file_validator schema not found at {schema_path}")

        # Load and validate schema JSON
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "id" in schema["required"]
        assert "name" in schema["required"]
        assert "email" in schema["required"]
