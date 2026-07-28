---
harness: Crush
ctx_provider: crush
vendor: Charm (charmbracelet)
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse]
fails_open: true
subagent_hooks_inherited: untested
config_path: crush.json (project) / ~/.local/share/crush data-dir
config_format: json
resource_type: [local, api]
fidelity: documented
sources:
  - https://github.com/charmbracelet/crush/blob/main/docs/hooks/README.md
  - https://github.com/charmbracelet/crush/blob/main/AGENTS.md
  - https://github.com/charmbracelet/crush/issues/2707
  - https://deepwiki.com/charmbracelet/crush/2-getting-started
---

# Talk-to: Crush

**Fidelity: documented** - drawn from Charm's official `docs/hooks/README.md`,
the repo `AGENTS.md`, and the lifecycle-hooks issue thread; not yet exercised
against a live Crush install by this registry.

## 1. Identity
- **Harness**: Crush ([Charm / charmbracelet](https://github.com/charmbracelet/crush)),
  a terminal-native agentic coding TUI written in Go.
- **ctx provider (read)**: `crush`.
- **Lineage**: **Claude-Code lineage in its gate semantics.** The single
  `PreToolUse` event, the `exit 2` block convention, and the stdout
  `decision: allow|deny|none` JSON are the Claude-Code model; failure model
  matches too. See [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events**: only **`PreToolUse`** is supported today (fires before every tool
  call — used to block dangerous commands, enforce policy, rewrite tool input,
  or inject context). Richer lifecycle/observer events are an open request
  ([issue #2707](https://github.com/charmbracelet/crush/issues/2707)).
- **Blocking mechanism**: exit `0` with stdout JSON whose `decision` is `allow`
  (pre-approve, skip permission prompt), `deny` (block; model sees the error),
  or `none`/omitted (normal permission flow). Exit `2` blocks the call with
  stderr as the deny reason. Exit `49` halts the whole turn. The hook receives
  JSON on stdin plus hook-specific env vars.
- **Failure mode**: **the engine FAILS OPEN.** On timeout or any unrecognized
  exit code Crush cancels the hook context, treats it as a non-blocking error,
  and the tool call proceeds. **A gate wired here must be the fail-closed party
  itself**: default to `exit 2`, reach a clean allow only on an explicit
  confirmed pass, and never lean on the engine to deny for you.

## 3. Config
- **Path**: `crush.json` in the working directory (project scope), plus a
  data-dir config; the data dir defaults to `.crush/` in-project or
  `~/.local/share/crush/`. Run `crush dirs` to print local paths.
- **Format**: JSON (schema `https://charm.land/crush.json`). Hooks live under a
  `hooks` map keyed by event, each entry taking `command` (required), optional
  `matcher` (regex over tool name), `name`, and `timeout` (seconds, default 30).
- **Knobs that matter**: use absolute paths (or inline commands) in a global
  config since relative paths only resolve at project scope.

## 4. Transcript pointer
- **Storage**: SQLite, not JSONL. Sessions and messages persist to `crush.db`
  inside the data dir (`.crush/crush.db` project-local, or the
  `~/.local/share/crush/` data dir; `--data-dir` overrides).
- **Read side**: the read/witness side must query the SQLite tables rather than
  tail a flat transcript file. ctx is the read-side authority for schema.

## 5. Capabilities and caveats
- Gate-capable but observe-thin: with a single `PreToolUse` event there is no
  official `PostToolUse`/`Stop`/`SessionEnd` observer hook yet, so passive
  witnessing has to come off the SQLite store, not an event stream.
- The Go engine (`internal/hooks/`) is deliberately decoupled from the agent and
  runs commands, aggregates decisions, and returns a verdict — a clean surface,
  but one whose fail-open default puts the safety burden on the hook script.
