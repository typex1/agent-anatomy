"""search — grep across the working tree, no dependencies.

Real coding agents (Kiro, Claude Code) shell out to ripgrep for speed.
We walk the tree in pure Python so you can read the whole mechanism.
The trade-off costs milliseconds on a repo this size and buys total
transparency — the right trade for a teaching codebase.
"""

import re
from pathlib import Path

from strands import tool

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".ruff_cache"}
MAX_RESULTS = 50


@tool
def search(pattern: str, directory: str = ".") -> str:
    """Search file contents for a regex pattern. Returns matching lines
    as path:line_number:line.

    Args:
        pattern: Regular expression to search for.
        directory: Directory to search in (default: current directory).
    """
    try:
        rx = re.compile(pattern)
    except re.error as e:
        return f"Invalid regex: {e}"

    hits: list[str] = []
    for p in sorted(Path(directory).rglob("*")):
        if not p.is_file() or any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            text = p.read_text(errors="strict")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable — skip
        for n, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append(f"{p}:{n}:{line.strip()[:200]}")
                if len(hits) >= MAX_RESULTS:
                    return "\n".join(hits) + f"\n... [stopped at {MAX_RESULTS} matches]"
    return "\n".join(hits) or f"No matches for {pattern!r} in {directory}."
