---
harness: Kimi Code CLI
ctx_provider: kimi_code_cli
vendor: Moonshot AI
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, UserPromptSubmit, Stop]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.kimi-code/config.toml
config_format: toml
resource_type: [subscription, api]
fidelity: verified
sources:
  - https://github.com/dp-web4/hestia/tree/main/plugins/kimi
---

# Talk-to: Kimi Code CLI

**Fidelity: verified** - reverse-engineered and wired against the real Kimi Code
CLI in [hestia/plugins/kimi](https://github.com/dp-web4/hestia/tree/main/plugins/kimi),
run in warn and enforce modes.

## 1. Identity
- **Harness**: Kimi Code CLI ([Moonshot AI](https://www.moonshot.ai/)).
- **ctx provider (read)**: `kimi_code_cli` (ctx source-format id `kimi_code_cli_wire_jsonl_tree`).
- **Lineage**: a near-clone of Claude Code's hook engine. Its failure semantics and
  event model follow the Claude-Code lineage; see [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events**: a 16-event engine, including `PreToolUse`, `PostToolUse`,
  `PostToolUseFailure`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `Stop`,
  and others.
- **Blocking-capable events**: only `PreToolUse`, `UserPromptSubmit`, and `Stop`
  can block, via exit code `2` or a `permissionDecision: "deny"` JSON on stdout.
  Every other event is fire-and-forget.
- **Failure mode**: **the engine FAILS OPEN.** A blocking hook that times out,
  fails to spawn, exits non-zero unexpectedly, or throws all resolve to *allow*.
  **Consequence: a gate on Kimi has to be the fail-closed party itself.** Default
  to `exit 2` and only reach `exit 0` on an explicit, confirmed allow; never rely
  on `set -e` or the engine default to deny for you.
- **Timeout before that fail-open fires (verified against the engine binary,
  2026-08-07)**: per-hook, from the `[[hooks]]` entry's own `timeout` (seconds),
  falling back to a built-in default of **30 s** when unset:

  ```js
  timeout: hook.timeout ?? DEFAULT_HOOK_TIMEOUT_SECONDS   // DEFAULT_HOOK_TIMEOUT_SECONDS = 30
  ```

  So the configured `timeout` **is** honoured, and an unset one is generous, not
  tight. Recorded because the fleet had been operating on a remembered figure of
  **3 s** — off by 5–10×, never sourced, and load-bearing: hestia sized its Kimi
  gate's internal budget at 800 ms to stay under it, which put the gate's
  per-request cap below the daemon's p99 and produced intermittent fail-closed
  denies. Measure the engine, don't inherit the number.
- **The gate's budget and this timeout are a COUPLED PAIR, and the coupling is a
  bypass surface.** A fail-closed gate on Kimi must finish inside the hook
  `timeout`; past it the engine allows. So:

  ```
  gate internal budget  <  hook timeout  (else the engine fails OPEN)
  ```

  Raising the gate's budget above the hook timeout does not slow the member down —
  it **silently un-governs it**. Every gate call overruns, the engine allows, and
  nothing is logged: no deny to notice, and the witness chain shows nothing missing
  because nothing was refused. It looks exactly like a well-behaved member. This is
  worth auditing periodically rather than trusting once, since either number can be
  edited independently and neither edit looks dangerous on its own.

## 3. Config
- **Path**: `~/.kimi-code/config.toml`.
- **Format**: TOML. `[[hooks]]` blocks map an event to a command.
- **Knobs that matter**: set `[upgrade] auto_install = false` in `tui.toml` to resist
  silent binary drift — but note it is not airtight: a 0.26→0.28.1 update was observed
  to land with this already set to `false`, so some update path (manual `upgrade`, or
  the web/server daemon) bypasses it. Re-verify the gate after any version change;
  don't assume the pin held.

## 4. Transcript pointer
- **Path pattern**: `~/.kimi-code/sessions/<slug>/<id>/agents/main/wire.jsonl`,
  append-only.
- **Notable fields**: rich detail including `turn.prompt`. Because the prompt is in
  the transcript, prompt capture reads the file rather than wiring a
  `UserPromptSubmit` hook. This file is exactly the read side's input.

## 5. Capabilities and caveats
- Observe without risk by wiring only the non-blocking events
  (`SessionStart`/`PostToolUse`/`PostToolUseFailure`/`SessionEnd`); gate by wiring
  `PreToolUse`.
- **Self-model gotcha**: Kimi's trained self-model wrongly believes it has no
  hooks. It does. A session will re-derive that error unless corrected (the hestia
  adapter carries the correction in its `AGENTS.md`).
- **Approval modes are a separate layer from hooks (verified live, v0.28.1).** Kimi
  has three approval modes — `manual` / `auto` / `yolo` — set by flag, by config
  (`default_permission_mode`), or in-session (`/permission`, `/auto`, `/yolo`). Their
  aggressiveness has *shifted across versions*, so pin the version when reasoning about
  them: in **v0.28.1**, `--auto` is the fully-autonomous "never ask" mode (the closest
  analog to Claude's `--dangerously-skip-permissions`) and `-y`/`--yolo` is milder
  ("auto-approve regular tool calls; the agent may still ask"); the ~v0.26 build had
  `--yolo` as the auto-approve-everything one. Regardless of which is most permissive,
  these control only the interactive **approval prompt** — they do **not** suppress the
  hook subsystem: a `PreToolUse` hook still fires and its `exit 2` deny is still
  honored, verified under the *most* permissive mode (`auto`) on v0.28.1 (a destructive
  Bash call was gated and denied). A gate sits *below* the approval layer and cannot be
  bypassed by any approval mode.
- **Headless guard**: `-p`/`--prompt` refuses to combine with `-y` or `--auto`
  ("Cannot combine --prompt with --yolo"), so `kimi -p -y` in a script is blocked;
  headless auto-approve requires setting `default_permission_mode` in config.
- **Session resume**: `-c`/`--continue` (resume the cwd's previous session) and
  `-S`/`--session [id]` mirror Claude Code's `--continue`/`--resume`.
- **No SessionStart context injection (verified live, v0.28.1).** The `SessionStart`
  hook *fires*, but Kimi injects **neither** raw hook stdout **nor** a Claude-style
  `hookSpecificOutput.additionalContext` JSON into the model's context (both tested, a
  sentinel emitted from a SessionStart hook does not reach the model). So unlike Claude
  Code, there is **no live recall-at-boot channel via hooks**. A memory/recall adapter
  must instead rewrite the deployed `AGENTS.md` (which *is* assembled into the system
  prompt at the next boot) — that is the only working injection path. Emitting a context
  block to hook stdout is a silent no-op.
