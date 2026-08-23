"""run_command — the dangerous tool, and therefore the interesting one.

The model can ask for ANY shell command. The y/n prompt below is the
entire safety model of this agent: a human in the loop. This is exactly
what Kiro-CLI does when it asks "Allow this action?" — trust is a UI
problem before it is an AI problem.

Note the asymmetry: the MODEL decides what to run, the HUMAN decides
whether it runs. The returned string (stdout/stderr/exit code, or the
rejection message) goes straight back into the model's context — that's
how it "sees" the result and reacts to a denial.
"""

import subprocess

from rich.console import Console
from rich.prompt import Confirm

from strands import tool

console = Console()

TIMEOUT_SECONDS = 60


@tool
def run_command(command: str) -> str:
    """Run a shell command and return its output. The user must approve
    each command before it executes; it may be denied.

    Args:
        command: The shell command to execute (bash).
    """
    console.print(f"\n[bold yellow]agent wants to run:[/] [bold]{command}[/]")
    if not Confirm.ask("Allow?", default=False):
        return "User DENIED this command. Ask them how to proceed instead."

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return f"Command timed out after {TIMEOUT_SECONDS}s."

    out = (result.stdout + result.stderr).strip()
    if len(out) > 10_000:
        out = out[:10_000] + "\n... [truncated]"
    return f"exit code: {result.returncode}\n{out or '(no output)'}"
