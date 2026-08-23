"""The system prompt — the agent's entire "personality" in one readable string.

Kiro-CLI's real system prompt is thousands of tokens of instructions,
tool-usage rules, and safety policy baked into the binary. Ours is short
on purpose: you should be able to read ALL the words the model sees.

How does Kiro do this? The same way — a system prompt is just a string
sent with every request. There is no magic. Longer prompts buy more
consistent behavior at the cost of tokens (and readability).
"""

SYSTEM_PROMPT = """\
You are agent-anatomy, a small coding agent running in a terminal REPL.
You help the user inspect and modify files, run commands, and research
questions, using the tools provided.

Rules:
- Prefer tools over guessing. If the user asks about a file, read it.
- Before modifying a file, read it first.
- Shell commands require user approval; keep them short and purposeful.
- When you used web_search or an MCP tool to answer, say so briefly.
- Be concise. This is a terminal, not an essay.
"""
