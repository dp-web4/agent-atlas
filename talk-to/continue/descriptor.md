---
harness: Continue
ctx_provider: continue
vendor: Continue.dev
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: unknown
subagent_hooks_inherited: untested
config_path: ~/.continue/config.yaml
config_format: yaml
fidelity: documented
sources:
  - https://docs.continue.dev/customize/deep-dives/configuration
  - https://docs.continue.dev/cli/tool-permissions
  - https://docs.continue.dev/customize/mcp-tools
---

# Talk-to: Continue

**Fidelity: documented** - from Continue's official config, tool-permissions, and
MCP docs. The finding is a recorded *absence*: Continue exposes no external
lifecycle-hook gate.

## 1. Identity
- **Harness**: Continue ([Continue.dev](https://www.continue.dev/)), an
  open-source IDE extension (VS Code / JetBrains) and CLI (`cn`) offering
  autocomplete, chat, and agent modes.
- **ctx provider (read)**: `continue`.
- **Lineage**: **independent.** YAML-configured; no Claude-Code hook engine.

## 2. Hook engine
- **No external hook / event surface.** Continue documents no lifecycle events
  (no PreToolUse-style callback), no way to register an external command that runs
  before/after a tool call, and no programmable pre-tool gate. Extensibility is
  **MCP servers** (add tools) plus **rules** (shape behavior) — neither can
  intercept and deny another tool's execution.
- **Blocking that exists is not programmable**: a static **Tool Permissions**
  policy (`allow` / `ask` / `exclude`, defaults: read-only tools allow, write &
  Bash ask) plus **interactive human approval** in the IDE. Policies are declared
  in `~/.continue/permissions.yaml` or via `--allow/--ask/--exclude` CLI flags;
  approvals you grant are appended back to `permissions.yaml`. There is no place
  to route a decision to an external witness/gate process, so
  `blocking_capable: false` for the purposes of a programmable gate.
- **Failure mode**: n/a (no hook engine); `fails_open: unknown`.

## 3. Config
- **Path**: `~/.continue/config.yaml` (global); workspace rules in
  `.continue/rules/`; permissions in `~/.continue/permissions.yaml`. Legacy
  `config.json` / `.continuerc.json` are deprecated.
- **Format**: YAML. Config composes `models`, `rules`, `context`, `mcpServers`,
  `prompts`, `docs` blocks (reusable via `uses: owner/item-name` slugs).

## 4. Transcript pointer
- **Not documented** in the sources reviewed. Session history is kept by the
  extension/CLI under `~/.continue/`, but no stable transcript path/format is
  published. ctx would be the read-side authority; treat the path as unverified.

## 5. Capabilities and caveats
- Good for adding tools/context (MCP) and shaping behavior (rules); **not** a
  place to enforce a fail-closed gate — the only enforcement is static policy plus
  a human clicking approve.
- Recorded absence is the finding: if you need to gate Continue, you must do it
  outside Continue (e.g. sandbox/OS layer), not via a Continue hook.
