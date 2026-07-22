---
harness: Windsurf (Cascade)
ctx_provider: windsurf
vendor: Codeium / Cognition
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [pre_user_prompt, pre_read_code, pre_write_code, pre_run_command, pre_mcp_tool_use]
fails_open: true
config_path: ~/.codeium/windsurf/hooks.json
config_format: json
fidelity: documented
sources:
  - https://docs.windsurf.com/windsurf/cascade/hooks
  - https://docs.devin.ai/desktop/cascade/hooks
  - https://docs.windsurf.com/windsurf/cascade/mcp
---

# Talk-to: Windsurf (Cascade)

**Fidelity: documented** - from Windsurf's official Cascade Hooks reference
(docs.windsurf.com now redirects to docs.devin.ai under Cognition); the event
list, exit-code semantics, and config paths are all documented.

## 1. Identity
- **Harness**: Windsurf, the AI editor from [Codeium](https://codeium.com/)
  (now under Cognition/Devin), built around the **Cascade** agent.
- **ctx provider (read)**: `windsurf`.
- **Lineage**: **independent** event taxonomy, but it deliberately borrows Claude
  Code's gate convention: **pre-hooks block with exit code `2`, any other exit
  code proceeds** — i.e. the same fail-open contract. Treat its failure model as
  Claude-like even though the event names differ.

## 2. Hook engine
- **Events (12)**: pre-hooks `pre_user_prompt`, `pre_read_code`, `pre_write_code`,
  `pre_run_command`, `pre_mcp_tool_use`; post-hooks `post_read_code`,
  `post_write_code`, `post_run_command`, `post_mcp_tool_use`,
  `post_cascade_response`, `post_cascade_response_with_transcript`,
  `post_setup_worktree`.
- **Blocking-capable events**: the five **pre-hooks only**. A pre-hook blocks by
  exiting `2` (stderr is shown to the user); post-hooks cannot block.
- **Exit-code semantics**: `0` = proceed; `2` = block (pre-hooks only); **any
  other code = proceed.**
- **Failure mode**: **the engine FAILS OPEN.** Only a clean `exit 2` denies; a
  hook that errors, times out, or exits with any unexpected code lets the action
  through. **A gate wired here must be fail-closed by construction**: emit `exit
  2` by default and only reach `exit 0` on an explicit confirmed allow.

## 3. Config
- **Path**: `hooks.json`, merged across three levels — system
  (`/etc/windsurf/hooks.json` on Linux, `C:\ProgramData\Windsurf\hooks.json`,
  `/Library/Application Support/Windsurf/hooks.json`), **user**
  (`~/.codeium/windsurf/hooks.json`; `~/.codeium/hooks.json` for JetBrains), and
  **workspace** (`.windsurf/hooks.json` at repo root).
- **Format**: JSON. A `hooks` map keys each event to a list of
  `{ "command": ..., "show_output": ... }` entries.
- MCP servers are configured separately in `~/.codeium/windsurf/mcp_config.json`.

## 4. Transcript pointer
- The `post_cascade_response_with_transcript` hook is handed the **full
  conversation as a JSONL file** at end of turn — the most direct read-side
  handle. The persistent on-disk store path is not documented here; the transcript
  hook is the reliable source.

## 5. Capabilities and caveats
- Observe via post-hooks; gate via pre-hooks. `pre_user_prompt` is the natural
  spot to screen prompts/injected instructions before Cascade acts.
- Because failure is fail-open, never rely on the engine to deny on hook error.
