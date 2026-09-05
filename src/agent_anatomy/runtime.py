"""runtime.py — the agent's cloud face (AgentCore Runtime entrypoint).

Chapter 2 of the anatomy lesson. Locally, cli.py wraps the agent in a
REPL: stdin in, rich panels out. On AgentCore Runtime there is no
terminal — the runtime invokes your agent over HTTP:

    POST /invocations   {"prompt": "..."}   ->  response text

Same agent, different skin. Note what had to change and what didn't:

  unchanged: model, prompt, tools, skills, MCP clients — build_agent()
  changed:   the interface (HTTP instead of REPL) and one safety rule —
             run_command is EXCLUDED below, because the y/n approval
             prompt in tools/shell.py needs a human at a keyboard and
             up there, there isn't one. Human-in-the-loop safety does
             not survive the removal of the human.

Run locally against the same HTTP contract with:  agentcore dev
"""

import sys
from pathlib import Path

# Packaging reality: the CodeZip build unpacks the whole repo at
# /var/task and runs this file as a script — nothing installs the
# package, so `src/` is not on Python's import path. On a laptop,
# `uv run` does this for you (via pyproject.toml); in the cloud we do
# it ourselves. One line, but it is the difference between "works on
# my machine" and works.
sys.path.insert(0, str(Path(__file__).parent.parent))

from bedrock_agentcore import BedrockAgentCoreApp

from agent_anatomy.agent import build_agent
from agent_anatomy.mcp_clients import aws_knowledge_client, clock_client, gateway_client
from agent_anatomy.tools import ALL_TOOLS
from agent_anatomy.tools.shell import run_command

app = BedrockAgentCoreApp()

# Cloud toolset: everything except the human-in-the-loop shell tool.
CLOUD_TOOLS = [t for t in ALL_TOOLS if t is not run_command]

# Lazy singleton: AgentCore Runtime requires initialization to finish
# within 30 seconds, and starting three MCP connections (HTTP session,
# stdio subprocess, gateway) can blow that budget on a cold start. So
# the module imports instantly and the agent is assembled on the FIRST
# invocation instead — a classic serverless trade: pay on first request,
# not at boot. Connections then live for the container's lifetime.
_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        clients = [aws_knowledge_client(), clock_client()]
        gateway = gateway_client()
        if gateway is not None:
            clients.append(gateway)
        for c in clients:
            c.start()
        _agent = build_agent(clients, tools=CLOUD_TOOLS)
    return _agent


@app.entrypoint
def invoke(payload: dict) -> str:
    """One HTTP invocation = one agent turn."""
    return str(_get_agent()(payload.get("prompt", "")))


if __name__ == "__main__":
    app.run()
