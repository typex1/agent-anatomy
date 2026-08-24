"""agent-anatomy: a Kiro-CLI-inspired coding agent, small enough to read.

Reading path (see EXPLORING.md for guided questions):

    cli.py      -> the REPL: where your keystrokes become agent invocations
    agent.py    -> the assembly point: model + prompt + tools + MCP + skills
    prompts.py  -> the system prompt: the agent's entire "personality"
    tools/      -> the five built-in tools the model can call
    mcp_clients.py      -> connecting to MCP servers (remote HTTP + local stdio)
    skills/     -> SKILL.md files loaded on demand (in repo root)
"""

__version__ = "0.1.0"
