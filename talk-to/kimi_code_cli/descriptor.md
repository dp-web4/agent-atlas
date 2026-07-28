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
