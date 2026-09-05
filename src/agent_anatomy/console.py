"""One shared Console — and a spinner that knows when to get out of the way.

Rich's `console.status(...)` runs a live spinner on a background thread
that constantly redraws its line. If a tool prints a question and waits
for input while the spinner is running (shell.py's "Allow?" prompt), the
animation overwrites the prompt: the agent looks stuck "thinking..."
while it is actually waiting for a keypress you never saw.

The fix is a tiny bit of shared state: `status(...)` remembers the live
spinner, and `suspend_status()` lets any tool stop it, talk to the human,
and restart it afterwards. UI plumbing, not AI — but it IS the
human-in-the-loop path, so it has to be visible.
"""

from contextlib import contextmanager

from rich.console import Console

console = Console()

_active_status = None


@contextmanager
def status(message: str):
    """Like console.status(...), but registers the spinner so tools can
    suspend it while they prompt the user."""
    global _active_status
    with console.status(message) as s:
        _active_status = s
        try:
            yield s
        finally:
            _active_status = None


@contextmanager
def suspend_status():
    """Pause the live spinner (if any) so prompts and input are visible."""
    if _active_status is not None:
        _active_status.stop()
    try:
        yield
    finally:
        if _active_status is not None:
            _active_status.start()
