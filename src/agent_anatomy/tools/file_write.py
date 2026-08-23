"""write_file — same shape as read_file, but with a side effect.

Note what we DON'T do here: no approval prompt. Writing files is the
agent's job; the risky tool is shell.py, which can do anything. Where
you draw that line is a design decision, not a law — Kiro-CLI, for
example, asks before file writes too (unless you /trust it).
"""

from pathlib import Path

from strands import tool


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories if needed.
    Overwrites the file if it already exists.

    Args:
        path: Path of the file to write.
        content: The complete new content of the file.
    """
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return f"Wrote {len(content)} chars to {path}."
