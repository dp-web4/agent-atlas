---
harness: Droid (Factory.ai)
ctx_provider: factory_ai_droid
vendor: Factory.ai
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, Stop]
fails_open: true
config_path: ~/.factory/hooks.json
config_format: json
fidelity: documented
sources:
  - https://docs.factory.ai/cli/configuration/hooks-guide
  - https://deepwiki.com/factory-ai/factory/4-cli-reference
---

# Talk-to: Droid (Factory.ai)

**Fidelity: documented** - built from Factory's official CLI hooks guide; the
failure mode is inferred from Claude lineage because the docs do not state it.

## 1. Identity
- **Harness**: Droid, Factory.ai's agentic coding CLI.
- **ctx provider (read)**: `factory_ai_droid`.
- **Lineage**: **a Claude-Code-lineage clone.** The event set is Claude Code's nine
  events verbatim, the `hooks.json` layout is `hooks > EventName > matchers >
  command` arrays, and `exit 2` denies — see
  [`../claude/descriptor.md`](../claude/descriptor.md). It inherits the lineage
  failure model.

## 2. Hook engine
- **Events**: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Notification`,
  `Stop`, `SubagentStop`, `PreCompact`, `SessionStart`, `SessionEnd`.
- **Blocking-capable events**: `PreToolUse` blocks tool calls (documented: it "runs
  before tool calls and can block them while providing Droid feedback"), using
  `exit 2` to deny; `Stop` can hold the agent. The rest are observational.
- **Failure mode**: **inferred FAILS OPEN.** Factory's docs do not state what
  happens on hook timeout, error, or unexpected non-zero exit — a gap worth flagging.
  Because Droid clones Claude Code's engine, the safe assumption is the lineage
  default: a broken blocking hook resolves to *allow*. **Treat the gate as the
  fail-closed party**: default to `exit 2`, reach `exit 0` only on a confirmed pass,
  and do not trust the engine to deny for you until this is verified live.

## 3. Config
- **Path**: `~/.factory/hooks.json` (user level); a project-scoped `.factory/`
  directory is also supported ("no configuration needed beyond copying the
  `.factory/` directory").
- **Format**: JSON, keyed by event name to matcher/command arrays.
- **Knobs that matter**: hook commands must use absolute paths or the
  `$FACTORY_PROJECT_DIR` variable — relative paths are explicitly warned against.

## 4. Transcript pointer
- **Path pattern**: not documented in the official hooks guide. The `SessionStart`/
  `SessionEnd`/`PostToolUse` events carry per-turn data and are the practical
  observation surface; ctx is the read-side authority for locating any on-disk
  session log.

## 5. Capabilities and caveats
- Observe without risk via the non-blocking events (`SessionStart`, `PostToolUse`,
  `SessionEnd`); gate via `PreToolUse`.
- **Documentation gap**: the fail-open/closed behavior is unstated by the vendor.
  Until confirmed against the live binary, assume fail-open and make the gate itself
  deny-by-default.
