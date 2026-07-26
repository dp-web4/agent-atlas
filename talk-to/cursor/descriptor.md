---
harness: Cursor
ctx_provider: cursor
vendor: Anysphere
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [beforeShellExecution, beforeMCPExecution, beforeReadFile, beforeSubmitPrompt, preToolUse]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.cursor/hooks.json
config_format: json
fidelity: documented
sources:
  - https://cursor.com/docs/hooks
  - https://blog.gitbutler.com/cursor-hooks-deep-dive
  - https://www.infoq.com/news/2025/10/cursor-hooks/
---

# Talk-to: Cursor

**Fidelity: documented** - built from Cursor's official hooks docs (hooks landed
in Cursor 1.7); the fail-open default and the per-hook `failClosed` opt-in are
stated by the vendor.

## 1. Identity
- **Harness**: Cursor (Anysphere) - the AI IDE. Hooks apply to the agent loop
  (Agent Chat / Cmd-K), not the closed cloud UI.
- **ctx provider (read)**: `cursor`.
- **Lineage**: independent. Cursor ships its own event vocabulary
  (`beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`,
  `afterFileEdit`, ...) alongside Claude-style `preToolUse`/`postToolUse` names.
  It is not a Claude-Code hook-engine clone; its config shape and failure model
  are its own.

## 2. Hook engine
- **Events**: agent hooks - `sessionStart`, `sessionEnd`, `preToolUse`,
  `postToolUse`, `postToolUseFailure`, `subagentStart`, `subagentStop`,
  `beforeShellExecution`, `afterShellExecution`, `beforeMCPExecution`,
  `afterMCPExecution`, `beforeReadFile`, `afterFileEdit`, `beforeSubmitPrompt`,
  `preCompact`, `stop`, `afterAgentResponse`, `afterAgentThought`; Tab hooks
  (`beforeTabFileRead`, `afterTabFileEdit`); app lifecycle (`workspaceOpen`).
- **Blocking-capable events**: the `before*` gates - `beforeShellExecution`,
  `beforeMCPExecution`, `beforeReadFile`, `beforeSubmitPrompt` (and `preToolUse`)
  - block by emitting a `"permission"` field on stdout JSON with value `"deny"`
  (or `"ask"` where supported), or by exiting with code `2` (equivalent to
  `"deny"`). `after*` / `post*` events are observational.
- **Failure mode**: **fails open by default.** A hook that crashes, times out,
  returns invalid JSON, or exits non-zero (other than `2`) resolves to *allow*
  and the action proceeds. **The gate must be fail-closed by construction.**
  Cursor uniquely offers a per-hook `"failClosed": true` flag that flips a hook
  to deny-on-failure; the vendor recommends it for `beforeMCPExecution` and
  `beforeReadFile`. Set it - but still write the gate to deny by default rather
  than trusting the flag alone.

## 3. Config
- **Path**: `~/.cursor/hooks.json` (user), `<project>/.cursor/hooks.json`
  (project), plus enterprise locations (`/etc/cursor/hooks.json` on Linux/WSL,
  `/Library/Application Support/Cursor/hooks.json` on macOS,
  `C:\ProgramData\Cursor\hooks.json` on Windows). Precedence: Enterprise > Team >
  Project > User; hooks from all present locations run.
- **Format**: JSON - `{ "version": 1, "hooks": { "<hookName>": [ { "command":
  "./script.sh", "timeout": 30, "failClosed": true } ] } }`. Each hook is a
  standalone process fed structured JSON on stdin.
- **Knobs that matter**: `failClosed` per hook; `timeout` (note timeouts still
  fail open unless `failClosed` is set).

## 4. Transcript pointer
- **Path pattern**: not documented as a stable local JSONL transcript. Cursor is
  IDE-hosted and does not publish a per-session transcript file the way the CLI
  harnesses do; the `cursor` ctx provider is the read-side authority for whatever
  session record is available.

## 5. Capabilities and caveats
- Rich, granular gate surface - separate hooks for shell, MCP, file read, and
  file edit means policy can be scoped tightly (e.g. block destructive git in
  `beforeShellExecution`, block reads of secret paths in `beforeReadFile`).
- The `failClosed` flag is the standout: Cursor is the one harness in this batch
  with a built-in deny-on-failure switch, but it is opt-in and default-off.
- Because hooks are IDE-loop bound, they cover the agent, not human-typed
  terminal commands outside the agent.
