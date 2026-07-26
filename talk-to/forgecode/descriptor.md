---
harness: Forge Code
ctx_provider: forgecode
vendor: Antinomy (antinomyhq; forgecode.dev)
lineage: independent
hook_engine: false
blocking_capable: true
blocking_events: []
fails_open: false
subagent_hooks_inherited: untested
config_path: .forge.toml (project); ~/.forge/permissions.yaml (gate)
config_format: toml (permissions: yaml; mcp: json)
fidelity: documented
sources:
  - https://forgecode.dev/docs/permissions/
  - https://forgecode.dev/docs/
  - https://github.com/antinomyhq/forgecode
  - https://www.teamday.ai/harness/forgecode
---

# Talk-to: Forge Code

**Fidelity: documented** - assembled from forgecode.dev docs and the antinomyhq
repo; the gate is a static config ACL, not a programmable hook, so it wasn't
exercised.

## 1. Identity
- **Harness**: Forge Code (a.k.a. Forge / ForgeCode), an open-source terminal AI
  coding agent from [Antinomy / antinomyhq](https://github.com/antinomyhq/forgecode),
  Apache-2.0, distributed as `@antinomyhq/forge`.
- **ctx provider (read)**: `forgecode`.
- **Lineage**: independent. It is **not** a Claude-Code hook-engine clone - it has
  no `PreToolUse`-style programmable lifecycle hook.

## 2. Hook engine
- **No programmable lifecycle hook engine.** Forge exposes only *outbound* event
  dispatch (`forge -e/--event <JSON>`), which pushes an event *into* a workflow; it
  is not a pre-tool interception point that a third party can register a blocking
  command against. There is no `PreToolUse`/exit-code-2 contract here.
- **Blocking does exist, but via a static permission ACL, not a hook.** When
  `restricted = true` is set in `.forge.toml`, Forge enforces
  `~/.forge/permissions.yaml`: rules over four operation classes (`read`, `write`,
  `command`, `url`), each with glob matching and one of `allow` / `deny` / `confirm`.
  Policies are scanned in order; a matching `deny`/`confirm` stops evaluation.
- **Failure mode**: the ACL is **fail-safe by default in the sense that no matching
  policy resolves to `confirm` (prompt), not `allow`** - so it does not silently
  fail open to permit an unmatched action. Two important gaps: (a) the gate is
  **opt-in** - with `restricted` unset, tools run unprompted; (b) it covers
  **built-in tools only** (Read/Write/Shell/Fetch) - **MCP tools bypass the
  permission system entirely.** A gate built on this must account for that MCP hole.

## 3. Config
- **Path**: `.forge.toml` (project-level primary config); `~/.forge/permissions.yaml`
  (permission ACL); `.mcp.json` / `~/.forge/.mcp.json` (MCP servers); `AGENTS.md`,
  `.forge/agents/`, `.forge/skills/<name>/SKILL.md` for agent/skill customization.
- **Format**: TOML for `.forge.toml`; YAML for `permissions.yaml`; JSON for
  `.mcp.json`.
- **Knobs that matter**: `restricted = true` to arm the ACL; `permissions.yaml`
  supports `all`/`any`/`not` logic and `dir` scoping; a `confirm` prompt can
  auto-append a matching allow rule. Also `FORGE_TOOL_TIMEOUT` (default 300s) and
  `--sandbox` (isolated git worktree+branch) for safety, but those are containment,
  not gating.

## 4. Transcript pointer
- **Unknown / undocumented.** Conversations are persistent and resumable
  (`forge conversation resume <id>`, `:compact`), implying local storage, but the
  official docs do not state a path or format. Treat the transcript location as
  undiscovered pending a live-install probe; the ctx read side is authoritative.

## 5. Capabilities and caveats
- You can gate built-in file/shell/network ops declaratively via `permissions.yaml`,
  but you cannot register an arbitrary program as a pre-tool decision hook, and you
  cannot gate MCP-provided tools at all through this surface.
- Because the gate is static config rather than an executable hook, a "talk-to"
  integration that needs dynamic, audited, fail-closed decisions can't fully live
  inside Forge - the MCP bypass and opt-in enforcement are the load-bearing caveats.

## Sources
- Permission model (permissions.yaml, allow/deny/confirm, MCP bypass) - https://forgecode.dev/docs/permissions/
- Config files overview - https://forgecode.dev/docs/
- Repo / identity / license - https://github.com/antinomyhq/forgecode
- Harness summary (hooks partial, no lifecycle gate) - https://www.teamday.ai/harness/forgecode
