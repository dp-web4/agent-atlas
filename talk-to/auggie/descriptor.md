---
harness: Auggie (Augment Code)
ctx_provider: auggie
vendor: Augment Code
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, Stop]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.augment/settings.json
config_format: json
fidelity: documented
sources:
  - https://docs.augmentcode.com/cli/hooks
  - https://docs.augmentcode.com/cli/reference
  - https://www.augmentcode.com/changelog/auggie-cli-0-16-0-release-notes
---

# Talk-to: Auggie (Augment Code)

**Fidelity: documented** - built from Augment's official CLI hooks docs, which
state the event model, blocking JSON, and failure behavior explicitly.

## 1. Identity
- **Harness**: Auggie, Augment Code's terminal coding agent (invoked as `auggie`,
  not `augment`).
- **ctx provider (read)**: `auggie`.
- **Lineage**: **a Claude-Code-lineage clone.** Same event names, same
  `hooks > PreToolUse > matcher > hooks > {type: command, command}` structure, same
  `exit 2` / `permissionDecision: "deny"` blocking convention — see
  [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events**: `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `Stop`.
- **Blocking-capable events**: only `PreToolUse` can block tool execution; `Stop`
  can block the agent from finishing (via `decision: "block"`); `PostToolUse`
  cannot block anything (vendor states this explicitly). `PreToolUse` denies via
  `exit 2` + stderr, or via a `{"hookSpecificOutput": {"permissionDecision":
  "deny", ...}}` JSON on stdout. (Input mutation via `updatedInput` is documented
  as not yet implemented — deny is the only supported intervention.)
- **Failure mode**: **the engine FAILS OPEN, documented.** The docs' exit-code
  table shows any exit code other than `0`/`2` ("Other") results in *"error logged,
  execution continues"* — i.e. timeouts and unexpected errors let the tool proceed.
  Default hook timeout is 60s. **Consequence: the gate must be the fail-closed
  party** — default to `exit 2`, reach a pass only on an explicit confirmed allow,
  and never rely on the engine to deny on error.

## 3. Config
- **Path (precedence, high→low)**: `/etc/augment/settings.json` (or
  `C:\ProgramData\Augment\settings.json` on Windows), `<workspace>/.augment/settings.local.json`,
  `<workspace>/.augment/settings.json`, `~/.augment/settings.json`.
- **Format**: JSON. Hooks, permissions, and MCP servers live in the same
  `settings.json`; a `rules/` directory and `hooks/` directory sit alongside it in
  `~/.augment/`.
- **Knobs that matter**: hooks are global (not per-agent); execution order follows
  definition order; per-command timeout is configurable.

## 4. Transcript pointer
- **Path pattern**: not documented in the hooks reference. The `SessionStart`/`Stop`
  events expose per-session context (the `Stop` payload includes an
  `agent_stop_cause` field such as `end_turn`/`interrupted`); ctx is the read-side
  authority for any on-disk session log.

## 5. Capabilities and caveats
- Observe via `SessionStart`/`PostToolUse`/`SessionEnd`; gate via `PreToolUse`.
- Auggie can itself be run as an MCP server (`--mcp` / `--mcp-auto-workspace`) to
  expose its codebase-retrieval tool to other agents — a tool-provider surface,
  distinct from the gate surface above.
- **Fail-open reminder**: like the rest of the Claude lineage, a broken gate hook
  waves the action through. Build the gate deny-by-default.
