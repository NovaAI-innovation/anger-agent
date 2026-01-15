"""
Tool system for agent execution.

DESIGN REASONING:
- Tools are reusable, self-contained capabilities
- Built-in tools cover 80% of common operations (file, JSON, logging)
- Custom tools can be added by users
- Consistent interface makes tools composable
- Tools are stateless (same input = same output)
"""

import os
import json
import shutil
import re
from pathlib import Path
from typing import Any, Dict, Callable, Optional
import logging

# Optional LLM provider imports
try:
    from openai import OpenAI, APIError, RateLimitError, APIConnectionError
except ImportError:
    OpenAI = None
    APIError = Exception
    RateLimitError = Exception
    APIConnectionError = Exception

try:
    from anthropic import Anthropic, APIError as AnthropicAPIError
except ImportError:
    Anthropic = None
    AnthropicAPIError = Exception


class Tool:
    """
    Base class for tools.

    DESIGN: Tools are simple functions with schema metadata.
    This allows both code-based execution and LLM tool-calling.
    """

    def __init__(self, name: str, description: str, func: Callable):
        """
        Initialize a tool.

        Args:
            name: Tool identifier (e.g., 'file.read')
            description: Human-readable description
            func: Callable that executes the tool
        """
        self.name = name
        self.description = description
        self.func = func

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            params: Input parameters

        Returns:
            Result dict with success/failure and output

        DESIGN REASONING:
        - Always returns consistent structure
        - Success indicated by 'success' field
        - Errors include 'error' field for debugging
        - Can be awaited (ready for async tools)
        """
        try:
            result = self.func(params)
            return {
                "success": True,
                "output": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def __repr__(self) -> str:
        return f"Tool({self.name})"


class ToolRegistry:
    """
    Registry of available tools.

    DESIGN: Centralized tool management.
    Allows discovery, execution, and custom tool registration.
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register all built-in tools."""
        # File tools
        self.register("file.read", "Read file contents", _tool_file_read)
        self.register("file.write", "Write content to file", _tool_file_write)
        self.register("file.move", "Move or copy file", _tool_file_move)
        self.register("file.find", "Find files matching pattern", _tool_file_find)

        # JSON tools
        self.register("json.parse", "Parse JSON string", _tool_json_parse)
        self.register("json.validate", "Validate JSON against schema", _tool_json_validate)
        self.register("json.stringify", "Convert object to JSON string", _tool_json_stringify)

        # LLM tools
        self.register("llm.analyze", "Analyze text using LLM (mock or real)", _tool_llm_analyze)

        # Message tools
        self.register("message.send", "Send message to agent", _tool_message_send)

        # Logging tools
        self.register("log", "Write to log", _tool_log)

    def register(self, name: str, description: str, func: Callable):
        """Register a new tool."""
        self.tools[name] = Tool(name, description, func)

    async def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a registered tool.

        Args:
            tool_name: Name of tool to execute
            params: Input parameters

        Returns:
            Result dict from tool

        Raises:
            KeyError: If tool not found
        """
        if tool_name not in self.tools:
            raise KeyError(f"Tool not found: {tool_name}")

        tool = self.tools[tool_name]
        return await tool.execute(params)

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> list:
        """List all registered tools."""
        return list(self.tools.values())

    def __repr__(self) -> str:
        return f"ToolRegistry({len(self.tools)} tools)"


# =============================================================================
# LLM Provider Abstraction
# =============================================================================

class LLMProvider:
    """
    Base class for LLM providers.

    DESIGN REASONING:
    - Provides consistent interface for different LLM services
    - Allows swapping providers via configuration
    - Each provider normalizes output to same structure
    - v0.3: Provider-agnostic LLM tool
    """

    def analyze(self, text: str, prompt: str, params: Dict[str, Any]) -> Dict:
        """
        Analyze text and return structured result.

        Args:
            text: Text to analyze
            prompt: Prompt for the LLM
            params: Additional provider-specific parameters

        Returns:
            Dict with keys: category, tags, confidence, summary, analysis
        """
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for deterministic testing."""

    def analyze(self, text: str, prompt: str, params: Dict[str, Any]) -> Dict:
        """Analyze using keyword-based mock categorization."""
        return _mock_llm_analyze(text, prompt)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT models provider."""

    def analyze(self, text: str, prompt: str, params: Dict[str, Any]) -> Dict:
        """Analyze using OpenAI API."""
        return _openai_llm_analyze(text, prompt, params)


