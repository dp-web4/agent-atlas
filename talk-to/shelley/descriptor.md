---
harness: Shelley
ctx_provider: shelley
vendor: Bold Software (exe.dev)
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [system-prompt, new-conversation, chat-message]
fails_open: false
subagent_hooks_inherited: untested
config_path: $HOME/.config/shelley/hooks/<name>
config_format: executable scripts (stdin JSON/text -> stdout)
fidelity: documented
sources:
  - https://github.com/boldsoftware/shelley
  - https://raw.githubusercontent.com/boldsoftware/shelley/main/HOOKS.md
---

# Talk-to: Shelley

**Fidelity: documented** - Shelley's own `HOOKS.md` in the boldsoftware/shelley
repo specifies the four hook points, the abort-on-failure rule, and the hook
directory; only the transcript path is inferred.

## 1. Identity
- **Harness**: Shelley, a mobile-friendly, web-based, multi-model single-user
  coding agent from Bold Software, built for (not limited to) exe.dev. It ships
  as prebuilt macOS/Linux binaries and explicitly ships **without** built-in
  authorization or sandboxing ("bring your own").
- **ctx provider (read)**: `shelley`.
- **Lineage**: **independent.** Its hook design does not follow the Claude-Code
  event model — no `PreToolUse`/`PostToolUse`, no per-tool-call gate, and it fails
  *closed*, the opposite of the Claude lineage.

## 2. Hook engine
- **Events (4)**: `system-prompt` (rewrite the system prompt), `new-conversation`
  (customize conversation init), `chat-message` (rewrite the user message), and
  `end-of-turn` (log completion; non-blocking).
- **Blocking-capable events**: the first three. A hook aborts the operation it
  belongs to on **non-zero exit, invalid output, or other error**. `end-of-turn`
  is the sole exception — its failures are only logged.
- **Failure mode**: **FAILS CLOSED** for the three blocking hooks — a hook that
  errors aborts the turn. This is the rare inversion of the Claude-lineage
  default, so a gate can lean on the engine to deny on failure. Note the coverage
  gap instead: these hooks gate *turn/prompt* boundaries, not individual tool
  calls, so they cannot veto a specific shell command mid-turn the way a
  `PreToolUse` gate can.

## 3. Config
- **Path**: hooks are executable scripts dropped in
  `$HOME/.config/shelley/hooks/<name>`, where `<name>` is the hook event. There is
  no separate declarative config file — presence of the executable *is* the
  registration.
- **Format**: scripts receive event data on **stdin** (JSON or text) and return
  their response on **stdout**; exit status decides abort vs. proceed.

## 4. Transcript pointer
- Shelley persists conversations, tool calls, and results in a **SQLite** database
  and streams UI updates over an **SSE** endpoint. The exact DB file path is not
  documented in `HOOKS.md`; treat as **unknown / inferred** and confirm on disk.
  ctx is the read-side authority once the DB is located.

## 5. Capabilities and caveats
- Observe cheaply via `end-of-turn`; shape or abort turns via `chat-message` /
  `system-prompt` / `new-conversation`.
- **No tool-call-level gate**: unlike Claude-lineage harnesses, Shelley exposes no
  pre-tool interception, so command-granular policy must live elsewhere (Shelley
  itself provides no sandbox/authorization — the vendor says bring your own).
- Fail-closed hooks are a security asset here — a crashing gate denies rather than
  leaks — but only at the turn boundary they cover.
