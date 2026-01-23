"""
Code analysis and manipulation tools.

This module provides tools for analyzing, refactoring, and understanding code.
"""

import ast
from pathlib import Path


def _get_file_content(file_path: str) -> str:
    """Get file content safely."""
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {file_path}"
    return path.read_text()


def _detect_language(file_path: str) -> str:
    """Detect programming language from file extension."""
    ext = Path(file_path).suffix.lower()
    lang_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".hpp": "cpp",
        ".h": "c",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".kt": "kotlin",
        ".swift": "swift",
        ".sh": "bash",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".md": "markdown",
    }
    return lang_map.get(ext, "text")


def analyze_code(args: dict) -> dict:
    """
    Analyze code structure, quality, and patterns.

    Args:
        args: Dictionary with 'file_path' key

    Returns:
        Analysis result with metrics and suggestions
    """
    file_path = args.get("file_path", "")
    content = _get_file_content(file_path)

    if content.startswith("Error:"):
        return {"content": [{"type": "text", "text": content}], "is_error": True}

    language = _detect_language(file_path)
    lines = content.split("\n")
    total_lines = len(lines)
    non_empty_lines = sum(1 for line in lines if line.strip())
    comment_lines = 0

    # Basic analysis
    analysis = [
        f"## Code Analysis: {file_path}",
        f"**Language**: {language}",
        f"**Total Lines**: {total_lines}",
        f"**Code Lines**: {non_empty_lines}",
    ]

    # Language-specific analysis
    if language == "python":
        try:
            tree = ast.parse(content)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend([alias.name for alias in node.names])
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    imports.extend([f"{module}.{alias.name}" for alias in node.names])

            analysis.append(f"**Functions**: {len(functions)}")
            analysis.append(f"**Classes**: {len(classes)}")
            analysis.append(f"**Imports**: {len(set(imports))}")

            if functions:
                analysis.append("\n**Functions**: " + ", ".join(functions[:10]))
                if len(functions) > 10:
                    analysis.append(f"... and {len(functions) - 10} more")

            if classes:
                analysis.append("\n**Classes**: " + ", ".join(classes))

        except SyntaxError as e:
            analysis.append(f"\n**Syntax Error**: {e}")

    result_text = "\n".join(analysis)
    return {"content": [{"type": "text", "text": result_text}]}


def explain_code(args: dict) -> dict:
    """
    Explain code functionality.

    Args:
        args: Dictionary with 'file_path' and optional 'focus' keys

    Returns:
        Explanation of what the code does
    """
    file_path = args.get("file_path", "")
    focus = args.get("focus", "")

    content = _get_file_content(file_path)

    if content.startswith("Error:"):
        return {"content": [{"type": "text", "text": content}], "is_error": True}

    language = _detect_language(file_path)

    explanation = [
        f"## Code Explanation: {file_path}",
        f"**Language**: {language}",
        "",
        "This file contains code that should be analyzed for its functionality.",
        "",
        "Key elements to examine:",
        "- Main functions and their purposes",
        "- Data structures used",
        "- Algorithms implemented",
        "- Dependencies and imports",
        "",
    ]

    if focus:
        explanation.append(f"**Focus Area**: {focus}")

    if language == "python":
        try:
            tree = ast.parse(content)
            functions = []
            classes = []

            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    docstring = ast.get_docstring(node)
                    funcs_info = f"**{node.name}**({', '.join(arg.arg for arg in node.args.args)})"
                    if docstring:
                        funcs_info += f"\n   {docstring.split(chr(10))[0]}"
                    functions.append(funcs_info)
                elif isinstance(node, ast.ClassDef):
                    docstring = ast.get_docstring(node)
                    classes.append(f"**class {node.name}**")

            if functions:
                explanation.append("\n### Functions\n" + "\n".join(functions))

            if classes:
                explanation.append("\n### Classes\n" + "\n".join(classes))

        except SyntaxError:
            pass

    return {"content": [{"type": "text", "text": "\n".join(explanation)}]}


def refactor_code(args: dict) -> dict:
    """
    Suggest code refactoring improvements.

    Args:
        args: Dictionary with 'file_path' key

    Returns:
        Refactoring suggestions
    """
    file_path = args.get("file_path", "")
    content = _get_file_content(file_path)

    if content.startswith("Error:"):
        return {"content": [{"type": "text", "text": content}], "is_error": True}

    suggestions = [
        f"## Refactoring Suggestions: {file_path}",
        "",
        "### Potential Improvements:",
        "",
        "1. **Code Organization**",
        "   - Check for repeated code patterns that could be extracted",
        "   - Consider breaking long functions into smaller units",
        "",
        "2. **Naming**",
        "   - Ensure variable and function names clearly express intent",
        "   - Use consistent naming conventions",
        "",
        "3. **Complexity**",
        "   - Look for deeply nested conditionals that could be simplified",
        "   - Consider guard clauses for early returns",
        "",
        "4. **Documentation**",
        "   - Add docstrings to functions and classes",
        "   - Document non-obvious logic",
        "",
    ]

    return {"content": [{"type": "text", "text": "\n".join(suggestions)}]}


def generate_tests(args: dict) -> dict:
    """
    Generate unit test suggestions for code.

    Args:
        args: Dictionary with 'file_path' key

    Returns:
        Suggested test cases
    """
    file_path = args.get("file_path", "")
    content = _get_file_content(file_path)

    if content.startswith("Error:"):
        return {"content": [{"type": "text", "text": content}], "is_error": True}

    language = _detect_language(file_path)

    test_suggestions = [
        f"## Test Generation: {file_path}",
        f"**Language**: {language}",
        "",
        "### Recommended Test Cases:",
        "",
    ]

    if language == "python":
        try:
            tree = ast.parse(content)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            for func in functions[:10]:
                test_suggestions.append(f"- `test_{func}`: Test the {func} function")

            test_suggestions.append("\n### Test Framework: pytest")
            test_suggestions.append("\n```python")
            test_suggestions.append("import pytest")
            test_suggestions.append("")
            test_suggestions.append("# TODO: Implement tests")
            test_suggestions.append("```")

        except SyntaxError:
            test_suggestions.append("Unable to parse file for test suggestions due to syntax errors.")

    return {"content": [{"type": "text", "text": "\n".join(test_suggestions)}]}
