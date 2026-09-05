# Exploring agent-anatomy

Run the agent first (`uv run agent`), play for five minutes, then work through
these questions module by module. Answers are collapsed — try before peeking.
Follow the reading path: each module assumes you've read the previous ones.

---

## 1. `cli.py` — the REPL

**Q1.** Where exactly does your typed message enter the agent? Find the single
line where the REPL hands off to the model.

<details><summary>Answer</summary>

`result = agent(line)` in `repl()`. Everything else — tool calls, MCP
round-trips, skill loading — happens inside that call, driven by Strands.
</details>

**Q2.** `/tools` and `/trace` are handled with `continue` before the agent is
called. Why must slash commands never reach the model?

<details><summary>Answer</summary>

They're UI, not conversation. If `/clear` were sent as a message, the model
would *talk about* clearing history instead of the history actually being
cleared — and the command text would pollute the context it's meant to manage.
</details>

**Q3.** Why are the MCP clients opened in a `with` block *around* the REPL,
rather than inside `build_agent()`?

<details><summary>Answer</summary>

The connections are stateful resources: the stdio client owns a live
subprocess, the HTTP client a session. They must outlive every agent call and
be cleaned up on exit — the context manager ties their lifetime to the REPL's.
</details>

## 2. `agent.py` — the assembly point

**Q4.** Where does a tool result re-enter the model's context? Find the
mechanism (careful: it's not in this repo's code).

<details><summary>Answer</summary>

Nowhere in this repo — that's the point. The Strands event loop appends each
tool result as a `toolResult` content block in a new message and re-invokes the
model. Use `/trace` to see the evidence; the loop itself lives in the SDK
(`strands/event_loop/`).
</details>

**Q5.** Rank the twelve-ish tools the model sees by where they come from
(`/tools` shows the merged list). How many sources are there?

<details><summary>Answer</summary>

Three: five local `@tool` functions from `tools/`, MCP tools from the two
servers (prefixed `aws_` and `clock_`), and the `skills` tool injected by the
`AgentSkills` plugin.
</details>

**Q6.** Change the default model to full strength (Sonnet-class) without
editing any code.

<details><summary>Answer</summary>

`AGENT_MODEL=us.anthropic.claude-sonnet-4-5-20250929-v1:0 uv run agent` — the
env var is read in `build_agent()`.
</details>

## 3. `prompts.py` — the system prompt

**Q7.** The prompt says "Before modifying a file, read it first." Is that
enforced anywhere in code? What kind of rule is it?

<details><summary>Answer</summary>

Not enforced — it's a *soft* behavioral instruction the model usually follows.
Compare with the shell approval prompt, which is *hard* (code, not prompt).
Deciding which rules deserve code is the core safety design question.
</details>

## 4. `tools/` — the five built-ins

