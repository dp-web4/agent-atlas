---
harness: Codex CLI
ctx_provider: codex
vendor: OpenAI
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, PermissionRequest, PostToolUse, UserPromptSubmit, SubagentStop, Stop]
fails_open: true
config_path: ~/.codex/config.toml
config_format: toml
fidelity: verified
sources:
  - https://learn.chatgpt.com/docs/hooks
  - https://learn.chatgpt.com/docs/plugins
  - https://learn.chatgpt.com/docs/sandboxing
  - https://github.com/openai/codex (codex-rs/core/src/tools/registry.rs; config/src/hook_config.rs; core-plugins/src/manifest.rs; linux-sandbox/README.md)
  - https://github.com/dp-web4/hestia/tree/main/plugins/codex
---

# Talk-to: Codex CLI

**Fidelity: verified** - the hook contract, plugin format, and sandbox behavior below are
source-verified against `codex-rs` and the installed binary (codex-cli 0.145.0), and a working
governance adapter is wired + config-validated ([hestia/plugins/codex](https://github.com/dp-web4/hestia/tree/main/plugins/codex)).
The one piece not yet exercised is a live model session firing the hooks (pends auth); everything
else — event dispatch, deny path, sandbox, plugin install — is confirmed.

## 1. Identity
- **Harness**: Codex CLI (OpenAI) — the Rust `codex-rs` binary, installed via `npm i -g @openai/codex`.
- **ctx provider (read)**: `codex`.
- **Lineage**: a genuine Claude-Code-lineage hook engine — same event names, same `exit 2` / stderr
  and `hookSpecificOutput.permissionDecision: "deny"` (and legacy `{"decision":"block"}`) contract, same
  stdin event JSON (`hook_event_name`, `tool_name`, `tool_input`, `cwd`, `session_id`). See
  [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Enable**: EXPERIMENTAL — off by default. Set `[features] codex_hooks = true` in `~/.codex/config.toml`
  (the binary maps the legacy alias `codex_hooks -> hooks`).
- **Events**: `SessionStart`, `SubagentStart`, `PreToolUse`, `PermissionRequest`, `PostToolUse`,
  `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`, `Stop`.
- **Blocking-capable**: `PreToolUse` (deny via exit `2` + stderr, or `permissionDecision: "deny"`),
  `PermissionRequest`, `PostToolUse` (`decision: "block"`), `UserPromptSubmit`, `SubagentStop`, `Stop`.
- **PreToolUse tool coverage (source-verified — a common blog claim of "Bash-only" is WRONG)**:
  PreToolUse dispatches centrally over every Function-payload tool (`registry.rs`), so it fires for the
  **shell** tool (`tool_name: "bash"`), **`apply_patch`** (file create/edit/delete), and **MCP** calls
  (`mcp__<server>__<tool>`). It does NOT fire for `tool_search`, custom/freeform-grammar tools, or a
  hosted/server-side `web_search`. Codex has no separate Edit/Write/Read tools: edits go through
  `apply_patch` (gated), reads via the shell tool (`cat`/`sed`, gated).
- **Failure mode**: **fails open** (verified from the docs: a hook that errors/times-out/exits-nonzero
  is "marked failed... and the tool call continues"). **The gate must be fail-closed by construction.**

## 3. Config, sandbox, and plugins
- **Config path/format**: `~/.codex/config.toml` (TOML). Hooks: inline `[[hooks.<Event>]]` tables OR a
  `hooks.json` (`{ "hooks": { "PreToolUse": [{ "matcher": "<regex>", "hooks": [{ "type": "command",
  "command": "...", "timeout": <s> }] }] } }`).
- **Sandbox = the structural boundary the hook can't be.** `sandbox_mode = "read-only" | "workspace-write"
  | "danger-full-access"`. Under `workspace-write`, writes are confined to the cwd + `/tmp` + any
  `[sandbox_workspace_write] writable_roots`, and network is off with `network_access = false`. **But the
  sandbox does NOT scope READS** — under workspace-write the whole FS is `--ro-bind / /` readable; there
  is no `readable_roots`. So write/egress scope is structural; read scope is not (needs a bind-mount /
  container). `approval_policy = "never" | "on-request" | ...`.
- **Plugins**: a native marketplace system. A plugin is `.codex-plugin/plugin.json` (JSON: `name`,
  `version`, `hooks` -> a `hooks.json`, `mcp_servers`, `skills`, `commands`); Codex injects
  `$CLAUDE_PLUGIN_ROOT` / `$PLUGIN_ROOT` for bundled scripts. Install from a local marketplace:
  `codex plugin marketplace add <path>` (manifest at `.agents/plugins/marketplace.json` in 0.145) then
  `codex plugin add <plugin>@<marketplace>` (one-time hook trust-review). `--dangerously-bypass-hook-trust`
  skips the trust *prompt*, not the hooks — so it does NOT bypass a gate.

## 4. Transcript pointer
- **Path pattern**: Codex writes session **rollout** files under `~/.codex/` (referenced internally as
  `rollout-*` / `rollout.persistence.*`). The `codex` ctx provider is the read-side authority for the
  concrete file shape.
- **Notable fields**: each hook is also passed `transcript_path` on stdin.

## 5. Capabilities and caveats
- **Defense-in-depth, not one gate** (each layer covers different acts): sandbox = write + egress boundary;
  PreToolUse gate = shell/apply_patch/MCP command gate (fail-closed); read-scope = the shell gate only
  (weak — relative-recursive traversal escapes string-parsing, same as the Kimi `find .` limit), so launch
  Codex in the task repo, not the workspace root.
- **Two approval surfaces** (`PreToolUse` + `PermissionRequest`) — a gate should cover both.
- **Fail-open + slow FS**: on WSL, keep hook scripts on local ext4, not a 9p `/mnt/c` path — a cold-load
  timeout would make the fail-open gate silently open.
- Reference adapter (this project): [hestia/plugins/codex](https://github.com/dp-web4/hestia/tree/main/plugins/codex).
