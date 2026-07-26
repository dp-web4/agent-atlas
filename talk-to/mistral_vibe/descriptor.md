---
harness: Mistral Vibe
ctx_provider: mistral_vibe
vendor: Mistral AI
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [pre_tool, post_tool, post_agent]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.vibe/config.toml (config); ~/.vibe/hooks.toml + ./.vibe/hooks.toml (hooks)
config_format: toml
fidelity: documented
sources:
  - https://docs.mistral.ai/vibe/code/cli/hooks
  - https://github.com/mistralai/mistral-vibe
  - https://github.com/mistralai/mistral-vibe/blob/main/CHANGELOG.md
  - https://docs.mistral.ai/vibe/code/cli/mcp-servers
---

# Talk-to: Mistral Vibe

**Fidelity: documented** - from Mistral's official Vibe hooks docs plus the
mistralai/mistral-vibe repo (README, CHANGELOG, `vibe/core/hooks/*`); the
mechanics were read, not run.

## 1. Identity
- **Harness**: Vibe (Mistral Vibe) - Mistral AI's minimal CLI coding agent
  (`mistral-vibe`, Python).
- **ctx provider (read)**: `mistral_vibe`.
- **Lineage**: **claude-lineage shell-hook engine, with meaningful divergence.**
  It clearly mirrors the Claude-Code model - shell-command hooks that receive JSON
  on stdin (`session_id`, `parent_session_id`, `transcript_path`, `cwd`,
  `hook_event_name`), and block by emitting `"decision": "deny"`. But it renames
  the events, ships a smaller set, and - crucially - adds a `strict` flag that can
  flip the failure mode (see below). See [`../claude/descriptor.md`](../claude/descriptor.md)
  for the shared lineage semantics.

## 2. Hook engine
- **Events**: three types, all declared in `hooks.toml`:
  - `pre_tool` - fires before the user permission prompt, per tool call.
  - `post_tool` - fires after a tool body actually ran (skipped on pre_tool deny,
    user denial, permission `NEVER`, or pre-body cancellation).
  - `post_agent` - fires after an assistant turn that has no pending tool calls.
  (Per the CHANGELOG these graduated from experimental; the old names
  `before_tool`/`after_tool`/`post_agent_turn` were renamed to the above.)
- **Blocking-capable**: `pre_tool` blocks the call (`decision: "deny"`; the reason
  is surfaced to the LLM as a tool error). `post_tool` deny replaces the tool's
  output text with the reason. `post_agent` deny injects a retry request (capped at
  3 retries per hook per turn). Hooks are shell `command`s with a `timeout`
  (default per docs ~60s; README examples show a `timeout` field).
- **Failure mode**: **DEFAULT FAILS OPEN.** With `strict = false` (the default) a
  hook that exits non-zero, times out, fails to spawn, or emits malformed JSON
  **degrades to a warning and the action proceeds**. This inherits the lineage
  footgun, so **a gate on Vibe must be fail-closed by construction** - deny by
  default, reach allow only on a confirmed pass.
  - **Divergence worth noting**: setting `strict = true` flips this - the same
    failures become *denials* instead of warnings. Vibe is one of the few
    Claude-lineage clones that can be configured fail-closed at the engine level.
    Even so, don't rely on it alone; `strict` is opt-in and per-config, so the gate
    logic should still self-fail-closed.

## 3. Config
- **Path**: `~/.vibe/config.toml` (main config: model, `[[mcp_servers]]`,
  `[tools.<name>]` permissions, `enabled_tools`/`disabled_tools`). Hooks live in a
  **separate** `hooks.toml`: `./.vibe/hooks.toml` (project, trusted folders only,
  takes precedence) and `~/.vibe/hooks.toml` (user fallback).
- **Format**: TOML. A hook entry needs `name`, `type` (`pre_tool`|`post_tool`|
  `post_agent`), `command`; optional `timeout`, `description`, and `match` (glob on
  tool name, valid only for the tool hooks). `strict` controls fail-open vs
  fail-closed.
- **Knobs that matter**: `strict = true` to make hook failures deny; `match` to
  scope a `pre_tool` gate to specific tools; note tool `permission` blocks and
  `enabled_tools`/`disabled_tools` are a separate, static tool-access layer.

## 4. Transcript pointer
- **Path**: not hardcoded in the public docs, but every hook is handed a
  `transcript_path` on stdin - so the session transcript is a real local file and
  the read side can take the path straight from the hook payload rather than
  guessing a location. Sessions are stored locally (ADR "Local Sessions"); general
  logs land at `~/.vibe/logs/vibe.log`. Prefer the `transcript_path` the engine
  provides over assuming a fixed layout.

## 5. Capabilities and caveats
- Full observe + gate: wire `post_tool`/`post_agent` to witness, and `pre_tool`
  (with `match`) to gate risky calls. `pre_tool` fires *before* the permission
  prompt, so it can deny outright.
- Set `strict = true` to harden the engine, but still build the gate itself
  fail-closed - `strict` is opt-in and the default engine behavior is fail-open.
- The `transcript_path` handed to each hook is the cleanest read-side input on this
  harness; use it instead of hardcoding a sessions directory.

## Sources
- Vibe hooks spec (events, decision deny, strict fail-closed) - https://docs.mistral.ai/vibe/code/cli/hooks
- Repo (README hook examples, `vibe/core/hooks/*`) - https://github.com/mistralai/mistral-vibe
- CHANGELOG (hooks stable; event renames) - https://github.com/mistralai/mistral-vibe/blob/main/CHANGELOG.md
- config.toml + MCP + tool permissions - https://docs.mistral.ai/vibe/code/cli/mcp-servers
