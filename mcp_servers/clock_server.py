"""A complete MCP server in ~30 lines.

This is the OTHER side of the protocol: mcp_clients.py in the package is the
client, this file is a server. The client launches this script as a
subprocess and they speak JSON-RPC 2.0 over stdin/stdout — that's all
the "stdio transport" is.

Run it manually to see it wait for JSON-RPC on stdin:

    uv run python mcp_servers/clock_server.py
"""

import warnings
from datetime import datetime, timezone

# Upstream noise, not ours: FastMCP's Settings has a `lifespan` field whose
# type hint forward-references FastMCP itself; pydantic-settings >= 2.15
# warns about that at import time. Harmless (the field defaults to None),
# but this process inherits the REPL's stderr, so the warning would show up
# in the user's terminal on every start. Drop the filter once `mcp` calls
# model_rebuild() upstream.
warnings.filterwarnings(
    "ignore", message=".*Field 'lifespan' has an incomplete definition.*"
)

from mcp.server.fastmcp import FastMCP  # noqa: E402  (after the filter on purpose)

server = FastMCP("clock")


@server.tool()
def current_time(tz_offset_hours: int = 0) -> str:
    """Return the current date and time, optionally offset from UTC.

    Args:
        tz_offset_hours: Hours to add to UTC (e.g. 2 for CEST).
    """
    now = datetime.now(timezone.utc)
    local = now.timestamp() + tz_offset_hours * 3600
    stamp = datetime.fromtimestamp(local, tz=timezone.utc)
    return stamp.strftime(f"%Y-%m-%d %H:%M:%S (UTC{tz_offset_hours:+d})")


if __name__ == "__main__":
    server.run()  # defaults to stdio transport
