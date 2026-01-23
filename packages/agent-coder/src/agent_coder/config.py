"""
Configuration management for agent-coder.

This module provides the AgentCoderConfig class for configuring
the AI coding agent behavior and capabilities.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class AgentCoderConfig:
    """
    Configuration for the AgentCoder.

    Attributes:
        model: The Claude model to use (default: claude-3-5-sonnet-20241022)
        fallback_model: Fallback model if primary fails
        permission_mode: Permission mode for tool usage
        working_dir: Working directory for file operations
        max_tokens: Maximum tokens for responses
        allowed_tools: List of allowed tool names
        custom_tools: Custom MCP servers with tools
        system_prompt: Custom system prompt override
    """

    model: str = "claude-3-5-sonnet-20241022"
    fallback_model: str | None = "claude-3-5-haiku-20241022"
    permission_mode: str = "acceptEdits"
    working_dir: str | Path = "."
    max_tokens: int = 8192
    allowed_tools: list[str] = field(default_factory=lambda: [
        "Read",
        "Write",
        "Edit",
        "Bash",
        "Grep",
        "Glob",
    ])
    custom_tools: dict[str, Any] = field(default_factory=dict)
    system_prompt: str | None = None

    def __post_init__(self):
        """Convert working_dir to Path if it's a string."""
        if isinstance(self.working_dir, str):
            self.working_dir = Path(self.working_dir)

    def to_claude_options(self) -> dict:
        """
        Convert this config to ClaudeAgentOptions kwargs.

        Returns:
            Dictionary of kwargs for ClaudeAgentOptions
        """
        options = {
            "model": self.model,
            "permission_mode": self.permission_mode,
            "cwd": str(self.working_dir.absolute()),
            "allowed_tools": self.allowed_tools,
        }

        if self.fallback_model:
            options["fallback_model"] = self.fallback_model

        if self.custom_tools:
            options["mcp_servers"] = self.custom_tools

        return options


@dataclass
class ToolConfig:
    """Configuration for a custom tool."""

    name: str
    description: str
    input_schema: dict
