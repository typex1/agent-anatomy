"""mcp.py — connecting to MCP servers, both flavors.

MCP (Model Context Protocol) lets an agent use tools that live in a
SEPARATE process — even on a separate machine. The agent doesn't know
or care how a tool is implemented; it just sees more tool schemas.

We connect to two servers, one per transport:

  1. AWS Knowledge MCP  — REMOTE, streamable HTTP. Fully managed by AWS,
     no credentials, no install. Gives the agent tools to search AWS
     docs. One URL is the entire integration.

  2. clock server       — LOCAL, stdio. A ~30-line server that lives in
     this repo (mcp_servers/clock_server.py). The client launches it as
     a subprocess and speaks JSON-RPC over stdin/stdout. Read the server
     file to see the other side of the protocol.

Strands' MCPClient wraps the official `mcp` package. The clients are
context managers: the connection (and the stdio subprocess) lives only
while the `with` block in cli.py is open.
"""

import sys
from pathlib import Path

from mcp import StdioServerParameters, stdio_client

from strands.tools.mcp import MCPClient

AWS_KNOWLEDGE_URL = "https://knowledge-mcp.global.api.aws"

# the tiny server that ships in this repo
CLOCK_SERVER = Path(__file__).parent.parent.parent / "mcp_servers" / "clock_server.py"


def aws_knowledge_client() -> MCPClient:
    """Remote server, streamable HTTP transport: the whole setup is a URL."""
    return MCPClient(url=AWS_KNOWLEDGE_URL, prefix="aws")


def clock_client() -> MCPClient:
    """Local server, stdio transport: we launch the subprocess ourselves."""
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(command=sys.executable, args=[str(CLOCK_SERVER)])
        ),
        prefix="clock",
    )
