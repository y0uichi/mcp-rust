# agent-coder

AI-powered coding agent built on Claude Agent SDK.

## Features

- **Code Writing**: Generate new code from specifications
- **Code Editing**: Modify existing code with precision
- **Code Analysis**: Understand and explain code structure
- **Test Generation**: Create unit tests automatically
- **Refactoring**: Improve code quality and patterns
- **Git Integration**: Smart git operations
- **Project Management**: Scaffold and manage project structures

## Installation

```bash
pip install -e packages/agent-coder
```

## Quick Start

### CLI Usage

The `ac` command-line tool provides quick access to agent-coder:

```bash
# Interactive mode (default)
ac

# Single-shot execution
ac run "Create a Python function to calculate fibonacci numbers"

# Stream responses in real-time
ac run -s "Explain what recursion is"

# Analyze a file
ac analyze src/main.py

# Explain what code does
ac explain src/utils.py

# Generate tests for a file
ac test src/calculator.py

# Specify working directory
ac -C /path/to/project run "Add error handling"
```

#### CLI Options

- `--model`: Claude model to use (default: claude-3-5-sonnet-20241022)
- `-C, --working-dir`: Working directory for file operations
- `--permission-mode`: Permission mode for tool usage

### Python API

#### Basic Usage

```python
import asyncio
from agent_coder import AgentCoder

async def main():
    agent = AgentCoder()
    result = await agent.run("Create a Python function to calculate fibonacci numbers")
    print(result)

asyncio.run(main())
```

### Interactive Session

```python
import asyncio
from agent_coder import AgentCoder

async def main():
    agent = AgentCoder()
    await agent.interactive_session()

asyncio.run(main())
```

### Custom Configuration

```python
from agent_coder import AgentCoder, AgentCoderConfig

config = AgentCoderConfig(
    model="claude-3-5-sonnet-20241022",
    permission_mode="acceptEdits",
    working_dir="/path/to/project"
)
agent = AgentCoder(config=config)
```

## Custom Tools

agent-coder includes custom tools for coding tasks:

- `analyze_code`: Analyze code structure and quality
- `refactor_code`: Suggest and apply refactoring
- `generate_tests`: Generate unit tests
- `explain_code`: Explain code functionality
- `create_project`: Scaffold new projects
- `git_status`: Get git status with context
- `git_commit`: Create formatted commits
- `git_diff`: Get intelligent diff summary

## Development

Install in development mode:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

MIT
