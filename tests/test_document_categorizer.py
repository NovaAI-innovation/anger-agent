"""
Tests for the document_categorizer agent example.
Tests both the LLM tool and the workflow configuration.
"""

import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Setup path
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
sys.path.insert(0, project_root)

from runtime.config import Config
from runtime.tools import ToolRegistry


class TestLLMTool:
    """Test the mock LLM analyze tool."""

    def test_llm_analyze_tool_exists(self):
        """Test that llm.analyze tool is registered."""
        registry = ToolRegistry()
        assert registry.get_tool("llm.analyze") is not None

    def test_mock_llm_error_category(self):
        """Test mock LLM categorizes error keywords."""
        registry = ToolRegistry()
        tool = registry.get_tool("llm.analyze")

        result = {
            "text": "System error occurred: Database connection failed",
            "prompt": "Categorize this",
            "provider": "mock"
        }

        # Execute the function directly
        from runtime.tools import _tool_llm_analyze
        response = _tool_llm_analyze(result)

        assert response["category"] == "error"
        assert response["confidence"] >= 0.9
        assert "error" in str(response).lower() or response["category"] == "error"

    def test_mock_llm_success_category(self):
        """Test mock LLM categorizes success keywords."""
        from runtime.tools import _tool_llm_analyze

        result = _tool_llm_analyze({
            "text": "Task completed successfully. All validations passed.",
            "provider": "mock"
        })

        assert result["category"] == "success"
        assert result["confidence"] >= 0.9

    def test_mock_llm_warning_category(self):
        """Test mock LLM categorizes warning keywords."""
        from runtime.tools import _tool_llm_analyze

        result = _tool_llm_analyze({
            "text": "Please use caution. Attention needed for edge cases.",
            "provider": "mock"
        })

        assert result["category"] == "warning"
        assert result["confidence"] >= 0.8

    def test_mock_llm_info_category(self):
        """Test mock LLM categorizes info keywords."""
        from runtime.tools import _tool_llm_analyze

        result = _tool_llm_analyze({
            "text": "This is some informational notice to be aware of.",
            "provider": "mock"
        })

        assert result["category"] == "info"
        assert result["confidence"] >= 0.8

    def test_mock_llm_unknown_category(self):
        """Test mock LLM defaults to unknown for no matches."""
        from runtime.tools import _tool_llm_analyze

        result = _tool_llm_analyze({
            "text": "This is a neutral piece of text with no special keywords.",
            "provider": "mock"
        })

        assert result["category"] == "unknown"
        assert result["confidence"] < 0.7

    def test_mock_llm_returns_tags(self):
        """Test mock LLM returns tags."""
        from runtime.tools import _tool_llm_analyze

        result = _tool_llm_analyze({
            "text": "User account security permissions for database access control and authentication.",
            "provider": "mock"
        })

        assert "tags" in result
        assert len(result["tags"]) > 0
        assert "security-related" in result["tags"]

    def test_mock_llm_detailed_tag(self):
        """Test mock LLM adds detailed tag for long text."""
        from runtime.tools import _tool_llm_analyze

        long_text = " ".join(["word"] * 30)  # More than 100 chars
        result = _tool_llm_analyze({
            "text": long_text,
            "provider": "mock"
        })

        assert "detailed" in result["tags"]

    def test_mock_llm_structured_output(self):
        """Test mock LLM returns structured output."""
        from runtime.tools import _tool_llm_analyze

        result = _tool_llm_analyze({
            "text": "This is an error with a problem",
            "provider": "mock"
        })

        # Verify structure
        assert "category" in result
        assert "tags" in result
        assert "confidence" in result
        assert "summary" in result
        assert "analysis" in result

        # Verify analysis structure
        analysis = result["analysis"]
        assert "word_count" in analysis
        assert "character_count" in analysis
        assert "provider" in analysis
        assert "model" in analysis

    def test_llm_analyze_missing_text(self):
        """Test llm.analyze raises error without text parameter."""
        from runtime.tools import _tool_llm_analyze

        with pytest.raises(ValueError, match="Missing required parameter: text"):
            _tool_llm_analyze({"provider": "mock"})

    def test_llm_analyze_unsupported_provider(self):
        """Test llm.analyze raises error for unsupported provider."""
        from runtime.tools import _tool_llm_analyze

        with pytest.raises(ValueError, match="Unknown provider"):
            _tool_llm_analyze({
                "text": "Some text",
                "provider": "unsupported"
            })

    @patch('runtime.tools.OpenAI')
    def test_openai_llm_analyze_success(self, mock_openai_class):
        """Test OpenAI provider with successful response."""
        from runtime.tools import _tool_llm_analyze

        # Mock the OpenAI client and response
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "category": "error",
            "tags": ["system", "critical"],
            "confidence": 0.95,
            "summary": "Critical system error detected"
        })

        mock_client.chat.completions.create.return_value = mock_response

        # Set API key in environment
        os.environ["OPENAI_API_KEY"] = "test-key-12345"

        try:
            result = _tool_llm_analyze({
                "text": "System error occurred: Database connection failed",
                "provider": "openai",
                "model": "gpt-4"
            })

            # Verify response structure
            assert result["category"] == "error"
            assert result["confidence"] == 0.95
            assert "system" in result["tags"]
            assert result["analysis"]["provider"] == "openai"
            assert result["analysis"]["model"] == "gpt-4"
        finally:
            os.environ.pop("OPENAI_API_KEY", None)

    @patch('runtime.tools.OpenAI')
    def test_openai_llm_analyze_missing_api_key(self, mock_openai_class):
        """Test OpenAI provider raises error without API key."""
        from runtime.tools import _tool_llm_analyze

        # Ensure API key is not set
        os.environ.pop("OPENAI_API_KEY", None)

        with pytest.raises(ValueError, match="API key not provided"):
            _tool_llm_analyze({
                "text": "Some text",
                "provider": "openai"
            })

    @patch('runtime.tools.OpenAI')
    def test_openai_llm_analyze_parse_json_from_markdown(self, mock_openai_class):
        """Test OpenAI provider can extract JSON from markdown response."""
        from runtime.tools import _tool_llm_analyze

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Response wrapped in markdown code blocks
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """```json
{
  "category": "success",
  "tags": ["completed"],
  "confidence": 0.92
}
```"""

        mock_client.chat.completions.create.return_value = mock_response
        os.environ["OPENAI_API_KEY"] = "test-key"

        try:
            result = _tool_llm_analyze({
                "text": "Task completed successfully",
                "provider": "openai"
            })

            assert result["category"] == "success"
            assert result["confidence"] == 0.92
        finally:
            os.environ.pop("OPENAI_API_KEY", None)

    @patch('runtime.tools.OpenAI')
    def test_openai_llm_analyze_response_validation(self, mock_openai_class):
        """Test OpenAI provider validates and normalizes response."""
        from runtime.tools import _tool_llm_analyze

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Response with invalid category (should be normalized)
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "category": "invalid_category",
            "tags": "single_tag",  # Should be converted to list
            "confidence": 1.5  # Should be clamped to 1.0
        })

        mock_client.chat.completions.create.return_value = mock_response
        os.environ["OPENAI_API_KEY"] = "test-key"

        try:
            result = _tool_llm_analyze({
                "text": "Some text",
                "provider": "openai"
            })

            # Verify normalization
            assert result["category"] == "unknown"  # Invalid category becomes unknown
            assert isinstance(result["tags"], list)
            assert result["confidence"] == 1.0  # Clamped to max
        finally:
            os.environ.pop("OPENAI_API_KEY", None)

    @patch('runtime.tools.Anthropic')
    def test_claude_llm_analyze_success(self, mock_anthropic_class):
        """Test Claude provider with successful response."""
        from runtime.tools import _tool_llm_analyze

        # Mock the Anthropic client and response
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = json.dumps({
            "category": "success",
            "tags": ["completed", "verified"],
            "confidence": 0.93,
            "summary": "Task completed successfully"
        })

        mock_client.messages.create.return_value = mock_response

        # Set API key in environment
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"

        try:
            result = _tool_llm_analyze({
                "text": "Task completed successfully with all tests passing",
                "provider": "claude",
                "model": "claude-3-sonnet-20240229"
            })

            # Verify response structure
            assert result["category"] == "success"
            assert result["confidence"] == 0.93
            assert "completed" in result["tags"]
            assert result["analysis"]["provider"] == "claude"
            assert "claude" in result["analysis"]["model"]
        finally:
            os.environ.pop("ANTHROPIC_API_KEY", None)

    @patch('runtime.tools.Anthropic')
    def test_claude_llm_analyze_missing_api_key(self, mock_anthropic_class):
        """Test Claude provider raises error without API key."""
        from runtime.tools import _tool_llm_analyze

        # Ensure API key is not set
        os.environ.pop("ANTHROPIC_API_KEY", None)

        with pytest.raises(ValueError, match="API key not provided"):
            _tool_llm_analyze({
                "text": "Some text",
                "provider": "claude"
            })

    def test_provider_factory_mock(self):
        """Test provider factory returns mock provider."""
        from runtime.tools import get_llm_provider

        provider = get_llm_provider("mock")
        assert provider is not None
        assert provider.__class__.__name__ == "MockLLMProvider"

    @patch('runtime.tools.OpenAI')
    def test_provider_factory_openai(self, mock_openai_class):
        """Test provider factory returns OpenAI provider."""
        from runtime.tools import get_llm_provider

        provider = get_llm_provider("openai")
        assert provider is not None
        assert provider.__class__.__name__ == "OpenAIProvider"

    @patch('runtime.tools.Anthropic')
    def test_provider_factory_claude(self, mock_anthropic_class):
        """Test provider factory returns Claude provider."""
        from runtime.tools import get_llm_provider

        provider = get_llm_provider("claude")
        assert provider is not None
        assert provider.__class__.__name__ == "ClaudeProvider"

    def test_provider_factory_invalid(self):
        """Test provider factory raises error for unknown provider."""
        from runtime.tools import get_llm_provider

        with pytest.raises(ValueError, match="Unknown provider"):
            get_llm_provider("unknown_provider")

    def test_provider_factory_case_insensitive(self):
        """Test provider factory is case insensitive."""
        from runtime.tools import get_llm_provider

        provider1 = get_llm_provider("MOCK")
        provider2 = get_llm_provider("Mock")
        provider3 = get_llm_provider("mock")

        assert provider1.__class__ == provider2.__class__ == provider3.__class__

    @patch('runtime.tools.OpenAI')
    @patch('runtime.tools.Anthropic')
    def test_provider_switching(self, mock_anthropic_class, mock_openai_class):
        """Test that same workflow works with different providers."""
        from runtime.tools import _tool_llm_analyze

        test_text = "This is a system error that needs attention"

        # Mock OpenAI
        mock_openai_client = MagicMock()
        mock_openai_class.return_value = mock_openai_client
        openai_response = MagicMock()
        openai_response.choices = [MagicMock()]
        openai_response.choices[0].message.content = json.dumps({
            "category": "error",
            "tags": ["system"],
            "confidence": 0.95
        })
        mock_openai_client.chat.completions.create.return_value = openai_response

        # Mock Claude
        mock_anthropic_client = MagicMock()
        mock_anthropic_class.return_value = mock_anthropic_client
        anthropic_response = MagicMock()
        anthropic_response.content = [MagicMock()]
        anthropic_response.content[0].text = json.dumps({
            "category": "error",
            "tags": ["system"],
            "confidence": 0.96
        })
        mock_anthropic_client.messages.create.return_value = anthropic_response

        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ["ANTHROPIC_API_KEY"] = "test-key"

        try:
            # Test with mock
            mock_result = _tool_llm_analyze({
                "text": test_text,
                "provider": "mock"
            })
            assert mock_result["category"] == "error"
            assert mock_result["analysis"]["provider"] == "mock"

            # Test with OpenAI
            openai_result = _tool_llm_analyze({
                "text": test_text,
                "provider": "openai"
            })
            assert openai_result["category"] == "error"
            assert openai_result["analysis"]["provider"] == "openai"

            # Test with Claude
            claude_result = _tool_llm_analyze({
                "text": test_text,
                "provider": "claude"
            })
            assert claude_result["category"] == "error"
            assert claude_result["analysis"]["provider"] == "claude"
        finally:
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("ANTHROPIC_API_KEY", None)


