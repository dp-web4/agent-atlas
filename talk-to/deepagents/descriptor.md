---
harness: DeepAgents (CLI)
ctx_provider: deepagents
vendor: LangChain
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [wrap_tool_call, before_agent, after_agent, HITL-interrupt]
fails_open: false
subagent_hooks_inherited: untested
config_path: ~/.deepagents/config.toml
config_format: toml
resource_type: [local, api]
fidelity: documented
sources:
  - https://docs.langchain.com/oss/python/deepagents/customization
  - https://reference.langchain.com/python/deepagents-cli
  - https://deepwiki.com/langchain-ai/deepagents/2.2-creating-deep-agents
  - https://deepwiki.com/langchain-ai/deepagents/3-cli-reference
---

# Talk-to: DeepAgents (CLI)

**Fidelity: documented** - built from LangChain's official deepagents docs and API
reference; the gating is in-process Python middleware, so it was read, not run.

## 1. Identity
- **Harness**: DeepAgents - LangChain's "deep agents" SDK plus a terminal CLI
  (`deepagents_cli`, exposing a Textual TUI) built on LangGraph.
- **ctx provider (read)**: `deepagents`.
- **Lineage**: independent. This is **not** a shell-hook engine and shares no
  hook contract with Claude Code. Gating is done with Python **middleware**
  composed into the agent graph, not with external commands and exit codes.

## 2. Hook engine
- **Model**: middleware, not shell hooks. Middleware classes subclass
  `AgentMiddleware` and override hooks - `before_agent` / `after_agent`
  (turn-level), `wrap_model_call` (intercept the LLM call), and
  `wrap_tool_call` (intercept a tool invocation), each with async variants.
- **Blocking-capable**: yes, in-process. `wrap_tool_call` wraps the tool handler,
  so a middleware can refuse to call `handler(...)` and return a rejection instead
  of executing. Shipped middleware includes `ShellAllowListMiddleware` (deny shell
  commands outside an allowlist) and HITL gates
  (`AutoModeHITLMiddleware`, `AsyncApprovalHITLMiddleware`); `create_deep_agent`
  also takes `interrupt_on=` to **pause before a tool call for human approval**.
- **Failure mode**: **fails closed by construction**, unlike the shell-hook
  lineage. Because the gate is Python in the same process, a middleware that
  raises (or a HITL interrupt that is never approved) **aborts the turn - the tool
  does not execute**. There is no timeout-then-allow resolution to silently fall
  through: an erroring gate stops the call rather than permitting it. (Marked
  `fails_open: false` on that basis; it is a property of the middleware model, not
  an explicit "on error, deny" statement in the docs, so treat it as documented-
  by-mechanism rather than by promise.)

## 3. Config
- **Path**: `~/.deepagents/config.toml` (model preferences, provider/credential
  settings; loaded via `load_config_toml()`).
- **Format**: TOML. Note the *gating* is not configured here - it is expressed in
  Python by which middleware you compose into the agent (`create_deep_agent(...,
  middleware=[...])` / `create_cli_agent`). The TOML file is model/provider config,
  not a hook table.
- **Knobs that matter**: `interrupt_on=` for HITL tool approval;
  `ShellAllowListMiddleware` for shell gating; custom `wrap_tool_call` middleware
  for arbitrary allow/deny logic.

## 4. Transcript pointer
- **Storage**: session/thread state is persisted via SQLite (LangGraph
  checkpointer, `aiosqlite`), reached through `get_db_path()` / `get_checkpointer()`
  with threads listed via `list_threads()` (a `sessions.db`-style database). The
  exact filesystem path is not pinned in the docs - most likely under
  `~/.deepagents/`, but confirm against a live install. This is structured DB rows,
  not a JSONL transcript tree, so the read side must query the checkpointer rather
  than tail a file.

## 5. Capabilities and caveats
- Full observe **and** gate are available, but only in-process: to witness or block
  you register Python middleware, so a "talk-to" integration here is a library
  dependency, not an external command wired via config. That is a different
  integration shape from the shell-hook harnesses in this registry.
- Strength: because blocking is a raise/interrupt in the same process, it does not
  inherit the fail-open footgun of the Claude-Code shell-hook lineage. Caveat: it
  requires shipping code into the agent build, and transcript access means talking
  to a SQLite checkpointer rather than reading a session file.

## Sources
- Middleware/customization, wrap_tool_call, interrupt_on (HITL) - https://docs.langchain.com/oss/python/deepagents/customization
- CLI API reference (middleware classes, config.toml, threads) - https://reference.langchain.com/python/deepagents-cli
- Middleware system / creating deep agents - https://deepwiki.com/langchain-ai/deepagents/2.2-creating-deep-agents
- CLI reference (SQLite session storage, HITL) - https://deepwiki.com/langchain-ai/deepagents/3-cli-reference
