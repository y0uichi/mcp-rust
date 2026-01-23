"""
Tests for custom tools.
"""

import tempfile
from pathlib import Path

import pytest

from agent_coder.tools import (
    analyze_code,
    explain_code,
    refactor_code,
    generate_tests,
    create_project,
    list_structure,
)


def test_analyze_code_python():
    """Test code analysis for Python files."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""
def hello(name: str) -> str:
    return f"Hello, {name}!"

class Greeter:
    def greet(self, name: str) -> str:
        return hello(name)
""")
        f.flush()

        result = analyze_code({"file_path": f.name})

        assert "content" in result
        assert not result.get("is_error", False)
        content = result["content"][0]["text"]
        assert "hello" in content.lower() or "function" in content.lower()

        Path(f.name).unlink()


def test_analyze_code_nonexistent():
    """Test code analysis with non-existent file."""
    result = analyze_code({"file_path": "/nonexistent/file.py"})

    assert result.get("is_error", False)
    assert "Error: File not found" in result["content"][0]["text"]


def test_explain_code():
    """Test code explanation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def add(a, b): return a + b")
        f.flush()

        result = explain_code({"file_path": f.name})

        assert "content" in result
        content = result["content"][0]["text"]
        assert "python" in content.lower()

        Path(f.name).unlink()


def test_refactor_code():
    """Test refactoring suggestions."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("x=1\ny=2\nz=x+y\n")
        f.flush()

        result = refactor_code({"file_path": f.name})

        assert "content" in result
        content = result["content"][0]["text"]
        assert "suggestion" in content.lower() or "improvement" in content.lower()

        Path(f.name).unlink()


def test_generate_tests():
    """Test test generation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def multiply(a, b): return a * b")
        f.flush()

        result = generate_tests({"file_path": f.name})

        assert "content" in result
        content = result["content"][0]["text"]
        assert "test" in content.lower()

        Path(f.name).unlink()


def test_create_project():
    """Test project creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = create_project({
            "project_name": "test_project",
            "project_type": "python",
            "path": tmpdir,
        })

        assert "content" in result
        assert not result.get("is_error", False)

        # Check that project was created
        project_path = Path(tmpdir) / "test_project"
        assert project_path.exists()
        assert (project_path / "pyproject.toml").exists()
        assert (project_path / "src").exists()


def test_list_structure():
    """Test listing project structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        Path(tmpdir, "test.py").touch()
        Path(tmpdir, "subdir").mkdir()
        Path(tmpdir, "subdir", "nested.py").touch()

        result = list_structure({"path": tmpdir, "max_depth": 3})

        assert "content" in result
        content = result["content"][0]["text"]
        assert "test.py" in content or "test" in content
