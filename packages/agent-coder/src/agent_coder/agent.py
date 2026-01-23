"""
Main agent implementation for agent-coder.

This module provides the AgentCoder class that orchestrates
the AI coding assistant using Claude Agent SDK.
"""

import asyncio
from typing import AsyncIterator

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, query
from claude_agent_sdk import create_sdk_mcp_server, tool

from .config import AgentCoderConfig
from .prompts import CODING_ASSISTANT_PROMPT, get_prompt
from .tools import (
    analyze_code,
    explain_code,
    generate_tests,
    refactor_code,
    git_commit,
    git_diff,
    git_status,
    create_project,
    add_dependency,
    list_structure,
)


# Wrap tools for MCP server
@tool("agent_coder_analyze_code", "Analyze code structure and quality", {"file_path": str})
async def _analyze_code(args: dict) -> dict:
    return analyze_code(args)


@tool("agent_coder_explain_code", "Explain code functionality", {"file_path": str, "focus": str})
async def _explain_code(args: dict) -> dict:
    return explain_code(args)


@tool("agent_coder_refactor_code", "Suggest code refactoring improvements", {"file_path": str})
async def _refactor_code(args: dict) -> dict:
    return refactor_code(args)


@tool("agent_coder_generate_tests", "Generate unit test suggestions", {"file_path": str})
async def _generate_tests(args: dict) -> dict:
    return generate_tests(args)


@tool("agent_coder_git_status", "Get git status with context", {"path": str})
async def _git_status(args: dict) -> dict:
    return git_status(args)


@tool("agent_coder_git_commit", "Create a git commit", {"message": str, "add_all": bool, "path": str})
async def _git_commit(args: dict) -> dict:
    return git_commit(args)


@tool("agent_coder_git_diff", "Get git diff summary", {"path": str, "staged": bool, "file": str})
async def _git_diff(args: dict) -> dict:
    return git_diff(args)


@tool("agent_coder_create_project", "Create a new project structure",
      {"project_name": str, "project_type": str, "path": str})
async def _create_project(args: dict) -> dict:
    return create_project(args)


@tool("agent_coder_add_dependency", "Add a dependency to the project",
      {"package": str, "dev": bool})
async def _add_dependency(args: dict) -> dict:
    return add_dependency(args)


@tool("agent_coder_list_structure", "List project structure", {"path": str, "max_depth": int})
async def _list_structure(args: dict) -> dict:
    return list_structure(args)


# Create the MCP server with all custom tools
_agent_coder_server = create_sdk_mcp_server(
    name="agent_coder",
    version="0.1.0",
    tools=[
        _analyze_code,
        _explain_code,
        _refactor_code,
        _generate_tests,
        _git_status,
        _git_commit,
        _git_diff,
        _create_project,
        _add_dependency,
        _list_structure,
    ],
)


class AgentCoder:
    """
    AI-powered coding agent using Claude Agent SDK.

    This agent can write, edit, analyze code, generate tests,
    and handle various coding tasks.
    """

    def __init__(self, config: AgentCoderConfig | None = None):
        """
        Initialize the AgentCoder.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or AgentCoderConfig()
        self._client: ClaudeSDKClient | None = None

    def _get_claude_options(self) -> ClaudeAgentOptions:
        """Build ClaudeAgentOptions from config."""
        options_kwargs = self.config.to_claude_options()
        options_kwargs["mcp_servers"] = {
            "agent_coder": _agent_coder_server,
            **self.config.custom_tools,
        }

        # Add custom tool names to allowed tools
        custom_tool_names = [
            "mcp__agent_coder__agent_coder_analyze_code",
            "mcp__agent_coder__agent_coder_explain_code",
            "mcp__agent_coder__agent_coder_refactor_code",
            "mcp__agent_coder__agent_coder_generate_tests",
            "mcp__agent_coder__agent_coder_git_status",
            "mcp__agent_coder__agent_coder_git_commit",
            "mcp__agent_coder__agent_coder_git_diff",
            "mcp__agent_coder__agent_coder_create_project",
            "mcp__agent_coder__agent_coder_add_dependency",
            "mcp__agent_coder__agent_coder_list_structure",
        ]
        options_kwargs["allowed_tools"] = list(set(options_kwargs["allowed_tools"] + custom_tool_names))

        return ClaudeAgentOptions(**options_kwargs)

    async def run(self, prompt: str) -> list[dict]:
        """
        Run a one-shot coding task.

        Args:
            prompt: The task description or prompt

        Returns:
            List of message dictionaries from the response
        """
        options = self._get_claude_options()
        messages = []

        async for message in query(prompt=prompt, options=options):
            messages.append(message)

        return messages

    async def run_stream(self, prompt: str) -> AsyncIterator[dict]:
        """
        Run a coding task with streaming responses.

        Args:
            prompt: The task description or prompt

        Yields:
            Message dictionaries as they arrive
        """
        options = self._get_claude_options()

        async for message in query(prompt=prompt, options=options):
            yield message

    async def interactive_session(self) -> None:
        """
        Start an interactive coding session.

        In this mode, you can have a back-and-forth conversation
        with the AI about your coding project.
        """
        if self._client is None:
            options = self._get_claude_options()
            self._client = ClaudeSDKClient(options=options)
            await self._client.connect(self.config.system_prompt or CODING_ASSISTANT_PROMPT)

        async for message in self._client.receive_messages():
            yield message

    async def send_message(self, message: str) -> AsyncIterator[dict]:
        """
        Send a message in an interactive session.

        Args:
            message: The message to send

        Yields:
            Response messages
        """
        if self._client is None:
            options = self._get_claude_options()
            self._client = ClaudeSDKClient(options=options)
            await self._client.connect(self.config.system_prompt or CODING_ASSISTANT_PROMPT)

        await self._client.query(message)

        async for response in self._client.receive_messages():
            yield response

    async def close(self) -> None:
        """Close the client connection if open."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
