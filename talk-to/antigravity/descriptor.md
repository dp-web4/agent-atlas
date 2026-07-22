---
harness: Antigravity
ctx_provider: antigravity
vendor: Google
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, Stop]
fails_open: false
config_path: ~/.gemini/config/hooks.json
config_format: json
fidelity: documented
sources:
  - https://antigravity.google/docs/hooks
  - https://antigravity.google/docs/plugins
  - https://antigravity.google/docs/cli/plugins
  - https://medium.com/google-cloud/a-developers-guide-to-agent-hooks-in-antigravity-cli-4c1440febd11
  - https://github.com/manaflow-ai/cmux/issues/5358
---

# Talk-to: Antigravity

**Fidelity: documented** - built from Google's official Antigravity hooks/plugins
docs plus a corroborating developer walkthrough; not run against a live gate here.

## 1. Identity
- **Harness**: Antigravity, Google's agentic IDE and CLI ("Gemini Antigravity"),
  built on the `~/.gemini` toolchain.
- **ctx provider (read)**: `antigravity`.
- **Lineage**: **claude-lineage in shape, divergent in failure mode.** The event
  model, `hooks.json` structure (`matcher` + `hooks` + `command` arrays), and
  `exit 2` blocking convention are recognizably cloned from Claude Code
  ([`../claude/descriptor.md`](../claude/descriptor.md)). It then diverges: it adds
  `PreInvocation`/`PostInvocation`, a richer `decision` vocabulary, and — most
  importantly — it **fails closed** where Claude Code fails open.

## 2. Hook engine
- **Events**: `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`,
  `Stop`.
- **Blocking-capable events**: `PreToolUse` gates tool execution; `Stop` can block
  the agent from finishing. `PreToolUse` blocks either via `exit 2` or by emitting a
  `decision` JSON on stdout — the documented values are `allow`, `deny`, `ask`, and
  `force_ask`. `PostToolUse`/`Post|PreInvocation` are observational.
- **Failure mode**: **this engine FAILS CLOSED — a notable divergence from the
  Claude lineage.** The docs state that when a hook subprocess exceeds its timeout
  (default 30-60s), the engine kills it (SIGTERM / `taskkill`) and *aborts the
  turn*; a killed or erroring `PreToolUse` hook is treated as a denial and the tool
  call is rejected (independently reproduced downstream: an injected hook that
  errored denied *every* tool call, cmux issue #5358). So unlike Kimi/Claude, the
  engine itself denies on hook failure. A gate here still benefits from being
  explicit, but the ambient default protects rather than exposes you.

## 3. Config
- **Path**: `~/.gemini/config/hooks.json` (global) or `<workspace>/.agents/hooks.json`
  (project); hooks may also live inside a plugin's `hooks.json` at the plugin root.
- **Format**: JSON. Plugins are namespaced bundles: `plugin.json` manifest plus
  optional `hooks.json` and `mcp_config.json`, dropped in `.agents/plugins/`
  (workspace) or `~/.gemini/config/plugins/` (global).
- **Knobs that matter**: each hook takes an optional `timeout` (seconds); the
  `matcher` field is a regex over tool names.

## 4. Transcript pointer
- **Path pattern**:
  `<app_data_dir>/brain/<conversationId>/.system_generated/logs/transcript.jsonl`,
  where `<app_data_dir>` is `~/.gemini/antigravity` (IDE) or `~/.gemini/antigravity-cli`
  (CLI). This is the read side's input.

## 5. Capabilities and caveats
- Full observe + gate: `PostToolUse` witnesses every call, `PreToolUse` gates the
  risky ones with a real fail-closed backstop from the engine.
- **Divergence to remember**: because Antigravity fails *closed*, a broken or slow
  gate hook will halt the agent rather than silently wave actions through — the
  opposite failure risk from the rest of the Claude lineage. Budget hook latency
  accordingly.
- MCP servers are configured separately via `mcp_config.json` (tool-provider
  surface, not a gate).
