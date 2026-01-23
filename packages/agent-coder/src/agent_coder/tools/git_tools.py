"""
Git operation tools.

This module provides tools for git operations including status,
commit creation, and diff analysis.
"""

import subprocess
from pathlib import Path


def _run_git_command(args: list[str], cwd: str = ".") -> tuple[str, str, int]:
    """Run a git command and return stdout, stderr, and return code."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout, result.stderr, result.returncode
    except FileNotFoundError:
        return "", "git not found in PATH", 1
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1


def _find_git_root(path: str = ".") -> str | None:
    """Find the git root directory."""
    current = Path(path).absolute()
    for _ in range(20):  # Limit depth
        if (current / ".git").exists():
            return str(current)
        if current.parent == current:
            break
        current = current.parent
    return None


def git_status(args: dict) -> dict:
    """
    Get git status with context.

    Args:
        args: Dictionary with optional 'path' key

    Returns:
        Git status information
    """
    path = args.get("path", ".")
    git_root = _find_git_root(path)

    if not git_root:
        return {
            "content": [{"type": "text", "text": "Not a git repository (or any parent up to mount point)"}],
            "is_error": True,
        }

    stdout, stderr, code = _run_git_command(["status", "--porcelain"], cwd=path)

    if code != 0:
        return {"content": [{"type": "text", "text": f"Error: {stderr}"}], "is_error": True}

    if not stdout.strip():
        return {"content": [{"type": "text", "text": "Working tree clean. No changes."}]}

    # Parse status output
    lines = stdout.strip().split("\n")
    staged = []
    modified = []
    untracked = []
    renamed = []

    for line in lines:
        if not line:
            continue
        status, filepath = line[:2], line[3:]
        if status[0] == "R":
            renamed.append(filepath)
        elif status[0] in "MADRC":
            staged.append(filepath)
        elif status[0] == " " and status[1] in "M":
            modified.append(filepath)
        elif status == "??":
            untracked.append(filepath)

    result = [f"## Git Status: {Path(path).absolute()}", ""]

    if staged:
        result.append("### Staged changes:")
        for f in staged:
            result.append(f"  - {f}")
        result.append("")

    if modified:
        result.append("### Modified but not staged:")
        for f in modified:
            result.append(f"  - {f}")
        result.append("")

    if untracked:
        result.append("### Untracked files:")
        for f in untracked[:20]:
            result.append(f"  - {f}")
        if len(untracked) > 20:
            result.append(f"  ... and {len(untracked) - 20} more")
        result.append("")

    result.append(f"**Git root**: {git_root}")

    return {"content": [{"type": "text", "text": "\n".join(result)}]}


def git_commit(args: dict) -> dict:
    """
    Create a formatted git commit.

    Args:
        args: Dictionary with 'message' and optional 'add_all' keys

    Returns:
        Commit result
    """
    message = args.get("message", "")
    add_all = args.get("add_all", False)
    path = args.get("path", ".")

    if not message:
        return {"content": [{"type": "text", "text": "Error: commit message is required"}], "is_error": True}

    if not _find_git_root(path):
        return {"content": [{"type": "text", "text": "Not a git repository"}], "is_error": True}

    if add_all:
        _run_git_command(["add", "."], cwd=path)

    stdout, stderr, code = _run_git_command(["commit", "-m", message], cwd=path)

    if code != 0:
        return {"content": [{"type": "text", "text": f"Commit failed: {stderr}"}], "is_error": True}

    result = [
        "## Commit Created",
        "",
        f"**Message**: {message}",
        "",
        "### Output:",
        stdout,
    ]

    return {"content": [{"type": "text", "text": "\n".join(result)}]}


def git_diff(args: dict) -> dict:
    """
    Get intelligent diff summary.

    Args:
        args: Dictionary with optional 'path', 'staged', and 'file' keys

    Returns:
        Diff summary
    """
    path = args.get("path", ".")
    staged = args.get("staged", False)
    file_path = args.get("file", "")

    if not _find_git_root(path):
        return {"content": [{"type": "text", "text": "Not a git repository"}], "is_error": True}

    cmd = ["diff"]
    if staged:
        cmd.append("--staged")
    if file_path:
        cmd.append(file_path)

    stdout, stderr, code = _run_git_command(cmd, cwd=path)

    if code != 0 and stderr:
        return {"content": [{"type": "text", "text": f"Error: {stderr}"}], "is_error": True}

    if not stdout.strip():
        return {"content": [{"type": "text", "text": "No differences found"}]}

    # Analyze diff
    lines = stdout.split("\n")
    added_lines = sum(1 for line in lines if line.startswith("+") and not line.startswith("+++"))
    removed_lines = sum(1 for line in lines if line.startswith("-") and not line.startswith("---"))
    files_changed = sum(1 for line in lines if line.startswith("diff --git"))

    result = [
        f"## Git Diff Summary",
        f"**Staged**: {staged}",
        f"**Files Changed**: {files_changed}",
        f"**Lines Added**: {added_lines}",
        f"**Lines Removed**: {removed_lines}",
        "",
        "### Diff:",
        "```diff",
    ]

    # Truncate very long diffs
    max_lines = 500
    if len(lines) > max_lines:
        result.extend(lines[:max_lines])
        result.append(f"... ({len(lines) - max_lines} more lines)")
    else:
        result.extend(lines)

    result.append("```")

    return {"content": [{"type": "text", "text": "\n".join(result)}]}
