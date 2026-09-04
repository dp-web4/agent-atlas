---
harness: Claude Code
ctx_provider: claude
vendor: Anthropic
lineage: canonical
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, UserPromptSubmit, Stop]
fails_open: true
subagent_hooks_inherited: verified-inherited
subagent_attribution: parent
subagent_probe_date: 2026-07-26
config_path: ~/.claude/settings.json
config_format: json
resource_type: [subscription, api]
fidelity: verified
sources:
  - https://docs.anthropic.com/en/docs/claude-code/hooks
  - https://github.com/dp-web4/hestia/tree/main/plugins/claude-code
---

# Talk-to: Claude Code

**Fidelity: verified** - Claude Code is the live reference gate the
[hestia claude-code plugin](https://github.com/dp-web4/hestia/tree/main/plugins/claude-code)
runs on; its hook path is exercised in production use. The fuller event list below
is documented from Claude Code's hook system; the blocking path and failure mode
are the verified, load-bearing parts.

## 1. Identity
- **Harness**: Claude Code (Anthropic).
- **ctx provider (read)**: `claude`.
- **Lineage**: this *is* the canonical hook engine that several other harnesses
  (Kimi, and other Claude-Code-lineage CLIs) clone. Descriptors for those can
  inherit this failure model.

## 2. Hook engine
- **Events**: `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Stop`,
  `SubagentStop`, `SessionStart`, `SessionEnd`, `PreCompact`, `Notification`.
- **Blocking-capable events**: `PreToolUse` (deny a tool call), `UserPromptSubmit`,
  and `Stop`, via exit code `2` or a `permissionDecision`/`decision` JSON on stdout.
  `PostToolUse` and the rest are observational.
- **Failure mode**: **fails open**, like the whole lineage. A blocking hook that
  errors, times out, or exits unexpectedly resolves to *allow*. **The gate must be
  fail-closed by construction**: deny by default, allow only on an explicit
  confirmed pass.

  **Overrun behaviour, MEASURED 2026-09-04 on 2.1.260** (four controlled arms, isolated
  `--settings`, file-existence as ground truth): `exit 0` → allowed; `exit 2` + stderr →
  **blocked**; `sleep 1; exit 2` under a 5 s timeout → **blocked** (slow but in time still
  binds); `sleep 30` under a 2 s timeout → **allowed**, killed at the deadline. The engine
  does not wait past the timeout and does not treat the kill as a denial.

- **Hook timeout**: per-hook `"timeout"` in seconds in the `hooks` entry. **The hestia
  `PreToolUse` entry on CBP carries `"timeout": 5`** (measured from the live
  `~/.claude/settings.json`, 2026-09-04 — not remembered; §17 of hestia's bypass catalogue
  says in as many words not to source this figure from memory).

  **The Class T pair, audited 2026-09-04: FAILS on this seat.** The invariant in hestia's
  catalogue and in `kimi_code_cli/descriptor.md` — `gate internal budget < hook timeout` —
  is wrong by 3×. The budget is minted once per *entry point* into the shared gate
  mechanism and one hook invocation crosses several. A starved daemon produces a 12.4 s
  hook that the engine kills at 5 s and allows. Demonstrated end to end.

  **Refined 2026-09-04 (same day), by sweeping past the per-request cap:** the composition
  is not linear in the budget. It is

  ```
  wall = 3 · min(budget, REQUEST_TIMEOUT_S) + c_seat        (REQUEST_TIMEOUT_S = 5 s)
  ```

  because a window ends when its *first* request gives up. Measured on this seat at
  2/4/6/10/20 s: 6.40 / 12.43 / 15.38 / 15.39 / 15.41 — so there is a **ceiling of 15.38 s
  that no budget can exceed**, and this seat fits its 5 s deadline only below a **1539 ms**
  budget. In force: 4000 ms. The three windows are the policy-snapshot fetch, its *retry*,
  and the society-safety query — two mint sites, three mint events.

  Fleet at the same date: codex 13.91 s vs 15 s (pass, 1.09 s margin), kimi 16.91 s vs 15 s
  (**FAIL**), gemini 6.08 s vs 15 s (pass). See hestia PR #939,
  `tools/class_t_seat_audit.py`, and
  `findings/wake-0904c-no-budget-is-safe-the-ceiling-belongs-to-the-request-cap-2026-09-04.md`.

### Sub-agent inheritance — **verified inherited** (2026-07-26)

Sub-agent tool calls fire the same hooks as the main loop, and they are witnessed.
Measured by giving a `general-purpose` sub-agent three Bash calls: two benign ones ran,
and a third — an `echo` whose *text* trips a lexical policy rule — was denied **inside the
sub-agent** with the harness's normal `PreToolUse` deny. The chain moved in step: +14
entries, +5 actions, **+1 denial**, carrying both a `policy_decision status=deny` and its
`outcome`. So on Claude Code, *"spawn a sub-agent to do it"* is **not** a gate bypass.

This is the load-bearing check for any harness that spawns sub-sessions, and it is the one
most likely to be assumed rather than measured. The rest of the registry is honestly
`untested` on it.

**Caveat — attribution, not enforcement.** Sub-agent actions are recorded under the
**parent's** `plugin_id`. Enforcement and witnessing are intact, but the record cannot tell
main-loop action from sub-agent action, so a fleet of sub-agents appears as one actor.

## 3. Config
- **Path**: `~/.claude/settings.json` (and project/local `settings.json`).
- **Format**: JSON. A `hooks` map keys each event to matchers and the command(s)
  to run; a `PreToolUse` matcher can scope by tool.
- **Knobs that matter**: hook precedence across user/project/local settings; keep
  the gate command in a stable, audited path.

## 4. Transcript pointer
- **Path pattern**: `~/.claude/projects/<encoded-cwd>/*.jsonl`, one JSONL file per
  session. This is the read side's input.
- **Notable fields**: per-turn tool calls and results; the witness side of the
  hestia plugin keys off `tool_name` and the tool payload.

## 5. Capabilities and caveats
- Full observe + gate: witness every tool call (`PostToolUse`) and gate the risky
  ones (`PreToolUse`). The hestia plugin does exactly this: hash-linked witness
  entries plus a fail-closed pre-tool gate.
- Because this is the lineage source, a new Claude-Code-clone harness usually needs
  only a thin descriptor that points here and notes its config path and any
  divergence.
