"""A complete MCP server in ~30 lines.

This is the OTHER side of the protocol: mcp.py in the package is the
client, this file is a server. The client launches this script as a
subprocess and they speak JSON-RPC 2.0 over stdin/stdout — that's all
the "stdio transport" is.

Run it manually to see it wait for JSON-RPC on stdin:

    uv run python mcp_servers/clock_server.py
"""

from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

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
