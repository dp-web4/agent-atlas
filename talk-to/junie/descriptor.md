---
harness: Junie (JetBrains)
ctx_provider: junie
vendor: JetBrains
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: unknown
subagent_hooks_inherited: untested
config_path: ~/.junie/allowlist.json
config_format: json
resource_type: [subscription]
fidelity: documented
sources:
  - https://junie.jetbrains.com/docs/junie-cli.html
  - https://junie.jetbrains.com/docs/junie-cli-mcp-configuration.html
  - https://junie.jetbrains.com/docs/junie-plugin-settings.html
  - https://www.jetbrains.com/help/ai-assistant/junie-agent.html
---

# Talk-to: Junie (JetBrains)

**Fidelity: documented** - built from JetBrains' official Junie CLI/plugin docs.
The finding here is a documented *absence* of a scriptable hook/gate surface.

## 1. Identity
- **Harness**: Junie, JetBrains' coding agent — lives inside the JetBrains IDEs and
  as a separate Junie CLI.
- **ctx provider (read)**: `junie`.
- **Lineage**: **independent.** Not a Claude-Code hook clone. Its extension surface
  is MCP (tool provider) plus `AGENTS.md` guidelines; its safety surface is
  interactive human approval, not scriptable lifecycle hooks.

## 2. Hook engine
- **No programmatic hook engine.** Junie exposes no `PreToolUse`/`PostToolUse`-style
  scriptable events that an external tool can register to observe or block a tool
  call. There is nothing to wire an out-of-process gate into.
- **How gating actually works — human-in-the-loop, not scriptable.** Sensitive
  actions (most terminal commands, editing files outside the project, MCP tool
  calls) prompt the user for approval. **Brave Mode** (toggle `/brave` or `Ctrl+B`)
  sets the posture: `Off` asks for everything not allowlisted, `Auto` auto-approves
  safe commands and asks on risky/unknown ones, `On` runs all sensitive actions
  without prompting. "Always allow" during a prompt appends to the allowlist. This
  is a UI consent gate, so engine fail-open/closed semantics don't apply
  (`fails_open: unknown`).
- **blocking_capable: false** — for this registry's purpose (a tool that
  programmatically observes/denies actions), Junie offers no such hook. Blocking is
  a human at the keyboard.

## 3. Config
- **Path**: `~/.junie/allowlist.json` (approved commands/patterns for the Action
  Allowlist). Guidelines/memory live in `.junie/AGENTS.md` (fallback: `AGENTS.md` at
  project root). MCP servers are declared in `.junie/mcp/mcp.json` (project or
  global), under an `mcpServers` key.
- **Format**: JSON (allowlist, mcp.json); Markdown for `AGENTS.md`.
- **Knobs that matter**: Brave Mode level is the real safety dial; the allowlist
  determines what runs without a prompt.

## 4. Transcript pointer
- **Path pattern**: a `transcript.md` file is written next to the session's
  `events.jsonl`; subagent transcripts live in the session's `subagents/` folder
  (viewable via `Ctrl+O`). The `events.jsonl` alongside it is the structured
  read-side input; ctx is the read-side authority for the exact session directory.

## 5. Capabilities and caveats
- **Read-side, not gate-side.** Junie can be *observed* (the `events.jsonl` /
  `transcript.md` per session) but not *gated* by an external hook. To enforce
  policy you must lean on Brave Mode + the allowlist, or restrict what MCP servers
  are wired in — none of which an out-of-process gate can drive.
- MCP is the only programmatic extension surface, and it is a tool-provider
  (capability-adding) surface, not a policy/deny surface.
