"""cli.py — the REPL. Start reading HERE.

This is where your keystrokes become agent invocations. The loop is:

    read a line -> agent(line) -> stream the reply -> repeat

Everything else (tool execution, MCP round-trips, skill loading) happens
inside `agent(...)` — follow the imports into agent.py to see how.

Slash commands (handled here, never sent to the model):
    /tools   list every tool the model can currently call
    /trace   show the tool calls made in the previous turn
    /clear   wipe the conversation history (fresh context window)
    /quit    exit
"""

import sys
from contextlib import ExitStack

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .agent import build_agent
from .mcp_clients import aws_knowledge_client, clock_client, gateway_client

console = Console()

BANNER = """[bold cyan]agent-anatomy[/] — a coding agent small enough to read
model responses stream below; [bold]/tools /trace /clear /quit[/]"""


def show_tools(agent) -> None:
    for name in sorted(agent.tool_names):
        console.print(f"  [green]{name}[/]")


def show_trace(agent) -> None:
    """Walk the raw message history and print the tool calls the model
    made last turn — the agent loop, made visible."""
    calls = [
        (block["toolUse"]["name"], block["toolUse"]["input"])
        for msg in agent.messages
        for block in msg.get("content", [])
        if isinstance(block, dict) and "toolUse" in block
    ]
    if not calls:
        console.print("  (no tool calls yet)")
    for name, args in calls[-10:]:
        console.print(f"  [yellow]{name}[/] {str(args)[:120]}")


def repl(agent) -> None:
    while True:
        try:
            line = console.input("\n[bold blue]you>[/] ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue
        if line in ("/quit", "/exit"):
            break
        if line == "/tools":
            show_tools(agent)
            continue
        if line == "/trace":
            show_trace(agent)
            continue
        if line == "/clear":
            agent.messages.clear()
            console.print("[dim]history cleared — the model now remembers nothing[/]")
            continue

        with console.status("[dim]thinking...[/]"):
            result = agent(line)
        console.print(Panel(Markdown(str(result)), border_style="dim"))


def main() -> None:
    console.print(BANNER)

    # MCP connections are context managers: the remote HTTP session and
    # the clock server subprocess live exactly as long as this block.
    # The gateway client only exists once deployed + configured (env vars).
    clients = [aws_knowledge_client(), clock_client()]
    gw = gateway_client()
    if gw is not None:
        clients.append(gw)
    try:
        with ExitStack() as stack:
            for c in clients:
                stack.enter_context(c)
            agent = build_agent(clients)
            repl(agent)
    except Exception as e:
        console.print(f"[red]startup failed:[/] {e}")
        sys.exit(1)
    console.print("[dim]bye[/]")


if __name__ == "__main__":
    main()
