# Talk-to: Kimi Code CLI

**Fidelity: verified** - reverse-engineered and wired against the real Kimi Code
CLI in [hestia/plugins/kimi](https://github.com/dp-web4/hestia/tree/main/plugins/kimi),
run in warn and enforce modes.

## 1. Identity
- **Harness**: Kimi Code CLI ([Moonshot AI](https://www.moonshot.ai/)).
- **ctx provider (read)**: `kimi_code_cli` (ctx source-format id `kimi_code_cli_wire_jsonl_tree`).
- **Lineage**: a near-clone of Claude Code's hook engine. Its failure semantics and
  event model follow the Claude-Code lineage; see [`claude-code.md`](claude-code.md).

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
- **Knobs that matter**: set `[upgrade] auto_install = false` in `tui.toml` so the
  audited binary does not silently drift under you.

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
