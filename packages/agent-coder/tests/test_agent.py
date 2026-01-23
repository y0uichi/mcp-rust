"""
Tests for the AgentCoder class.
"""

import pytest

from agent_coder import AgentCoder, AgentCoderConfig


def test_config_default_values():
    """Test that default configuration values are set correctly."""
    config = AgentCoderConfig()

    assert config.model == "claude-3-5-sonnet-20241022"
    assert config.permission_mode == "acceptEdits"
    assert str(config.working_dir) == "."
    assert config.max_tokens == 8192
    assert len(config.allowed_tools) > 0


def test_config_custom_values():
    """Test that custom configuration values are set correctly."""
    config = AgentCoderConfig(
        model="claude-3-5-haiku-20241022",
        permission_mode="plan",
        max_tokens=4096,
    )

    assert config.model == "claude-3-5-haiku-20241022"
    assert config.permission_mode == "plan"
    assert config.max_tokens == 4096


def test_config_to_claude_options():
    """Test conversion to ClaudeAgentOptions kwargs."""
    config = AgentCoderConfig(
        model="claude-3-5-sonnet-20241022",
        permission_mode="acceptEdits",
        working_dir="/tmp/test",
    )

    options = config.to_claude_options()

    assert options["model"] == "claude-3-5-sonnet-20241022"
    assert options["permission_mode"] == "acceptEdits"
    assert "cwd" in options


def test_agent_initialization():
    """Test that AgentCoder initializes correctly."""
    agent = AgentCoder()

    assert agent.config is not None
    assert agent._client is None


def test_agent_with_config():
    """Test that AgentCoder accepts custom config."""
    config = AgentCoderConfig(model="claude-3-5-haiku-20241022")
    agent = AgentCoder(config=config)

    assert agent.config.model == "claude-3-5-haiku-20241022"
