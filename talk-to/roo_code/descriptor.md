---
harness: Roo Code
ctx_provider: roo_code
vendor: Roo Code (open source)
lineage: cline
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: n/a
subagent_hooks_inherited: untested
config_path: VS Code settings.json (roo-cline.* keys) + in-UI auto-approve
config_format: json
fidelity: documented
sources:
  - https://roocodeinc.github.io/Roo-Code/features/auto-approving-actions
  - https://deepwiki.com/RooCodeInc/Roo-Code/11.3-auto-approve-configuration
  - https://docs.roocode.com/features/mcp/using-mcp-in-roo
---

# Talk-to: Roo Code

**Fidelity: documented** - based on Roo Code's official auto-approve and MCP docs, which describe an in-app gate but **no external hook/lifecycle surface**. Recorded absence is the finding.

## 1. Identity
- **Harness**: [Roo Code](https://github.com/RooCodeInc/Roo-Code), an open-source VS Code coding-agent extension, forked from Cline.
- **ctx provider (read)**: `roo_code`.
- **Lineage**: **Cline fork.** Notably, Roo Code has **not** adopted Cline's v3.36 executable-script hook engine; as of these docs it has no equivalent external-script lifecycle system. So while its heritage is `cline`, its integration surface diverges (no hooks).

## 2. Hook engine
- **No external hook engine.** There is no PreToolUse/PostToolUse-style event system that runs a user script to allow/deny a tool call. Gating is entirely **in-app**: an auto-approve system with per-category boolean toggles, evaluated per tool call inside the extension.
- **Auto-approve categories** (each an independent flag, all gated by a master `autoApprovalEnabled`): read, write, command execution (via allowlist/denylist), browser, MCP tools (dual-permission: global "always approve MCP" + per-tool "Always allow"), mode switching, subtasks, follow-up questions.
- **Blocking-capable**: `false` in the sense this registry cares about — there is no seam for an *external* gate/witness to intercept a tool call. A human (or a static allow/deny list) is the only gate. There is no fail-open/closed hook question because there is no hook.

## 3. Config
- **Path/format**: managed through the VS Code Settings UI (Settings -> Auto-Approve) and VS Code `settings.json` for command lists, under keys like `roo-cline.allowedCommands` / `roo-cline.deniedCommands` (JSON). No dedicated Roo hooks config file exists.

## 4. Transcript pointer
- **Path pattern**: **unknown / not a documented stable path.** Roo persists task history in the extension's VS Code `globalStorage` (per-task directories under the `rooveterinaryinc.roo-cline` storage namespace), similar to Cline. Treat the layout as version-dependent; the read side (`ctx`) is the authority.

## 5. Capabilities and caveats
- **No programmatic gate/witness seam.** To supervise Roo Code externally you are limited to (a) the static command allow/deny lists, (b) leaving auto-approve off so a human confirms each action, or (c) tailing the globalStorage task files after the fact.
- If Roo later mirrors Cline's hook engine, this descriptor should be revised toward `../cline/descriptor.md`; until then, absence is the honest record.
