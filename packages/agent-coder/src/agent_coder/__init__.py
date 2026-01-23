"""
agent-coder: AI-powered coding agent built on Claude Agent SDK.

This package provides a full-featured AI coding assistant that can:
- Write, edit, and analyze code
- Generate unit tests
- Refactor existing code
- Manage project structure
- Handle git operations
"""

from .agent import AgentCoder
from .config import AgentCoderConfig
from .prompts import CODING_ASSISTANT_PROMPT, CODE_REVIEWER_PROMPT

__all__ = [
    "AgentCoder",
    "AgentCoderConfig",
    "CODING_ASSISTANT_PROMPT",
    "CODE_REVIEWER_PROMPT",
]

__version__ = "0.1.0"
