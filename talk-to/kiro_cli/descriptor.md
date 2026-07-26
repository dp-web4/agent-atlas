---
harness: Kiro (AWS)
ctx_provider: kiro_cli
vendor: AWS (Amazon)
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, UserPromptSubmit, PreTaskExec]
fails_open: true
subagent_hooks_inherited: untested
config_path: .kiro/agents/*.json (CLI) / .kiro/hooks/*.json (IDE)
config_format: json
fidelity: documented
sources:
  - https://kiro.dev/docs/hooks/
  - https://kiro.dev/docs/cli/hooks/
  - https://kiro.dev/docs/cli/custom-agents/configuration-reference/
  - https://kiro.dev/changelog/ide/0-9/
---

# Talk-to: Kiro (AWS)

**Fidelity: documented** - from Kiro's official IDE and CLI hooks docs and the
agent configuration reference; not exercised live by this registry.

## 1. Identity
- **Harness**: Kiro ([kiro.dev](https://kiro.dev), AWS/Amazon), a spec-driven
  agentic IDE plus a `kiro` CLI. Both surfaces share a hook system.
- **ctx provider (read)**: `kiro_cli`.
- **Lineage**: **Claude-Code lineage in gate semantics** (and Amazon Q Developer
  CLI heritage — the CLI's tool names are `fs_read`/`fs_write`/`execute_bash`/
  `use_aws`). Events `PreToolUse`/`PostToolUse`/`UserPromptSubmit`/`Stop`, the
  `exit 2` block, stderr-as-reason, and the fail-open default all follow the
  Claude-Code model. See [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **IDE events** (8 triggers): `SessionStart`, `Stop`, `PreToolUse`,
  `PostToolUse`, `PreTaskExec`, `PostTaskExec`, `UserPromptSubmit`, and
  `PostFileCreate`/`PostFileSave`/`PostFileDelete`.
- **CLI events** (5 triggers): `AgentSpawn`, `UserPromptSubmit`, `PreToolUse`,
  `PostToolUse`, `Stop`.
- **Blocking-capable**: IDE — `PreToolUse`, `UserPromptSubmit`, `PreTaskExec`;
  CLI — `PreToolUse`. Mechanism: **exit code `2` blocks** and STDERR is returned
  to the agent as the reason. A `matcher` regex scopes a hook to specific tools.
- **Failure mode**: **the engine FAILS OPEN.** Any exit code other than `0` or
  `2` shows a warning and lets tool execution proceed; `PostToolUse`/`PostTask*`
  run after the fact and cannot block. Default hook timeout is 30s
  (`timeout`/`timeout_ms`). **A gate here must itself be fail-closed**: emit
  `exit 2` unless an explicit confirmed pass is reached; never rely on a crash or
  an odd exit code to deny.

## 3. Config
- **CLI**: hooks live under a `"hooks"` field inside a **JSON agent config file**
  in `.kiro/agents/` (project) or `~/.kiro/agents/` (global); local wins on name
  clash. Each entry takes a `command` and optional `matcher`.
- **IDE**: hooks are standalone **JSON** files in `.kiro/hooks/` at the workspace
  level, with fields `version`, `name`, `trigger`, `matcher`, `action`
  (`command` or agent prompt), `timeout`, `enabled`. Hooks can also be authored
  via natural language or a form in the IDE.
- **Format**: JSON in both surfaces.

## 4. Transcript pointer
- **Unknown.** Kiro is a closed AWS product; the sources reviewed do not document
  an on-disk session-transcript path or format. ctx is the read-side authority.
  For observation, wire non-blocking `PostToolUse`/`Stop`/`SessionStart` hooks
  rather than expecting a tailable transcript.

## 5. Capabilities and caveats
- Full observe + gate: block risky tools with `PreToolUse` (exit 2), witness with
  `PostToolUse`; spec-task granularity adds `PreTaskExec`/`PostTaskExec` beyond
  the usual Claude-Code set.
- Because it is Claude-Code-lineage and **fails open**, this behaves like the rest
  of that family: a thin descriptor pointing at `../claude/descriptor.md` plus the
  Kiro-specific config paths and the extra spec-task/file triggers captures it.
