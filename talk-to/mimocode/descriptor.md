---
harness: MiMo Code
ctx_provider: mimocode
vendor: Xiaomi
lineage: opencode
hook_engine: true
blocking_capable: true
blocking_events: [tool.execute.before]
fails_open: unknown
config_path: ~/.config/mimocode/mimocode.jsonc
config_format: jsonc
fidelity: documented
sources:
  - https://github.com/XiaomiMiMo/MiMo-Code
  - https://opencode.ai/docs/plugins/
  - https://github.com/anomalyco/opencode/issues/5894
---

# Talk-to: MiMo Code

**Fidelity: documented** - MiMo Code's own README documents it as an OpenCode fork
that keeps OpenCode's plugin system, and OpenCode's plugin docs document the hook
events and the throw-to-block mechanism. The exact fail-open/closed behavior on an
unexpected hook error is not documented upstream and is left `unknown`.

## 1. Identity
- **Harness**: MiMo Code / MiMoCode ([Xiaomi](https://github.com/XiaomiMiMo/MiMo-Code)) -
  a terminal-native (TUI + Web UI + non-interactive) CLI coding agent, installable
  via `npm i -g @mimo-ai/cli`, talking to the MiMo API over an Anthropic-compatible
  interface. **NOT a Claude-Code clone** despite the Anthropic-compatible wire.
- **ctx provider (read)**: `mimocode`.
- **Lineage**: **`opencode`** - the README states MiMoCode is "built as a fork of
  OpenCode," inheriting OpenCode's providers, TUI, LSP, MCP, and **plugin system**,
  and adding persistent memory, subagent orchestration, goal-driven loops, and
  self-improvement (dream/distill). Its gate surface is OpenCode's plugin/event
  bus, **not** the Claude-Code `settings.json` hook engine.

## 2. Hook engine
- **Model**: OpenCode plugins are JavaScript/TypeScript modules that subscribe to
  an event bus and to tool-lifecycle hooks - there is no `exit 2` shell-hook
  convention here. The blocking primitive is a hook that **throws**.
- **Events**: OpenCode exposes a broad bus - `tool.execute.before`,
  `tool.execute.after`, `permission.asked`, `permission.replied`,
  `session.created`/`.idle`/`.updated`/`.error`/`.compacted`, `file.edited`,
  `message.*`, `command.executed`, `lsp.*`, `todo.updated`, `tui.*`, and more.
- **Blocking-capable events**: **`tool.execute.before`** - throwing an error from
  this hook prevents the tool from running (the canonical example blocks reading
  `.env` files). Config-side, per-tool `permission` = allow/ask/deny also gates
  tools. `tool.execute.after` and the rest are observational.
- **Failure mode**: **`unknown` - and the nuance matters.** Because the block
  primitive *is* "throw = deny," a hook that errors tends to **deny** the gated
  call (fail-closed-ish for the hooked path) - the opposite of the Claude
  lineage's fail-open. **But** OpenCode has documented **bypass holes** that fail
  open at the architecture level: `tool.execute.before` does **not** intercept
  tool calls made by subagents spawned via the task tool
  ([issue #5894](https://github.com/anomalyco/opencode/issues/5894), a security-
  policy bypass), and config `deny` permissions have been reported ignored under
  the SDK ([issue #6396](https://github.com/anomalyco/opencode/issues/6396)).
  **Consequence: a gate here must both throw-to-deny by default AND account for
  the unhooked subagent path** - do not assume `tool.execute.before` sees every
  tool call. Confirm the specific MiMoCode build's subagent behavior on a live
  session before trusting the gate.

## 3. Config
- **Path**: `~/.config/mimocode/mimocode.jsonc` (global) and
  `.mimocode/mimocode.jsonc` (project); `.json` is also accepted. Plugins live as
  JS/TS files in the OpenCode plugin dirs (`.opencode/plugins/` /
  `~/.config/opencode/plugins/` upstream; MiMoCode may relocate under
  `.mimocode/` - verify on the build).
- **Format**: JSON/JSONC, with a published `$schema` auto-injected for
  autocomplete/validation. Plugin code is TypeScript/JavaScript, not declarative
  config.
- **Knobs that matter**: the `permission` block (allow/ask/deny per tool) is the
  declarative gate; plugins are the programmable gate. Runtime state (SQLite DB,
  memory files) lives under XDG paths or `$MIMOCODE_HOME`.

## 4. Transcript pointer
- **Path pattern**: not documented in the README. State lives under XDG paths (or
  `$MIMOCODE_HOME`) including a SQLite database and memory files; OpenCode upstream
  stores session data under `~/.local/share/opencode/`, so the MiMoCode analog is
  likely `~/.local/share/mimocode/` - but this is **inferred/unknown**. ctx is the
  read-side authority; confirm on a live session.

## 5. Capabilities and caveats
- Observe with `tool.execute.after` / session events; gate with a
  `tool.execute.before` plugin that throws on disallowed calls, plus a
  `permission: deny` policy as belt-and-suspenders.
- **This is the batch's odd one out**: OpenCode lineage, not Claude lineage. Do
  not port a Claude-Code `settings.json` `exit 2` gate here - it will not run. You
  write a TS/JS plugin instead.
- **Known bypass**: subagent (task-tool) tool calls can escape
  `tool.execute.before`. Any real gate must treat that as an open path until the
  specific build is verified to route subagent calls through the hook.
