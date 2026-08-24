# agent-anatomy

**A Kiro-CLI-inspired coding agent, small enough to read.**

This is an educational project: a working terminal coding agent built with the
[Strands Agents SDK](https://strandsagents.com), designed to be *explored*, not
just used. Run it first, then read your way through the implementation —
[`EXPLORING.md`](EXPLORING.md) is your guide.

> Educational, Kiro-CLI-inspired, **not affiliated with AWS**. "Kiro" is a
> trademark of Amazon.com, Inc. This project clones the *ideas*, not the product.

## Quickstart

Requirements: [uv](https://docs.astral.sh/uv/), an AWS account with Bedrock
model access (see first-run trap below).

```bash
git clone https://github.com/typex1/agent-anatomy
cd agent-anatomy
uv run agent
```

That's it — `uv` resolves Python and dependencies on first run.

Try these in the REPL:

```
you> what time is it in UTC+2?                     # local stdio MCP server
you> what's the max Lambda timeout? check AWS docs # remote AWS Knowledge MCP
you> read cli.py and explain the REPL loop         # read_file tool
you> draft a commit message for my staged changes  # skill loading, visible in /trace
/trace                                             # see which tools just fired
```

### First-run trap: Bedrock model access

The default model is Anthropic **Claude Haiku 4.5** via a cross-region
inference profile (`us.anthropic.claude-haiku-4-5-20251001-v1:0`) in
`us-east-1`. Before first use you must **enable model access** in the AWS
console: *Bedrock → Model access → Manage model access → Anthropic*. Cheap and
fast — an evening of exploring costs cents.

Override model or region with environment variables:

```bash
AGENT_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0 uv run agent
AWS_REGION=eu-central-1 uv run agent
```

### Escape hatch: no AWS account

Strands swaps model providers in two lines. In `src/agent_anatomy/agent.py`,
replace `BedrockModel(...)` with:

```python
from strands.models.ollama import OllamaModel
model = OllamaModel(host="http://localhost:11434", model_id="qwen3:8b")
```

(`uv add 'strands-agents[ollama]'` first.)

## Architecture

```
 you ──► cli.py (REPL) ──► agent.py (the agent loop, run by Strands)
                              │
              ┌───────────────┼──────────────────┐
              ▼               ▼                  ▼
          tools/          mcp_clients.py             skills/
       5 local tools   2 MCP servers      SKILL.md files,
      read_file etc.  ┌────────────┐    loaded on demand by
                      │ AWS Knowledge│   the native AgentSkills
                      │ (remote HTTP)│   plugin (progressive
                      │ clock server │   disclosure)
                      │ (local stdio)│
                      └────────────┘
                              ▲
                 mcp_servers/clock_server.py
                 (~30 lines — the server side)
```

**Reading path:** `cli.py` → `agent.py` → `prompts.py` → `tools/file_read.py` →
`tools/shell.py` → `mcp_clients.py` → `mcp_servers/clock_server.py` → `skills/*/SKILL.md`.
Every file is 30–120 lines and starts with a docstring explaining its role.

## What this teaches

| Concept | Where |
|---|---|
| The agent loop (model ↔ tools until done) | `agent.py`, visible via `/trace` |
| Tools = schema in, string out | `tools/` — five examples, one shape |
| Human-in-the-loop safety | `tools/shell.py` — the y/n prompt IS the safety model |
| MCP, both transports | `mcp_clients.py` (client), `mcp_servers/clock_server.py` (server) |
| Agent Skills / progressive disclosure | `skills/`, native `AgentSkills` plugin |
| System prompts are just strings | `prompts.py` — read every word the model sees |
| Context management | `/clear` + the section below |

### Context management (the part we deliberately did NOT build)

Real agentic CLIs live or die by context handling: every tool result stays in
the conversation, so long sessions fill the model's context window. Kiro-CLI
and Claude Code handle this with **compaction** — summarizing older turns into
a shorter digest and dropping the originals. We ship only `/clear` (wipe
history) because compaction code would be the most complex module in this repo
and drown the concepts it exists to teach. When your session gets long and
slow, that's the problem compaction solves — now you know why it exists.

### How does Kiro-CLI do all this?

Same anatomy, industrial strength: a large system prompt with detailed
tool-usage policy, ripgrep-backed search, an approval/trust model per tool
("Allow this action?"), MCP client support, steering files for persistent
context, and compaction. Rebuilding the small version is the fastest way to
read the big ones.

## Chapter 2: to the cloud (AgentCore Runtime + Gateway)

The `agentcore-runtime` branch content promotes the same agent from laptop
REPL to managed cloud service — with the **AgentCore CLI** (`npm i -g
@aws/agentcore-cli`), which deploys via CDK:

```
 laptop:  you ──► cli.py (REPL) ──────────► build_agent()
 cloud:   POST /invocations ──► runtime.py ──► build_agent()   (same!)
                                                  │
    ┌──────────────┬────────────────────────────┬─┘
    ▼              ▼                            ▼
 clock server   AWS Knowledge          AgentCore Gateway ──► Lambda
 (stdio, in     (remote HTTP,          (remote HTTP, YOURS)   aws_lookup
  container)     managed by AWS)        gateway/aws_lookup/   tools
```

New files to read, in order:

1. `src/agent_anatomy/runtime.py` — the cloud face: HTTP entrypoint instead
   of a REPL. Note `run_command` is **excluded**: human-in-the-loop safety
   does not survive the removal of the human.
2. `gateway/aws_lookup/handler.py` — a Lambda that *is* two MCP tools yet
   contains zero MCP code. Gateway does all protocol translation; the tool
   schema lives separately in `gateway/aws_lookup_schema.json`.
3. `src/agent_anatomy/mcp_clients.py` (bottom) — the third answer to "where does an
   MCP tool live?": nowhere, until invoked.

Deploy story (`agentcore/` holds the project config):

```bash
npm install -g @aws/agentcore-cli
agentcore deploy          # CDK: runtime + gateway + target (~8 resources)
agentcore invoke "which AWS account are you running in?"
agentcore logs            # CloudWatch, streamed
```

To use the gateway tools from the *local* REPL too:

```bash
GATEWAY_URL=https://<your-gateway-id>.gateway.bedrock-agentcore.<region>.amazonaws.com/mcp uv run agent
```

The demo gateway deploys with `authorizerType: NONE` to keep the lesson
focused. Real deployments should use `CUSTOM_JWT` — see the note in
`mcp_clients.py` about the client-credentials flow (the code is already there).

## License

Apache-2.0 — matching the Strands Agents SDK this project teaches.