class ClaudeProvider(LLMProvider):
    """Anthropic Claude models provider."""

    def analyze(self, text: str, prompt: str, params: Dict[str, Any]) -> Dict:
        """Analyze using Claude API."""
        return _claude_llm_analyze(text, prompt, params)


def get_llm_provider(provider_name: str) -> LLMProvider:
    """
    Factory function to get LLM provider by name.

    Supported providers:
    - "mock": Keyword-based mock (deterministic, no API needed)
    - "openai": OpenAI GPT models (requires openai SDK)
    - "claude": Anthropic Claude models (requires anthropic SDK)

    Args:
        provider_name: Name of the provider

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider not supported or SDK not installed
    """
    provider_name = (provider_name or "mock").lower().strip()

    if provider_name == "mock":
        return MockLLMProvider()
    elif provider_name == "openai":
        if OpenAI is None:
            raise ImportError("OpenAI SDK not installed. Run: pip install openai")
        return OpenAIProvider()
    elif provider_name == "claude":
        if Anthropic is None:
            raise ImportError("Anthropic SDK not installed. Run: pip install anthropic")
        return ClaudeProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Supported: mock, openai, claude")


# =============================================================================
# Built-in Tool Implementations
# =============================================================================

def _tool_file_read(params: Dict[str, Any]) -> str:
    """Read file and return contents as string."""
    path = params.get("path")
    if not path:
        raise ValueError("Missing required parameter: path")

    with open(path, 'r') as f:
        return f.read()


def _tool_file_write(params: Dict[str, Any]) -> Dict:
    """Write content to file."""
    path = params.get("path")
    content = params.get("content")

    if not path or content is None:
        raise ValueError("Missing required parameters: path, content")

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        f.write(content)

    return {"written_bytes": len(content)}


def _tool_file_move(params: Dict[str, Any]) -> Dict:
    """Move file from source to destination."""
    source = params.get("source")
    dest = params.get("dest")

    if not source or not dest:
        raise ValueError("Missing required parameters: source, dest")

    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(dest))

    return {"source": source, "dest": dest}


def _tool_file_find(params: Dict[str, Any]) -> list:
    """Find files matching pattern."""
    path = params.get("path")
    pattern = params.get("pattern", "*")

    if not path:
        raise ValueError("Missing required parameter: path")

    return [str(p) for p in Path(path).glob(pattern)]


def _tool_json_parse(params: Dict[str, Any]) -> Any:
    """Parse JSON string to object."""
    content = params.get("content")

    if content is None:
        raise ValueError("Missing required parameter: content")

    return json.loads(content)


def _tool_json_validate(params: Dict[str, Any]) -> Dict:
    """
    Validate JSON data against schema.

    DESIGN REASONING:
    - Returns structured result (valid, errors)
    - Supports simple schema validation
    - Extensible to JSON Schema later
    """
    data = params.get("data")
    schema_path = params.get("schema_path")

    if data is None:
        raise ValueError("Missing required parameter: data")

    # Load schema if path provided
    schema = None
    errors = []

    if schema_path:
        with open(schema_path, 'r') as f:
            schema = json.load(f)

        # Simple validation: check required fields
        if "required" in schema:
            if isinstance(data, dict):
                for field in schema["required"]:
                    if field not in data:
                        errors.append(f"Missing required field: {field}")

        # Check properties exist in schema
        if "properties" in schema and isinstance(data, dict):
            for field in data:
                if field not in schema["properties"]:
                    errors.append(f"Unknown field: {field}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "recoverable": len(errors) > 0  # Flag if errors are potentially fixable
    }


def _tool_json_stringify(params: Dict[str, Any]) -> str:
    """Convert object to JSON string."""
    data = params.get("data")

    if data is None:
        raise ValueError("Missing required parameter: data")

    return json.dumps(data, indent=2)


