---
harness: Codex CLI
ctx_provider: codex
vendor: OpenAI
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, PermissionRequest, UserPromptSubmit]
fails_open: true
config_path: ~/.codex/config.toml
config_format: toml
fidelity: documented
sources:
  - https://learn.chatgpt.com/docs/hooks
  - https://developers.openai.com/codex/config-advanced
  - https://github.com/openai/codex/blob/main/docs/config.md
  - https://github.com/falcosecurity/prempti/blob/main/hooks/codex/README.md
---

# Talk-to: Codex CLI

**Fidelity: documented** - built from OpenAI's official Codex hooks and config
docs; the failure mode is not stated by OpenAI and is inferred from the
Claude-Code lineage the engine copies.

## 1. Identity
- **Harness**: Codex CLI (OpenAI).
- **ctx provider (read)**: `codex`.
- **Lineage**: a Claude-Code-lineage hook engine. The event names, the
  `exit 2`-blocks convention, and the `permissionDecision: "deny"` / `decision:
  "block"` JSON contract are the Claude Code model; see
  [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events**: `SessionStart`, `SubagentStart`, `PreToolUse`, `PermissionRequest`,
  `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStop`,
  `Stop`.
- **Blocking-capable events**: `PreToolUse` (deny a tool call via exit code `2`
  with stderr, or JSON `"permissionDecision": "deny"`), `PermissionRequest`
  (JSON `"behavior": "deny"`), and `UserPromptSubmit` (exit `2`, or JSON
  `"decision": "block"`). `PostToolUse` can only replace/annotate a result after
  the tool already ran; the rest are observational.
- **Failure mode**: OpenAI's docs do not state fail-open vs fail-closed. Because
  the engine is a Claude-Code clone, **treat it as fails open**: a blocking hook
  that errors, times out, or exits unexpectedly resolves to *allow*. **The gate
  must be fail-closed by construction** - deny by default, reach `exit 0` only on
  an explicit confirmed pass. (Falco's third-party `prempti` interceptor makes
  itself fail-closed and offers `PREMPTI_FAIL_OPEN=1`, which is exactly the
  build-your-own-fail-closed posture the lineage requires.)

## 3. Config
- **Path**: `~/.codex/config.toml`. Hooks are discovered next to active config
  layers as either a standalone `hooks.json` or an inline `[hooks]` table inside
  `config.toml`.
- **Format**: TOML for `config.toml`; JSON for `hooks.json`. Higher-precedence
  layers add hooks rather than replacing lower-precedence ones, so all matching
  hooks run.
- **Knobs that matter**: project-local `.codex/config.toml` ignores some keys
  (e.g. `notify`); keep the gate command in a stable, audited path.

## 4. Transcript pointer
- **Path pattern**: Codex writes session rollout/history under `~/.codex/`
  (session logs), but the exact per-session transcript path/format is not nailed
  down here. The `codex` ctx provider is the read-side authority for the concrete
  file shape.

## 5. Capabilities and caveats
- Full observe + gate: witness tool calls with `PostToolUse` and gate risky ones
  with `PreToolUse` / `PermissionRequest`.
- Two distinct approval surfaces (`PreToolUse` and `PermissionRequest`) mean a
  gate should cover both, not just `PreToolUse`.
- Thin descriptor by lineage: divergence from Claude Code is mostly the config
  location (TOML at `~/.codex/`) and the extra `PermissionRequest` /
  `PostCompact` events.
