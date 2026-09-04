---
harness: Gemini CLI
ctx_provider: gemini
vendor: Google
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [BeforeTool, BeforeAgent, BeforeModel, BeforeToolSelection]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.gemini/settings.json
config_format: json
resource_type: [subscription, api]
fidelity: documented
sources:
  - https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md
  - https://developers.googleblog.com/tailor-gemini-cli-to-your-workflow-with-hooks/
  - https://geminicli.com/docs/hooks/reference/
---

# Talk-to: Gemini CLI

**Fidelity: documented** - built from Google's official `gemini-cli` hooks
reference; the exit-code semantics and the fail-open-on-unexpected-failure
behavior are stated in the docs.

## 1. Identity
- **Harness**: Gemini CLI (Google), the open-source `google-gemini/gemini-cli`
  agent.
- **ctx provider (read)**: `gemini`.
- **Lineage**: independent. Gemini uses its own `Before*/After*` event vocabulary
  (`BeforeTool`, `BeforeModel`, `BeforeAgent`) rather than Claude's
  `PreToolUse`/`PostToolUse`, but it shares the `exit 2` = block and stdout-JSON
  `decision` conventions - concept-parallel to the Claude lineage, not a clone.

## 2. Hook engine
- **Events**: `SessionStart`, `SessionEnd`, `Notification`, `PreCompress`,
  `BeforeAgent`, `AfterAgent`, `BeforeModel`, `BeforeToolSelection`,
  `AfterModel`, `BeforeTool`, `AfterTool`.
- **Blocking-capable events**: `BeforeTool` (deny a tool call), `BeforeAgent`
  (block a prompt), `BeforeModel` (block the LLM request), and `BeforeToolSelection`
  - each blocks via exit code `2` (stderr becomes the rejection reason) or stdout
  JSON `"decision": "deny"` (aliased `"block"`). `AfterAgent` can force a retry;
  `After*` events are otherwise observational.
- **Failure mode**: **fails open on unexpected failure.** Exit code `2` is the
  *intentional* block; exit `0` is success; any *other* non-zero exit is treated
  as a non-fatal warning and the interaction proceeds using the original
  parameters. Timeouts (default `60000` ms) likewise proceed. So a hook that
  crashes or hangs does **not** deny. **The gate must be fail-closed by
  construction** - deny by default, `exit 2` unless an explicit confirmed pass
  produces `exit 0`; never rely on the engine to deny on your behalf.

## 3. Config
- **Path**: `~/.gemini/settings.json` (user), `<project>/.gemini/settings.json`
  (project), `/etc/gemini-cli/settings.json` (system), plus hooks contributed by
  installed extensions (`hooks/hooks.json`, registered at Extensions priority).
- **Format**: JSON - a `hooks` object keys each event to an array of definitions
  with `matcher` (regex for tool events, exact string for lifecycle events),
  optional `sequential`, and `hooks` entries of `type: "command"` + `command`.
- **Knobs that matter**: `matcher` scoping; per-hook timeout (default 60 s); a
  hook must print only the final JSON object to stdout - stray stdout text breaks
  the protocol.
- **The timeout is in MILLISECONDS here**, where Claude Code, Codex and Kimi all spell
  theirs in seconds. The deployed `BeforeTool` entry reads `"timeout": 15000` — 15 s, not
  15000 s. A hook-deadline number quoted across seats is a number read wrong by 1000×.
- **The Class T pair, measured 2026-09-04 on CBP: this seat PASSES with the most margin in
  the fleet (6.08 s against 15 s, 59%) — and it does so by implementing the fix the others
  need.** Its gate does not enter the shared mechanism in-process; it spawns the governor
  as a subprocess under **its own** deadline (`subprocess.run(…, timeout=6)`) and fails
  closed in the `except`. That is one deadline minted per invocation and threaded over
  everything downstream, which is exactly what claude (12.38 s vs 5 s, FAIL) and kimi
  (16.91 s vs 15 s, FAIL) lack. The cost is that this seat never obtains a real verdict
  under daemon starvation and takes the ratified degraded path instead — correct, and what
  the failing seats cannot do because nothing holds a clock over them. hestia PR #939,
  `tools/class_t_seat_audit.py`.

## 4. Transcript pointer
- **Path pattern**: Gemini CLI keeps session/checkpoint state under `~/.gemini/`
  (e.g. logs and checkpoints), but a stable per-session transcript path/format is
  not pinned down here. The `gemini` ctx provider is the read-side authority.

## 5. Capabilities and caveats
- Distinctive `BeforeModel` / `BeforeToolSelection` events allow gating at the
  model-request and tool-choice layers, earlier than most harnesses expose.
- Extensions can ship their own hooks, so an audited gate should account for
  hooks it did not install (they run alongside user/project hooks).
