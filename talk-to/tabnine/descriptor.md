---
harness: Tabnine CLI
ctx_provider: tabnine
vendor: Tabnine (Codota)
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [BeforeAgent, AfterAgent, BeforeModel, AfterModel, BeforeTool]
fails_open: true
config_path: .tabnine/agent/settings.json
config_format: json
fidelity: documented
sources:
  - https://docs.tabnine.com/main/getting-started/tabnine-cli/features/hooks
  - https://docs.tabnine.com/main/getting-started/tabnine-cli/features/settings/settings-reference
  - https://docs.tabnine.com/main/administering-tabnine/release-notes
---

# Talk-to: Tabnine CLI

**Fidelity: documented** - built from Tabnine's official CLI docs (hooks and
settings reference pages); not run locally, so failure semantics are inferred
from the documented exit-code contract rather than exercised.

## 1. Identity
- **Harness**: Tabnine CLI, the agentic command-line tool from
  [Tabnine](https://docs.tabnine.com/) (Codota). Tabnine's older surface is an
  IDE completion plugin with no hook API; this descriptor covers the newer
  **CLI agent**, which is the part with a real integration surface.
- **ctx provider (read)**: `tabnine`.
- **Lineage**: a Claude-Code-lineage hook engine with **renamed events**. The
  mechanism is the same family — command hooks that exchange JSON over
  stdin/stdout, `exit 2` to block, a `{"decision":"deny"}` JSON contract, and a
  `hooks` map in a JSON settings file — but the event names diverge from
  Claude's. Failure model follows the lineage; see
  [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events (11)**: `SessionStart`, `SessionEnd`, `BeforeAgent`, `AfterAgent`,
  `BeforeModel`, `AfterModel`, `BeforeToolSelection`, `BeforeTool`, `AfterTool`,
  `Notification`, `PreCompress`. Hooks run **synchronously** inside the agent
  loop — the CLI waits for all matching hooks before continuing.
- **Blocking-capable events**: `BeforeTool` (prevent a tool call), `BeforeAgent`
  (block a prompt), `AfterAgent` (force retry), `BeforeModel` (mock/modify the
  request), and `AfterModel` (filter the response). Blocking is via **exit code
  `2`** (action blocked, reason on stderr) or **`exit 0` with
  `{"decision":"deny","reason":"..."}`** on stdout. Any other non-zero exit is
  treated as a **non-fatal warning and execution proceeds**. `AfterTool`,
  `SessionStart/End`, `Notification`, `PreCompress`, `BeforeToolSelection` are
  observational.
- **Failure mode**: **fails open.** The docs state invalid JSON on stdout
  defaults to *allow* (treated as a `systemMessage`), and any exit code other
  than `2` proceeds; a hook that exceeds its `timeout` is killed by the
  framework. So an errored/timed-out/misbehaving blocking hook resolves to
  *allow*. **A gate on Tabnine must be the fail-closed party itself**: default to
  `exit 2` and only reach a confirmed `exit 0` allow. The hook must also print
  **nothing to stdout but the final JSON object** — a stray `echo` breaks parsing
  and, per the fail-open default, lets the action through.

## 3. Config
- **Path**: `.tabnine/agent/settings.json`, resolved across four layers
  (highest first): system settings, then workspace `<project>/.tabnine/agent/`,
  then user `~/.tabnine/agent/`, then system defaults. On Linux the system files
  live at `/etc/tabnine-cli/settings.json` and `.../system-defaults.json`
  (override via `TABNINE_CLI_SYSTEM_SETTINGS_PATH` /
  `TABNINE_CLI_SYSTEM_DEFAULTS_PATH`).
- **Format**: JSON, deep-merged across layers. A `hooks` object maps each event
  name to arrays of `{type:"command", command, name}` definitions; hooks accept a
  per-hook `env` map and a `timeout`.
- **Knobs that matter**: put the gate in a **system-settings** layer so a
  per-project `settings.json` cannot unset it (workspace merges under system);
  set an explicit `timeout` and remember the timeout path fails open.

## 4. Transcript pointer
- **Path pattern**: not pinned down in the docs. Sessions are stored as
  **JSONL** files (the v0.26.0 release notes describe improved validation and
  error messaging for invalid JSONL session files), but the exact directory is
  undocumented in the pages reviewed. ctx is the read-side authority here.
- **Notable fields**: hooks receive event metadata as JSON on stdin, so the
  live signal (tool name, arguments) is available at gate time even without
  reading the transcript file.

## 5. Capabilities and caveats
- Full observe + gate: wire `SessionStart`/`AfterTool`/`SessionEnd` to witness,
  and `BeforeTool`/`BeforeAgent` to gate. `BeforeModel`/`AfterModel` additionally
  allow request/response interception, which the Claude lineage does not expose.
- **Renamed-events gotcha**: do not assume Claude's `PreToolUse` name — Tabnine
  uses `BeforeTool` (singular), and there is no `Stop` event; the loop-end
  analogue is `AfterAgent` (which can force a retry, not block a stop).
- Distinguish the two Tabnine products: the IDE completion extension has **no**
  hook surface; only the CLI agent does.
