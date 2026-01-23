"""
Project management tools.

This module provides tools for creating project structures,
managing dependencies, and listing project structure.
"""

import os
from pathlib import Path


def create_project(args: dict) -> dict:
    """
    Create a new project structure.

    Args:
        args: Dictionary with 'project_name', 'project_type', and optional 'path' keys

    Returns:
        Result message
    """
    project_name = args.get("project_name", "")
    project_type = args.get("project_type", "python")
    base_path = args.get("path", ".")

    if not project_name:
        return {"content": [{"type": "text", "text": "Error: project_name is required"}], "is_error": True}

    project_path = Path(base_path) / project_name

    if project_path.exists():
        return {
            "content": [{"type": "text", "text": f"Error: Directory {project_name} already exists"}],
            "is_error": True,
        }

    # Create project structure based on type
    os.makedirs(project_path, exist_ok=True)

    if project_type == "python":
        _create_python_project(project_path, project_name)
    elif project_type == "node":
        _create_node_project(project_path, project_name)
    elif project_type == "rust":
        _create_rust_project(project_path, project_name)
    else:
        _create_generic_project(project_path, project_name)

    result = [
        f"## Project Created: {project_name}",
        f"**Type**: {project_type}",
        f"**Path**: {project_path.absolute()}",
        "",
        "### Next Steps:",
        "1. cd " + project_name,
        "2. Review the generated structure",
        "3. Start coding!",
    ]

    return {"content": [{"type": "text", "text": "\n".join(result)}]}


def _create_python_project(path: Path, name: str) -> None:
    """Create a Python project structure."""
    dirs = ["src", "tests", "docs"]
    for d in dirs:
        (path / d).mkdir(exist_ok=True)

    (path / "src" / "__init__.py").touch()
    (path / "tests" / "__init__.py").touch()

    (path / "pyproject.toml").write_text(
        f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{name}"
version = "0.1.0"
description = "A new Python project"
requires-python = ">=3.10"

[tool.black]
line-length = 100
"""
    )

    (path / ".gitignore").write_text(
        """__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
.env
dist/
build/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
"""
    )

    (path / "README.md").write_text(
        f"""# {name}

A new Python project.

## Installation

```bash
pip install -e .
```

## Usage

TODO: Add usage instructions
"""
    )


def _create_node_project(path: Path, name: str) -> None:
    """Create a Node.js project structure."""
    dirs = ["src", "tests"]
    for d in dirs:
        (path / d).mkdir(exist_ok=True)

    (path / "package.json").write_text(
        f"""{{
  "name": "{name}",
  "version": "0.1.0",
  "description": "A new Node.js project",
  "type": "module",
  "scripts": {{
    "start": "node src/index.js",
    "test": "echo \\"Error: no test specified\\" && exit 1"
  }},
  "keywords": [],
  "author": "",
  "license": "MIT"
}}
"""
    )

    (path / ".gitignore").write_text(
        """node_modules/
dist/
.env
*.log
.DS_Store
"""
    )

    (path / "README.md").write_text(
        f"""# {name}

A new Node.js project.

## Installation

```bash
npm install
```

## Usage

```bash
npm start
```
"""
    )


def _create_rust_project(path: Path, name: str) -> None:
    """Create a Rust project structure."""
    dirs = ["src"]
    for d in dirs:
        (path / d).mkdir(exist_ok=True)

    (path / "Cargo.toml").write_text(
        f"""[package]
name = "{name}"
version = "0.1.0"
edition = "2021"

[dependencies]
"""
    )

    (path / "src" / "main.rs").write_text(
        """fn main() {
    println!("Hello, world!");
}
"""
    )

    (path / ".gitignore").write_text(
        """/target
**/*.rs.bk
Cargo.lock
"""
    )

    (path / "README.md").write_text(
        f"""# {name}

A new Rust project.

## Build

```bash
cargo build
```

## Run

```bash
cargo run
```
"""
    )


def _create_generic_project(path: Path, name: str) -> None:
    """Create a generic project structure."""
    (path / "src").mkdir(exist_ok=True)
    (path / ".gitignore").write_text("*.log\n.env/\n")
    (path / "README.md").write_text(f"# {name}\n\nTODO: Add project description\n")


def add_dependency(args: dict) -> dict:
    """
    Add a dependency to the project.

    Args:
        args: Dictionary with 'package' and optional 'dev' keys

    Returns:
        Result message
    """
    package = args.get("package", "")
    dev = args.get("dev", False)

    if not package:
        return {"content": [{"type": "text", "text": "Error: package name is required"}], "is_error": True}

    # Check project type and suggest install command
    cwd = Path.cwd()

    if (cwd / "pyproject.toml").exists() or (cwd / "setup.py").exists():
        cmd = f"pip install {'--dev ' if dev else ''}{package}"
    elif (cwd / "package.json").exists():
        cmd = f"npm install {'--save-dev ' if dev else '--save '}{package}"
    elif (cwd / "Cargo.toml").exists():
        cmd = f"cargo add {'--dev ' if dev else ''}{package}"
    elif (cwd / "go.mod").exists():
        cmd = f"go get {package}"
    else:
        cmd = f"# Unknown project type. Please install {package} manually"

    result = [
        f"## Add Dependency: {package}",
        f"**Dev Dependency**: {dev}",
        "",
        "### Suggested Command:",
        f"```bash",
        cmd,
        "```",
    ]

    return {"content": [{"type": "text", "text": "\n".join(result)}]}


def list_structure(args: dict) -> dict:
    """
    List the project structure.

    Args:
        args: Dictionary with optional 'path' and 'max_depth' keys

    Returns:
        Project structure as text
    """
    path = args.get("path", ".")
    max_depth = args.get("max_depth", 5)

    root_path = Path(path).absolute()
    if not root_path.exists():
        return {"content": [{"type": "text", "text": f"Error: Path not found: {path}"}], "is_error": True}

    lines = [f"## Project Structure: {root_path.name}", ""]
    lines.extend(_generate_tree(root_path, root_path, max_depth=max_depth))

    return {"content": [{"type": "text", "text": "\n".join(lines)}]}


def _generate_tree(
    root: Path,
    current: Path,
    prefix: str = "",
    max_depth: int = 5,
    current_depth: int = 0,
) -> list[str]:
    """Generate tree structure lines."""
    if current_depth > max_depth:
        return []

    try:
        entries = sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        # Skip common ignore directories
        entries = [e for e in entries if e.name not in {".git", "node_modules", "__pycache__", ".venv", "venv", "target", "dist", "build"}]
    except PermissionError:
        return []

    lines = []
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            lines.extend(
                _generate_tree(
                    root,
                    entry,
                    prefix=prefix + extension,
                    max_depth=max_depth,
                    current_depth=current_depth + 1,
                )
            )

    return lines