def _tool_llm_analyze(params: Dict[str, Any]) -> Dict:
    """
    Analyze text using LLM (provider-agnostic).

    DESIGN REASONING:
    - Returns structured analysis result (category, tags, confidence)
    - Provider can be mocked, OpenAI, Claude, etc.
    - Configuration determines which provider to use
    - v0.1: Mock provider for deterministic testing
    - v0.2: OpenAI integration
    - v0.3: Provider abstraction (Claude, OpenAI, local, etc.) - IMPLEMENTED

    Params:
    - text (required): Text to analyze
    - prompt (optional): Prompt for the LLM
    - provider (optional): Provider name (mock, openai, claude) - default: mock
    - model (optional): Model name (specific to provider)
    - api_key (optional): API key (from environment or param)
    """
    text = params.get("text")
    prompt = params.get("prompt", "Analyze this text and categorize as: error, success, warning, info, or unknown. Return a JSON object with category, tags (list), and confidence (0-1).")
    provider_name = params.get("provider", "mock")

    if not text:
        raise ValueError("Missing required parameter: text")

    # Get provider and delegate analysis
    provider = get_llm_provider(provider_name)
    return provider.analyze(text, prompt, params)


def _mock_llm_analyze(text: str, prompt: str) -> Dict:
    """
    Mock LLM analyzer for deterministic testing.
    Returns consistent results based on keywords in text.
    """
    text_lower = text.lower()

    # Determine category based on keywords
    if any(word in text_lower for word in ["error", "failed", "problem", "issue", "bug"]):
        category = "error"
        confidence = 0.95
    elif any(word in text_lower for word in ["success", "completed", "done", "finished", "working"]):
        category = "success"
        confidence = 0.92
    elif any(word in text_lower for word in ["warning", "caution", "attention", "careful"]):
        category = "warning"
        confidence = 0.88
    elif any(word in text_lower for word in ["info", "information", "note", "notice"]):
        category = "info"
        confidence = 0.85
    else:
        category = "unknown"
        confidence = 0.5

    # Extract mock tags based on text length and content
    tags = []
    if len(text) > 100:
        tags.append("detailed")
    if any(word in text_lower for word in ["user", "account", "profile", "person"]):
        tags.append("user-related")
    if any(word in text_lower for word in ["system", "server", "network", "database"]):
        tags.append("system-related")
    if any(word in text_lower for word in ["security", "auth", "permission", "access"]):
        tags.append("security-related")

    return {
        "category": category,
        "tags": tags if tags else ["general"],
        "confidence": confidence,
        "summary": f"Text classified as {category}",
        "analysis": {
            "word_count": len(text.split()),
            "character_count": len(text),
            "provider": "mock",
            "model": "mock-v1"
        }
    }


def _openai_llm_analyze(text: str, prompt: str, params: Dict[str, Any]) -> Dict:
    """
    Analyze text using OpenAI API (GPT-4, GPT-3.5, etc.).

    Requires params:
    - model: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
    - api_key: OpenAI API key (from environment or params)

    Returns structured analysis result matching mock format for compatibility.
    """
    if OpenAI is None:
        raise ImportError("OpenAI SDK not installed. Run: pip install openai")

    # Get configuration from params or environment
    model = params.get("model", "gpt-3.5-turbo")
    api_key = params.get("api_key") or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or provide api_key parameter.")

    try:
        client = OpenAI(api_key=api_key)

        # Build a structured prompt for consistent responses
        structured_prompt = f"""{prompt}

Text to analyze:
{text}

Return ONLY a JSON object (no markdown, no extra text) with these fields:
{{
  "category": "error" | "success" | "warning" | "info" | "unknown",
  "tags": ["tag1", "tag2"],
  "confidence": 0.0-1.0,
  "summary": "brief description"
}}"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": structured_prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent categorization
            max_tokens=500
        )

        # Parse LLM response
        response_text = response.choices[0].message.content.strip()

        # Try to extract JSON from response
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If response isn't pure JSON, try to extract JSON from it
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback if parsing fails
                result = {
                    "category": "unknown",
                    "tags": ["parsing_error"],
                    "confidence": 0.0,
                    "summary": "Could not parse LLM response"
                }

        # Ensure required fields exist and are correct type
        result.setdefault("category", "unknown")
        result.setdefault("tags", [])
        result.setdefault("confidence", 0.5)
        result.setdefault("summary", f"Text classified as {result.get('category', 'unknown')}")

        # Validate category is one of allowed values
        if result["category"] not in ["error", "success", "warning", "info", "unknown"]:
            result["category"] = "unknown"

        # Ensure tags is a list
        if not isinstance(result["tags"], list):
            result["tags"] = [str(result["tags"])]

        # Ensure confidence is a float between 0 and 1
        try:
            confidence = float(result["confidence"])
            result["confidence"] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            result["confidence"] = 0.5

        # Add analysis metadata
        result["analysis"] = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "provider": "openai",
            "model": model
        }

        return result

    except RateLimitError:
        raise ValueError("OpenAI API rate limit exceeded. Please retry after a moment.")
    except APIConnectionError:
        raise ValueError("Failed to connect to OpenAI API. Check your internet connection and API key.")
    except APIError as e:
        raise ValueError(f"OpenAI API error: {str(e)}")


def _claude_llm_analyze(text: str, prompt: str, params: Dict[str, Any]) -> Dict:
    """
    Analyze text using Claude API (Anthropic).

    Requires params:
    - model: Claude model name (e.g., "claude-3-opus", "claude-3-sonnet", "claude-3-haiku")
    - api_key: Anthropic API key (from environment or params)

    Returns structured analysis result matching mock format for compatibility.
    """
    if Anthropic is None:
        raise ImportError("Anthropic SDK not installed. Run: pip install anthropic")

    # Get configuration from params or environment
    model = params.get("model", "claude-3-sonnet-20240229")
    api_key = params.get("api_key") or os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable or provide api_key parameter.")

    try:
        client = Anthropic(api_key=api_key)

        # Build a structured prompt for consistent responses
        structured_prompt = f"""{prompt}