class TestDocumentCategorizerConfig:
    """Test the document_categorizer agent configuration."""

    def test_document_categorizer_config_loads(self):
        """Test that document_categorizer config loads correctly."""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        config_path = framework_root / "agents/examples/document_categorizer/config.yaml"

        if not config_path.exists():
            pytest.skip(f"document_categorizer example not found at {config_path}")

        # Set required environment variables
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["INBOX_PATH"] = tmpdir
            os.environ["ERRORS_PATH"] = os.path.join(tmpdir, "errors")
            os.environ["PROCESSED_PATH"] = os.path.join(tmpdir, "processed")
            os.environ["REVIEW_PATH"] = os.path.join(tmpdir, "review")

            try:
                config = Config(str(config_path))

                assert config.agent_id == "document_categorizer"
                assert config.agent_type == "task_executor"
            finally:
                # Clean up environment variables
                for var in ["INBOX_PATH", "ERRORS_PATH", "PROCESSED_PATH", "REVIEW_PATH"]:
                    os.environ.pop(var, None)

    def test_document_categorizer_has_workflow(self):
        """Test that document_categorizer has categorize_and_route workflow."""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        config_path = framework_root / "agents/examples/document_categorizer/config.yaml"

        if not config_path.exists():
            pytest.skip(f"document_categorizer example not found at {config_path}")

        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["INBOX_PATH"] = tmpdir
            os.environ["ERRORS_PATH"] = os.path.join(tmpdir, "errors")
            os.environ["PROCESSED_PATH"] = os.path.join(tmpdir, "processed")
            os.environ["REVIEW_PATH"] = os.path.join(tmpdir, "review")

            try:
                config = Config(str(config_path))

                assert "categorize_and_route" in config.workflows
                workflow = config.workflows["categorize_and_route"]

                # Verify workflow has all expected steps
                step_ids = [step["id"] for step in workflow["steps"]]
                assert "read_document" in step_ids
                assert "analyze_content" in step_ids
                assert "create_metadata" in step_ids
                assert "route_by_category" in step_ids
            finally:
                for var in ["INBOX_PATH", "ERRORS_PATH", "PROCESSED_PATH", "REVIEW_PATH"]:
                    os.environ.pop(var, None)

    def test_document_categorizer_llm_step(self):
        """Test that workflow includes llm.analyze step with mock provider."""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        config_path = framework_root / "agents/examples/document_categorizer/config.yaml"

        if not config_path.exists():
            pytest.skip(f"document_categorizer example not found at {config_path}")

        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["INBOX_PATH"] = tmpdir
            os.environ["ERRORS_PATH"] = os.path.join(tmpdir, "errors")
            os.environ["PROCESSED_PATH"] = os.path.join(tmpdir, "processed")
            os.environ["REVIEW_PATH"] = os.path.join(tmpdir, "review")

            try:
                config = Config(str(config_path))
                workflow = config.workflows["categorize_and_route"]

                # Find the analyze_content step
                analyze_step = None
                for step in workflow["steps"]:
                    if step["id"] == "analyze_content":
                        analyze_step = step
                        break

                assert analyze_step is not None
                assert analyze_step["action"] == "llm.analyze"
                assert analyze_step["params"]["provider"] == "mock"
                assert "text" in analyze_step["params"]
            finally:
                for var in ["INBOX_PATH", "ERRORS_PATH", "PROCESSED_PATH", "REVIEW_PATH"]:
                    os.environ.pop(var, None)

    def test_document_categorizer_conditional_routing(self):
        """Test that workflow has conditional routing logic."""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        config_path = framework_root / "agents/examples/document_categorizer/config.yaml"

        if not config_path.exists():
            pytest.skip(f"document_categorizer example not found at {config_path}")

        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["INBOX_PATH"] = tmpdir
            os.environ["ERRORS_PATH"] = os.path.join(tmpdir, "errors")
            os.environ["PROCESSED_PATH"] = os.path.join(tmpdir, "processed")
            os.environ["REVIEW_PATH"] = os.path.join(tmpdir, "review")

            try:
                config = Config(str(config_path))
                workflow = config.workflows["categorize_and_route"]

                # Find the routing conditional step
                route_step = None
                for step in workflow["steps"]:
                    if step["id"] == "route_by_category":
                        route_step = step
                        break

                assert route_step is not None
                assert route_step["action"] == "conditional"
                assert "if_true" in route_step
                assert "if_false" in route_step

                # Verify nested conditional
                if_false_steps = route_step["if_false"]
                check_success_step = None
                for step in if_false_steps:
                    if step["id"] == "check_success":
                        check_success_step = step
                        break

                assert check_success_step is not None
                assert check_success_step["action"] == "conditional"
            finally:
                for var in ["INBOX_PATH", "ERRORS_PATH", "PROCESSED_PATH", "REVIEW_PATH"]:
                    os.environ.pop(var, None)

    def test_document_categorizer_schema_exists(self):
        """Test that document_categorizer schema file exists."""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        schema_path = framework_root / "agents/examples/document_categorizer/schema.json"

        if not schema_path.exists():
            pytest.skip(f"document_categorizer schema not found at {schema_path}")

        # Load and validate schema JSON
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "filename" in schema["properties"]
        assert "category" in schema["properties"]
        assert "tags" in schema["properties"]
        assert "confidence" in schema["properties"]

    def test_document_categorizer_agents_md_exists(self):
        """Test that AGENTS.md exists and is readable."""
        test_dir = Path(__file__).parent
        framework_root = test_dir.parent
        agents_md_path = framework_root / "agents/examples/document_categorizer/AGENTS.md"

        if not agents_md_path.exists():
            pytest.skip(f"document_categorizer AGENTS.md not found at {agents_md_path}")

        # Read and verify content
        with open(agents_md_path, 'r') as f:
            content = f.read()

        assert "Document Categorizer" in content
        assert "mock" in content.lower()
        assert "configuration" in content.lower()
