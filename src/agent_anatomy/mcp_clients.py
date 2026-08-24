"""mcp_clients.py — connecting to MCP servers, both flavors.

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

(Why "mcp_clients" and not "mcp"? This module was once mcp.py — until it
deployed to AgentCore Runtime, where the zip layout put it on sys.path
AS `mcp`, shadowing the official mcp package it imports from and dying
in a circular import. Never name a module after a package you import.)
"""

import json
import os
import sys
from pathlib import Path

from mcp import StdioServerParameters, stdio_client

from strands.tools.mcp import MCPClient

AWS_KNOWLEDGE_URL = "https://knowledge-mcp.global.api.aws"

# repo root (locally) / unpacked code root (on AgentCore Runtime)
REPO_ROOT = Path(__file__).parent.parent.parent

# the tiny server that ships in this repo
CLOCK_SERVER = REPO_ROOT / "mcp_servers" / "clock_server.py"


def aws_knowledge_client() -> MCPClient:
    """Remote server, streamable HTTP transport: the whole setup is a URL."""
    return MCPClient(url=AWS_KNOWLEDGE_URL, prefix="aws")


def clock_client() -> MCPClient:
    """Local server, stdio transport: we launch the subprocess ourselves.

    The child gets PYTHONPATH pointing at our dependency root: a fresh
    Python subprocess inherits none of OUR import path, and on AgentCore
    Runtime the deps live in the unpacked code dir (/var/task), not in
    a site-packages the child would find on its own. Locally it's
    harmless — uv's venv already covers it.
    """
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command=sys.executable, args=[str(CLOCK_SERVER)], env=env
            )
        ),
        prefix="clock",
    )


# --- Third flavor: YOUR OWN remote server — AgentCore Gateway ------------
#
# Gateway exposes a Lambda function (gateway/aws_lookup/handler.py) as MCP
# tools over streamable HTTP — same transport as AWS Knowledge, but this
# one is ours. The demo gateway deploys with authorizerType NONE (open),
# so connecting is just a URL again. For a real deployment you'd switch
# to CUSTOM_JWT and set the three GATEWAY_* auth env vars below — the
# client then buys a bearer token via the OAuth2 client-credentials flow
# ("machine login"). SaaS MCP servers may be public; production
# infrastructure never should be.
#
# GATEWAY_URL comes from `agentcore deploy` outputs — see README.

def _gateway_token() -> str:
    """OAuth2 client-credentials flow against the gateway's authorizer."""
    import urllib.parse
    import urllib.request

    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": os.environ["GATEWAY_CLIENT_ID"],
            "client_secret": os.environ["GATEWAY_CLIENT_SECRET"],
        }
    ).encode()
    req = urllib.request.Request(
        os.environ["GATEWAY_TOKEN_URL"],
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def gateway_client() -> MCPClient | None:
    """Remote server, streamable HTTP — but ours.

    Returns None when GATEWAY_URL isn't set, so the agent runs fine
    before anything is deployed. Sends a bearer token only when JWT
    auth is configured (GATEWAY_TOKEN_URL etc. present).
    """
    url = os.environ.get("GATEWAY_URL")
    if not url:
        return None
    headers = None
    if os.environ.get("GATEWAY_TOKEN_URL"):
        headers = {"Authorization": f"Bearer {_gateway_token()}"}
    return MCPClient(url=url, headers=headers, prefix="gw")
