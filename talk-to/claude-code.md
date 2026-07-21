# Talk-to: Claude Code

**Fidelity: verified** - Claude Code is the live reference gate the
[hestia claude-code plugin](https://github.com/dp-web4/hestia/tree/main/plugins/claude-code)
runs on; its hook path is exercised in production use. The fuller event list below
is documented from Claude Code's hook system; the blocking path and failure mode
are the verified, load-bearing parts.

## 1. Identity
- **Harness**: Claude Code (Anthropic).
- **ctx provider (read)**: `claude`.
- **Lineage**: this *is* the canonical hook engine that several other harnesses
  (Kimi, and other Claude-Code-lineage CLIs) clone. Descriptors for those can
  inherit this failure model.

## 2. Hook engine
- **Events**: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`,
  `SubagentStop`, `SessionStart`, `SessionEnd`, `PreCompact`, `Notification`.
- **Blocking-capable events**: `PreToolUse` (deny a tool call), `UserPromptSubmit`,
  and `Stop`, via exit code `2` or a `permissionDecision`/`decision` JSON on stdout.
  `PostToolUse` and the rest are observational.
- **Failure mode**: **fails open**, like the whole lineage. A blocking hook that
  errors, times out, or exits unexpectedly resolves to *allow*. **The gate must be
  fail-closed by construction**: deny by default, allow only on an explicit
  confirmed pass.

## 3. Config
- **Path**: `~/.claude/settings.json` (and project/local `settings.json`).
- **Format**: JSON. A `hooks` map keys each event to matchers and the command(s)
  to run; a `PreToolUse` matcher can scope by tool.
- **Knobs that matter**: hook precedence across user/project/local settings; keep
  the gate command in a stable, audited path.

## 4. Transcript pointer
- **Path pattern**: `~/.claude/projects/<encoded-cwd>/*.jsonl`, one JSONL file per
  session. This is the read side's input.
- **Notable fields**: per-turn tool calls and results; the witness side of the
  hestia plugin keys off `tool_name` and the tool payload.

## 5. Capabilities and caveats
- Full observe + gate: witness every tool call (`PostToolUse`) and gate the risky
  ones (`PreToolUse`). The hestia plugin does exactly this: hash-linked witness
  entries plus a fail-closed pre-tool gate.
- Because this is the lineage source, a new Claude-Code-clone harness usually needs
  only a thin descriptor that points here and notes its config path and any
  divergence.
