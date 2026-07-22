---
harness: Qoder
ctx_provider: qoder
vendor: Alibaba
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, UserPromptSubmit, Stop]
fails_open: true
config_path: ~/.qoder/settings.json
config_format: json
fidelity: documented
sources:
  - https://docs.qoder.com/extensions/hooks
  - https://help.aliyun.com/en/lingma/qoder-cn/user-guide/hooks
  - https://docs.qoder.com/
---

# Talk-to: Qoder

**Fidelity: documented** - Qoder ships an official hooks reference whose event
list, exit-code-2 blocking convention, `settings.json` layout, and timeout
behavior are spelled out in vendor docs (both the global docs.qoder.com page and
the Alibaba/Lingma CN mirror).

## 1. Identity
- **Harness**: Qoder ([Alibaba](https://docs.qoder.com/)) - an agentic coding
  platform shipping a desktop IDE, a CLI, and JetBrains plugin, backed by Alibaba
  Cloud Model Studio. The China edition is branded Qoder CN / Lingma (Tongyi
  Lingma) and uses `~/.lingma/` in place of `~/.qoder/`.
- **ctx provider (read)**: `qoder`.
- **Lineage**: a **Claude-Code-lineage clone**. Same event names, same `exit 2`
  blocking convention, same `permissionDecision: "deny"` JSON, same layered
  `settings.json` with `hooks`/`matcher`/`command` shape. Its failure semantics
  follow the Claude lineage; see [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events**: `UserPromptSubmit`, `PreToolUse`, `PostToolUse`,
  `PostToolUseFailure`, `Stop` (a lean five-event subset of the Claude engine).
- **Blocking-capable events**: `PreToolUse` (reject the tool call),
  `UserPromptSubmit` (cancel the prompt), and `Stop` (prevent completion), via
  **exit code `2`** with a stderr message, or - for `PreToolUse` on `exit 0` - a
  stdout JSON `{"hookSpecificOutput":{"permissionDecision":"deny"}}`. The rest
  are observational.
- **Failure mode**: **the engine FAILS OPEN.** The docs are explicit: a hook
  timeout (default 30s) kills the script and is **treated as `exit 0` (allow)**,
  and any non-0/non-2 exit is a non-blocking error that shows stderr and lets
  execution continue. **Consequence: a gate on Qoder must be the fail-closed
  party itself** - default to `exit 2` and only reach `exit 0` on an explicit,
  confirmed allow; never rely on the engine to deny on your behalf, and keep the
  gate command fast enough to finish inside its own timeout.

## 3. Config
- **Path**: `~/.qoder/settings.json` (user), `.qoder/settings.json` (project),
  `.qoder/settings.local.json` (project-local, git-ignored). Qoder CN / Lingma
  uses the parallel `~/.lingma/settings.json` tree.
- **Format**: JSON. A `hooks` map keys each event to a list of `{matcher, hooks:
  [{type: "command", command, timeout?}]}` blocks; scopes merge by priority
  (user < project < project-local).
- **Knobs that matter**: `matcher` scopes a `PreToolUse` hook by tool; per-hook
  `timeout` (default 30s) - size the gate to finish well under it, since a
  timeout resolves to allow.

## 4. Transcript pointer
- **Path pattern**: not documented in the public hooks/CLI reference. Likely
  under the `~/.qoder/` (or `~/.lingma/`) tree, but unconfirmed. The read side
  (ctx) is the authority here; treat transcript location as **unknown** until a
  live session is inspected.

## 5. Capabilities and caveats
- Observe without risk by wiring the non-blocking events
  (`PostToolUse`/`PostToolUseFailure`/`Stop` for logging); gate by wiring
  `PreToolUse` fail-closed.
- Because this is a Claude-Code clone, a gate written for Claude Code ports
  almost directly - only the config path (`~/.qoder/` vs `~/.claude/`, or
  `~/.lingma/` on the CN build) and the smaller event set differ.
- The CN (`~/.lingma/`) doc lists only `PreToolUse`/`UserPromptSubmit` as
  blocking and omits `Stop`-blocking - verify which blocking events the specific
  build honors before relying on `Stop`.