Text to analyze:
{text}

Return ONLY a JSON object (no markdown, no extra text) with these fields:
{{
  "category": "error" | "success" | "warning" | "info" | "unknown",
  "tags": ["tag1", "tag2"],
  "confidence": 0.0-1.0,
  "summary": "brief description"
}}"""

        response = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[
                {"role": "user", "content": structured_prompt}
            ]
        )

        # Parse Claude response
        response_text = response.content[0].text.strip()

        # Try to extract JSON from response
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # If response isn't pure JSON, try to extract JSON from it
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback if parsing fails
                result = {
                    "category": "unknown",
                    "tags": ["parsing_error"],
                    "confidence": 0.0,
                    "summary": "Could not parse Claude response"
                }

        # Ensure required fields exist and are correct type
        result.setdefault("category", "unknown")
        result.setdefault("tags", [])
        result.setdefault("confidence", 0.5)
        result.setdefault("summary", f"Text classified as {result.get('category', 'unknown')}")

        # Validate category is one of allowed values
        if result["category"] not in ["error", "success", "warning", "info", "unknown"]:
            result["category"] = "unknown"

        # Ensure tags is a list
        if not isinstance(result["tags"], list):
            result["tags"] = [str(result["tags"])]

        # Ensure confidence is a float between 0 and 1
        try:
            confidence = float(result["confidence"])
            result["confidence"] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            result["confidence"] = 0.5

        # Add analysis metadata
        result["analysis"] = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "provider": "claude",
            "model": model
        }

        return result

    except AnthropicAPIError as e:
        raise ValueError(f"Claude API error: {str(e)}")
    except Exception as e:
        if "API_KEY" in str(e) or "authentication" in str(e).lower():
            raise ValueError("Failed to authenticate with Claude API. Check your API key.")
        raise ValueError(f"Claude API error: {str(e)}")


def _tool_message_send(params: Dict[str, Any]) -> Dict:
    """Send message to another agent (stub for now)."""
    recipient = params.get("recipient")
    message = params.get("message")

    if not recipient:
        raise ValueError("Missing required parameter: recipient")

    # v0.1: Just log it (hub not connected yet)
    # v0.5: Will actually send via hub
    return {
        "recipient": recipient,
        "message": message,
        "status": "queued_for_hub"
    }


def _tool_log(params: Dict[str, Any]) -> Dict:
    """
    Write to log.

    DESIGN REASONING:
    - Allows workflows to log custom messages
    - Supports different log levels
    - Logs appear in structured logs
    """
    message = params.get("message")
    level = params.get("level", "info").upper()

    if not message:
        raise ValueError("Missing required parameter: message")

    # Get the logger (created by runtime)
    logger = logging.getLogger()

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)

    return {"logged": message}
