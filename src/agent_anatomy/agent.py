"""agent.py — the assembly point. Everything meets here.

An "agent" in Strands is: a model + a system prompt + tools + plugins.
The SDK runs the agent loop for us: send messages to the model, execute
any tool calls it makes, feed results back, repeat until the model
answers in plain text. That loop is the heart of every agentic CLI —
Kiro-CLI, Claude Code, and this toy all share it.

Model selection: Bedrock, Haiku-class by default (cheap + fast for many
small exploratory turns). Override with the AGENT_MODEL env var:

    AGENT_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0 uv run agent

That one line is Strands' whole model configuration story. Using Ollama
instead of Bedrock is a two-line swap — see README, "Escape hatch".
"""

import os
from pathlib import Path

from strands import Agent, AgentSkills
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

from .prompts import SYSTEM_PROMPT
from .tools import ALL_TOOLS

DEFAULT_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"


def build_agent(mcp_clients: list[MCPClient]) -> Agent:
    """Assemble the agent: model + prompt + tools + MCP + skills.

    The MCP clients must already be started (inside their `with` blocks —
    see cli.py). We ask each one for its tool list; those remote tools
    appear to the model exactly like our local @tool functions.
    """

    model = BedrockModel(
        model_id=os.environ.get("AGENT_MODEL", DEFAULT_MODEL),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )

    mcp_tools = [tool for client in mcp_clients for tool in client.list_tools_sync()]

    # Native Agent Skills (SKILL.md spec): the plugin lists each skill's
    # name+description in the system prompt and registers a `skills` tool
    # the model calls to load full instructions on demand — progressive
    # disclosure. Ask the agent to write a commit message, then check
    # /trace: you'll see the skills tool fire BEFORE it answers.
    skills = AgentSkills(skills=[str(SKILLS_DIR)])

    return Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[*ALL_TOOLS, *mcp_tools],
        plugins=[skills],
        callback_handler=None,  # cli.py consumes the result itself
    )
