---
harness: Trae (AI IDE)
ctx_provider: trae
vendor: ByteDance
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: unknown
config_path: .trae/rules/project_rules.md
config_format: markdown
fidelity: documented
sources:
  - https://traeide.com/news/6
  - https://www.aibase.com/news/www.aibase.com/news/17375
  - https://github.com/bytedance/trae-agent
  - https://github.com/bytedance/trae-agent/issues/397
---

# Talk-to: Trae (AI IDE)

**Fidelity: documented** - based on Trae's v1.3.0 release notes and the
bytedance/trae-agent repo/issues. The finding is that Trae has MCP + rules but
**no hook/gate engine**.

## 1. Identity
- **Harness**: Trae, the AI IDE from **ByteDance** ([traeide.com](https://traeide.com/)).
  Distinct from **trae-agent**, ByteDance's separate open-source Python CLI
  agent — noted here because searches conflate them.
- **ctx provider (read)**: `trae`.
- **Lineage**: independent. Trae's extensibility is MCP + `.rules`, not a
  Claude-Code-style hook engine.

## 2. Hook engine
- **No hook engine, in either product.**
  - **Trae IDE**: v1.3.0 added **MCP** (external tools/data) and **`.rules`**
    (behavioral context). Neither intercepts or blocks a tool call; `.rules` is
    prompt-context loaded at agent init, and MCP only *adds* tools. There is no
    lifecycle-event / pre-tool-gate mechanism, so no `exit 2` / `decision:deny`
    contract exists.
  - **trae-agent (CLI)**: lifecycle hooks are an **open feature request**
    ([issue #397](https://github.com/bytedance/trae-agent/issues/397)) —
    explicitly *not implemented*. The request notes trae-agent "is invisible to
    this entire ecosystem" without hooks and asks for a subprocess-JSON push
    model that could "gate dangerous operations". Until it ships there is no
    blocking path (`blocking_capable: false`, `fails_open: unknown`).
- **Watch item**: if #397 lands, trae-agent would gain a Claude-lineage-style
  subprocess/JSON hook surface; revisit then.

## 3. Config
- **Path**: `.rules` files — project-level `project_rules.md` and user-level
  `user_rules.md` (Trae surfaces these under a rules panel; commonly under a
  `.trae/rules/` project dir). MCP servers are added via an `mcp_servers`
  configuration.
- **Format**: **Markdown** for `.rules`; **YAML** for the `mcp_servers` block
  (per the v1.3.0 notes). There is no JSON `hooks` map — nothing here runs an
  external command around a tool call.
- **Knobs that matter**: `.rules` is context-shaping only; it cannot enforce a
  gate. MCP config is documented as having a relatively high setup barrier and
  `.rules` lacks an official syntax spec (per ByteDance's own v1.3.0 notes).

## 4. Transcript pointer
- **Path pattern**: not documented for the IDE. trae-agent (CLI) writes
  trajectory/telemetry to its own working files, but no stable JSONL session path
  is published for the IDE. ctx is the read-side authority.

## 5. Capabilities and caveats
- **Observe/gate**: no programmatic hook path today. You can add MCP tools and
  shape behavior with `.rules`, but you cannot insert an automated witness or a
  fail-closed gate into Trae's tool loop.
- Recorded absence is the finding: Trae is MCP + rules capable but has **no
  talk-to hook surface**; the CLI sibling has the capability only as an open
  request.
