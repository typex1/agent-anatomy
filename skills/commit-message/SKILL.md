---
name: commit-message
description: Conventions for writing git commit messages in this project. Use whenever asked to commit changes or draft a commit message.
---

# Commit message conventions

Write commit messages in this exact style:

1. **Subject line**: imperative mood, lowercase type prefix, max 72 chars.
   Format: `type: short summary`
   Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`.
2. **Blank line**, then a body only when the change isn't self-evident:
   2–4 lines explaining WHY, not what (the diff shows what).
3. Never mention AI, agents, or tools in the message.
4. One logical change per commit. If asked to commit unrelated changes,
   propose splitting them first.

Example:

```
feat: add /trace command to the REPL

Makes the agent loop visible for students: shows which tools the
model called last turn without reading the raw message history.
```
