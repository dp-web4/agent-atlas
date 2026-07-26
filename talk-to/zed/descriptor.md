---
harness: Zed (Agent Panel)
ctx_provider: zed
vendor: Zed Industries
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: unknown
subagent_hooks_inherited: untested
config_path: ~/.config/zed/settings.json
config_format: json
fidelity: documented
sources:
  - https://zed.dev/docs/ai/agent-panel
  - https://zed.dev/docs/ai/agent-settings
  - https://zed.dev/docs/assistant/model-context-protocol
  - https://github.com/zed-industries/zed/discussions/57943
  - https://github.com/zed-industries/zed/issues/57890
  - https://github.com/zed-industries/zed/issues/52688
---

# Talk-to: Zed (Agent Panel)

**Fidelity: documented** - based on Zed's official AI docs plus the open
GitHub discussion/issues for the proposed hook feature. The absence of a shipped
hook engine is the load-bearing finding.

## 1. Identity
- **Harness**: Zed, the Rust editor from
  [Zed Industries](https://zed.dev/), and its **Agent Panel** AI surface.
- **ctx provider (read)**: `zed`.
- **Lineage**: independent. The Agent Panel connects to external coding agents
  over the **Agent Client Protocol (ACP)** and adds tools via **MCP context
  servers** — neither of which is a Claude-Code-style shell hook engine.

## 2. Hook engine
- **No shipped hook engine.** As of this writing there is **no** user-scriptable
  lifecycle-hook / pre-tool-gate mechanism for Zed's built-in agent. Blocking a
  tool call is only possible through Zed's interactive **tool permission
  prompts** (the human clicks allow/deny), not through a programmable gate.
- **Proposed, not implemented**: discussion
  [#57943](https://github.com/zed-industries/zed/discussions/57943) and issues
  [#57890](https://github.com/zed-industries/zed/issues/57890) /
  [#52688](https://github.com/zed-industries/zed/issues/52688) propose settings-
  based lifecycle hooks (`session_start`, `pre_tool_use`, `post_tool_use`,
  `generation_end`, `tool_permission_denied`) configured under an `agent.hooks`
  key with `$ZED_TOOL_NAME`-style env vars. Community comments explicitly ask for
  the ability to **block risky shell commands before execution**, but the
  proposal does not yet specify a blocking contract or a failure mode — so
  `blocking_capable` and `fails_open` are **not applicable / unknown** until it
  ships.
- **Watch item**: if `pre_tool_use` lands with a block path, revisit this
  descriptor; it would likely inherit an env-var-over-stdin design closer to
  Zed's own conventions than to Claude's exit-code-2.

## 3. Config
- **Path**: `~/.config/zed/settings.json` (Linux/macOS;
  `%APPDATA%\Zed\settings.json` on Windows).
- **Format**: JSON. MCP tool servers are keyed under **`context_servers`** (note:
  not `mcpServers` as in Cursor), each `{command, args, env}` run as a child
  process. Agent behavior (auto-compaction threshold, providers) also lives here.
- **Knobs that matter**: the only current "gate" lever is turning off agent
  autonomy / requiring tool-permission prompts; there is no config key that runs
  an external command before a tool call today.

## 4. Transcript pointer
- **Path pattern**: not documented in the reviewed pages. Agent threads are
  stored/compacted internally (auto-compaction fires at 90% of context), but Zed
  does not publish an on-disk JSONL transcript path the way the CLI harnesses do.
  ctx is the read-side authority.

## 5. Capabilities and caveats
- **Observe/gate today**: no programmatic path — you can add MCP tools and rely
  on interactive permission prompts, but you cannot insert an automated witness
  or fail-closed gate into the built-in agent's tool loop.
- Recorded absence is the finding: Zed is a strong MCP host but currently has
  **no talk-to hook surface**. This is a moving target — the feature is in active
  discussion.
