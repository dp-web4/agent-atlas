---
harness: OpenCode
ctx_provider: opencode
vendor: SST (opencode-ai)
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [tool.execute.before, permission.asked]
fails_open: false
config_path: ~/.config/opencode/opencode.json
config_format: json
fidelity: documented
sources:
  - https://opencode.ai/docs/plugins/
  - https://opencode.ai/docs/config/
  - https://ccusage.com/guide/opencode/
---

# Talk-to: OpenCode

**Fidelity: documented** - built from OpenCode's official plugin and config
docs; the plugin API and blocking mechanism are documented, the on-disk storage
layout is corroborated from a third-party reader.

## 1. Identity
- **Harness**: OpenCode ([SST / opencode-ai](https://opencode.ai/)), an
  open-source AI coding agent for the terminal.
- **ctx provider (read)**: `opencode`.
- **Lineage**: **independent.** It does *not* clone Claude Code's hook engine.
  Plugins are JavaScript/TypeScript modules that register async hook functions
  in-process; blocking is expressed by *throwing*, not by an exit code. Do not
  inherit the Claude fail-open model here.

## 2. Hook engine
- **Mechanism**: a plugin is a JS/TS module exporting hooks. Events include
  `tool.execute.before`, `tool.execute.after`, `permission.asked`,
  `permission.replied`, `session.*`, `message.*`, `file.edited`,
  `command.executed`, `lsp.*`, and TUI events.
- **Blocking-capable events**: `tool.execute.before` (and the `permission.asked`
  path). A hook blocks the tool call by **throwing an Error**; the thrown message
  surfaces as the reason and the tool does not run.
- **Failure mode**: **fails CLOSED on the execution path.** Because the block
  signal *is* a thrown exception, a hook that errors mid-decision also aborts the
  tool call. This is the opposite of the Claude lineage and is favorable for a
  gate. **Caveat — absence is still fail-open**: if the plugin fails to load or
  is never registered, there is simply no gate and the tool runs. So the gate is
  fail-closed *once wired*, but wiring/load must itself be verified.

## 3. Config
- **Path**: `~/.config/opencode/opencode.json` (global); project-local
  `.opencode/` and `opencode.json`.
- **Format**: JSON / JSONC.
- **Plugins**: dropped in `.opencode/plugins/` (or `~/.config/opencode/plugins/`),
  or referenced from the config's `plugin` array; relative paths resolve against
  the defining config file.

## 4. Transcript pointer
- **Path pattern**: `~/.local/share/opencode/storage/` (override with
  `OPENCODE_DATA_DIR`). Messages at
  `storage/message/<sessionID>/msg_<messageID>.json`; sessions at
  `storage/session/<projectHash>/<sessionID>.json`; also `part/` and
  `session_diff/`. **Note: per-message JSON files, not one JSONL per session.**
- These files are the read side's input.

## 5. Capabilities and caveats
- Full observe + gate: witness via `tool.execute.after`/`session.*`, gate via
  `tool.execute.before`.
- No automatic storage cleanup; the `message/` tree grows unbounded.
- Because blocking is exception-based, keep gate plugins minimal and let any
  internal error propagate — that propagation is the deny.
