---
harness: Warp (Agent Mode)
ctx_provider: warp
vendor: Warp (Warp.dev)
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: unknown
subagent_hooks_inherited: untested
config_path: unknown
config_format: json
resource_type: [subscription, free]
fidelity: documented
sources:
  - https://docs.warp.dev/agent-platform/capabilities/agent-profiles-permissions/
  - https://docs.warp.dev/agent-platform/capabilities/mcp/
  - https://docs.warp.dev/guides/external-tools/using-mcp-servers-with-warp/
  - https://docs.warp.dev/terminal/settings/all-settings/
---

# Talk-to: Warp (Agent Mode)

**Fidelity: documented** - based on Warp's official agent-platform docs. The
finding is that Warp has a native permission gate but **no user-scriptable hook
engine**.

## 1. Identity
- **Harness**: Warp, the agentic terminal from [Warp.dev](https://warp.dev/),
  and its **Agent Mode** / local-agents surface.
- **ctx provider (read)**: `warp`.
- **Lineage**: independent. Warp is a closed-source app; there is no
  Claude-Code-style shell hook engine or external gate-insertion point.

## 2. Hook engine
- **No user-scriptable hook engine.** Warp exposes **no** lifecycle events or
  command hooks that a third party can wire in to observe or block a tool call
  with its own code. There is therefore no `exit 2` / `decision:deny` contract to
  document.
- **Native (built-in) gate**: Warp *does* gate commands, but only through its own
  UI-configured permission model, not a pluggable hook:
  - **Autonomy levels** per action type — "Agent Decides", "Always ask", "Always
    allow", "Never" (Never blocks outright).
  - **Command allowlist** — regex patterns that auto-execute (e.g. `ls(\s.*)?`).
  - **Command denylist** — regex patterns that force approval regardless of other
    settings (defaults include `rm(\s.*)?`, `curl(\s.*)?`, `wget(\s.*)?`). **The
    denylist takes precedence** over the allowlist and "Agent Decides".
  This is real blocking, but it is native and static (regex + autonomy), not a
  place to inject an external fail-closed gate — hence `blocking_capable: false`
  for the talk-to sense of "a tool hooks in and decides". Its failure mode is
  internal and undocumented (`fails_open: unknown`).
- **Extension point that exists**: **MCP servers** (Settings > Agents > MCP
  servers, Warp Drive, or file-based config). MCP adds *tools*, not *gates* —
  it cannot intercept or veto the agent's other tool calls.

## 3. Config
- **Path**: primarily UI-managed (Settings > Agents > Profiles / MCP servers);
  no documented single settings file for profiles/permissions. Warp
  **auto-discovers** MCP config from `~/.claude.json`, `.mcp.json`, or
  `.codex/config.toml`, so MCP servers can be shared with Claude Code / Codex.
- **Format**: JSON for the file-based MCP config (TOML when reusing Codex's
  `config.toml`). Rules/permissions themselves are set in-app.
- **Knobs that matter**: `rules_enabled` (bool, default true) toggles saved-rule
  context; Agent Profiles scope autonomy, model, tool access, and per-profile MCP
  access.

## 4. Transcript pointer
- **Path pattern**: not documented / not exposed as an on-disk transcript. Warp
  keeps agent conversations in-app; there is no published JSONL session path.
  ctx is the read-side authority.

## 5. Capabilities and caveats
- **Observe/gate**: no external hook path. You get Warp's native allow/deny/
  autonomy controls and MCP tool-adding, but you cannot insert an automated
  witness or a custom fail-closed gate into Warp's tool loop.
- Recorded absence is the finding: Warp is MCP-capable and has a decent built-in
  permission gate, but offers **no talk-to hook surface** for third-party gating.
