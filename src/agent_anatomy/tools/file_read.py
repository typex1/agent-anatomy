"""read_file — the simplest possible tool. Start reading here."""

from pathlib import Path

from strands import tool

MAX_CHARS = 50_000  # protect the context window from huge files


@tool
def read_file(path: str, start_line: int = 1, num_lines: int = 500) -> str:
    """Read a text file and return its content with line numbers.

    Args:
        path: Path to the file (absolute or relative to the working directory).
        start_line: First line to return (1-indexed).
        num_lines: Maximum number of lines to return.
    """
    p = Path(path).expanduser()
    if not p.is_file():
        return f"Error: {path} is not a file."

    lines = p.read_text(errors="replace").splitlines()
    window = lines[start_line - 1 : start_line - 1 + num_lines]
    body = "\n".join(f"{i}|{line}" for i, line in enumerate(window, start=start_line))
    if len(body) > MAX_CHARS:
        body = body[:MAX_CHARS] + "\n... [truncated]"

    header = f"{path} ({len(lines)} lines total, showing from line {start_line}):\n"
    return header + body
