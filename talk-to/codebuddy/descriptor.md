---
harness: CodeBuddy
ctx_provider: codebuddy
vendor: Tencent
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.codebuddy/settings.json
config_format: json
fidelity: documented
sources:
  - https://www.codebuddy.ai/docs/cli/hooks
  - https://www.codebuddy.ai/docs/cli/settings
  - https://www.codebuddy.ai/docs/cli/hooks-guide
---

# Talk-to: CodeBuddy

**Fidelity: documented** - CodeBuddy publishes an official CLI hooks reference and
settings page; its event list, `exit 2` / `"continue": false` blocking convention,
and layered `~/.codebuddy/settings.json` are documented. The precise fail-open vs
fail-closed timeout behavior is NOT stated by the docs and is inferred from the
Claude-Code lineage (see below).

## 1. Identity
- **Harness**: CodeBuddy (Tencent Cloud Code Assistant) - an AI code editor with a
  CLI ("CodeBuddy Code"), IDE, and plugin surface.
  [Docs](https://www.codebuddy.ai/docs/cli/hooks).
- **ctx provider (read)**: `codebuddy`.
- **Lineage**: a **Claude-Code-lineage clone**, and a notably faithful one - the
  hook config schema (`hooks` map, `matcher`, `hooks:[{type:"command",command}]`),
  the layered `settings.json` scopes, the `mcp__<server>__<tool>` naming, and the
  `exit 2` blocking convention all match Claude Code. Failure semantics follow the
  Claude lineage; see [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events**: a large (27+) engine spanning tool lifecycle (`PreToolUse`,
  `PostToolUse`, `PostToolUseFailure`), session/agent (`SessionStart`,
  `SessionEnd`, `Stop`, `SubagentStart`, `SubagentStop`, `StopFailure`), user
  interaction (`UserPromptSubmit`, `Notification`, `PermissionRequest`,
  `PermissionDenied`, `Elicitation`, `ElicitationResult`), context (`PreCompact`,
  `PostCompact`, `InstructionsLoaded`, `ConfigChange`), task/team (`TaskCreated`,
  `TaskCompleted`, `TeammateIdle`), file/env (`FileChanged`, `CwdChanged`,
  `WorktreeCreate`, `WorktreeRemove`), and `Setup`.
- **Blocking-capable events**: `PreToolUse` (block the tool call),
  `UserPromptSubmit` (block prompt submission), `Stop`/`SubagentStop` (prevent
  stopping), and `PreCompact` (block compaction) - via **exit code `2`** or a
  stdout JSON `{"continue": false, "reason": ...}`. All other events are
  observational; a non-0/non-2 exit is a non-blocking error (stderr shown,
  execution continues).
- **Failure mode**: **treat it as FAILS OPEN.** Hook processes time out after 60s
  (per-hook configurable). The docs do **not** explicitly state whether a
  timeout/unexpected error on a blocking hook resolves to allow or deny - but the
  whole engine is a Claude-Code clone, and the documented handling of non-0/non-2
  exits (continue anyway) points the same way. **A gate on CodeBuddy must be the
  fail-closed party itself**: default to `exit 2`, reach `exit 0` only on an
  explicit confirmed allow, and finish inside the hook timeout. Verify the live
  timeout-path behavior before trusting it.

## 3. Config
- **Path**: `~/.codebuddy/settings.json` (user), `.codebuddy/settings.json`
  (project, committed), `.codebuddy/settings.local.json` (project-local,
  git-ignored). Scopes merge (all matching hooks run); a `disableAllHooks: true`
  kill-switch exists.
- **Format**: JSON. Same `hooks` -> event -> `[{matcher, hooks:[{type:"command",
  command}]}]` shape as Claude Code. MCP tools are matchable by the
  `mcp__<server>__<tool>` regex pattern.
- **Knobs that matter**: `disableAllHooks` silently voids every gate - an
  adversary flipping it is a bypass; the audited gate should assert it stays
  false. Plugins can also bundle MCP servers via `.mcp.json` / `plugin.json`.

## 4. Transcript pointer
- **Path pattern**: not disclosed in the settings/hooks docs. Chat history
  retention is controlled by `cleanupPeriodDays` (default 30) and memory lives
  under `~/.codebuddy/memories/` (or `.codebuddy/memories/` for team mode), but
  raw session transcripts are a separate, **undocumented** location - likely under
  `~/.codebuddy/`. Treat as **unknown**; ctx is the read-side authority.

## 5. Capabilities and caveats
- Observe without risk by wiring the non-blocking events
  (`SessionStart`/`PostToolUse`/`PostToolUseFailure`/`SessionEnd`); gate by wiring
  `PreToolUse` (and `PreCompact` if compaction must be controlled) fail-closed.
- The unusually rich event set (`PermissionRequest`, `PermissionDenied`,
  `FileChanged`, `WorktreeCreate`, team events) gives more witness surface than
  Claude Code, but only the five listed blocking events actually deny.
- A Claude-Code gate ports almost directly; the main divergences are the config
  path, the `"continue": false` JSON form (vs Claude's `permissionDecision`), and
  the `disableAllHooks` switch.