**Q8.** All five tools return a plain string, even errors ("Error: ... is not a
file"). Why return error text instead of raising an exception?

<details><summary>Answer</summary>

The string goes back into the model's context, so the model can *react* — try
another path, ask the user. A raised exception would crash the loop; an error
message is information.
</details>

**Q9.** In `shell.py`, who decides *what* runs and who decides *whether* it
runs? Deny a command and watch what the model does with your denial.

<details><summary>Answer</summary>

The model composes the command; the human approves it. On denial the tool
returns "User DENIED this command..." — which the model reads and adapts to,
usually by asking you how to proceed. The denial is just another tool result.
</details>

**Q10.** `web_search` and `search` have nearly identical shapes but totally
different data sources. What does the model know about the difference?

<details><summary>Answer</summary>

Nothing except the schema (name, description, parameters). Implementation is
invisible — every tool is schema in, string out. That's why docstrings are
written for the model.
</details>

## 5. `mcp_clients.py` + `mcp_servers/clock_server.py` — the protocol, both sides

**Q11.** The AWS Knowledge connection is one URL; the clock connection names a
command to launch. What does that tell you about the two transports?

<details><summary>Answer</summary>

Remote streamable-HTTP servers run elsewhere (AWS manages this one); you just
connect. Stdio servers are subprocesses the *client* launches, speaking
JSON-RPC over stdin/stdout. Same protocol above the transport line — the model
can't tell the difference (check `/tools`).
</details>

**Q12.** Kill test: what happens to the clock subprocess when you `/quit`?
Verify with `ps` before and after.

<details><summary>Answer</summary>

It dies with the client: exiting the `with` block in `cli.py` closes the stdio
transport and reaps the subprocess. Tool lifetime = connection lifetime.
</details>

**Q13.** Add a `days_until(date: str)` tool to the clock server. How many
files do you need to touch?

<details><summary>Answer</summary>

One — `mcp_servers/clock_server.py`. The client discovers tools at connect
time via `list_tools`; nothing in the agent hardcodes the tool list.
</details>

## 6. `skills/` — progressive disclosure

**Q14.** Ask the agent to draft a commit message, then run `/trace`. What
fired before it answered, and why wasn't the full SKILL.md in context from the
start?

<details><summary>Answer</summary>

The `skills` tool fired to load `commit-message`. Only each skill's
name+description sits in the system prompt permanently; full instructions load
on demand. That's progressive disclosure: pay tokens only for skills you use.
</details>

**Q15.** The two shipped skills differ structurally. What does
`aws-well-architected` have that `commit-message` doesn't, and when is it read?

<details><summary>Answer</summary>

A `references/pillars.md` resource file, read only when the skill is active.
Skills can bundle scripts/references/assets — instructions are just the entry
point.
</details>

**Q16.** Write your own skill: create `skills/explain-like-im-five/SKILL.md`
(frontmatter: `name`, `description`; body: "explain using only everyday
analogies, max 3 sentences"). Restart, ask for an ELI5 of MCP, check `/trace`.

<details><summary>Answer</summary>

If the skill fired: congratulations, you've extended the agent without
touching a line of Python. If not: check your `description` — it's the only
thing the model sees when deciding to load a skill. That description IS the
trigger.
</details>

## 7. Chapter 2: `runtime.py` + `gateway/` — the cloud

**Q17.** `runtime.py` builds the agent with `CLOUD_TOOLS` — every tool
except `run_command`. Why can't the shell tool simply keep its y/n prompt in
the cloud?

<details><summary>Answer</summary>

The prompt reads from a terminal (`Confirm.ask`), and an AgentCore Runtime
container has no interactive stdin — nobody is there to answer. The honest
options are: drop the tool (chosen), auto-deny, or build an out-of-band
approval channel (what real products do). Human-in-the-loop requires a human.
</details>

**Q18.** `gateway/aws_lookup/handler.py` implements two MCP tools but
imports nothing MCP-related. Where do JSON-RPC, the tool schema, and
transport live?

<details><summary>Answer</summary>

In the Gateway (managed service) and in `aws_lookup_schema.json` (registered
at deploy time). The Lambda receives plain arguments as its event, plus the
tool name in `context.client_context`. Contract and code are separate
artifacts — compare with `@tool`, where the docstring IS the contract.
</details>

**Q19.** One Lambda serves both `aws_account_info` and `region_location`.
How does it know which tool was called, and what prefix does the agent see
on the tool names?

<details><summary>Answer</summary>

Gateway passes `bedrockAgentCoreToolName` in the Lambda client context,
prefixed with the target name (`aws-lookup___aws_account_info`); our
`MCPClient(prefix="gw")` adds another layer: `gw_aws-lookup___aws_account_info`
in `/trace`. Names are namespaced at every hop so tools from different
sources can't collide.
</details>

**Q20.** The same `build_agent()` serves both `cli.py` and `runtime.py`.
List everything that changed between laptop and cloud — and everything that
didn't.

<details><summary>Answer</summary>

Changed: the interface (REPL → HTTP `/invocations`), the toolset (no
`run_command`), connection lifetime (per-`with`-block → container lifetime),
and who provides credentials (your profile → the runtime's execution role).
Unchanged: model, system prompt, skills, all other tools, both MCP clients,
and the agent loop itself. The anatomy is portable; only the skin changes.
</details>

---

**Where next?** Read the Strands event loop source (`.venv/lib/.../strands/event_loop/`),
then compare with what you can observe of Kiro-CLI or Claude Code. The anatomy
is the same — only the muscle mass differs.
