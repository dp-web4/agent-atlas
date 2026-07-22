---
harness: Lingma / Qoder CN CLI
ctx_provider: lingma
vendor: Alibaba Cloud
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [UserPromptSubmit, PreToolUse]
fails_open: true
config_path: ~/.lingma/settings.json
config_format: json
fidelity: documented
sources:
  - https://help.aliyun.com/en/lingma/qoder-cn/user-guide/hooks
  - https://help.aliyun.com/en/lingma/qodercli-cn/user-guide/using-the-cli
---

# Talk-to: Lingma / Qoder CN CLI

**Fidelity: documented** - Alibaba Cloud's official Qoder CN (formerly Lingma)
help center documents the hook lifecycle, the `settings.json` shape, exit-code
blocking, and the timeout/error behavior directly.

## 1. Identity
- **Harness**: Lingma, Alibaba Cloud's AI coding assistant. It ships both an IDE
  plugin (VS Code / JetBrains, agent mode) and a terminal agent, the **Qoder CN
  CLI** (formerly Lingma; command `qoderclicn`). The gate surface described here
  is the CLI's.
- **ctx provider (read)**: `lingma`.
- **Lineage**: a **Claude-Code-lineage** clone. Its hook engine mirrors Claude
  Code's event names, `settings.json` layout, exit-code convention, and fail-open
  semantics point-for-point (the docs never name Claude Code, but the surface is
  identical). Inherits the failure model in [`../claude/descriptor.md`](../claude/descriptor.md).

## 2. Hook engine
- **Events**: `UserPromptSubmit`, `PreToolUse`, `PostToolUse`,
  `PostToolUseFailure`, `Stop`.
- **Blocking-capable events**: `UserPromptSubmit` and `PreToolUse` only. A hook
  blocks by `exit 2` (stderr is fed back to the agent), or by `exit 0` with a
  JSON `permissionDecision: "deny"` on stdout for finer control. `PostToolUse`,
  `PostToolUseFailure`, and `Stop` are observational.
- **Failure mode**: **the engine FAILS OPEN.** The docs state a hook timeout
  (default 30s) is treated as an error and *execution continues*; anything short
  of an explicit `exit 2` / `deny` lets the operation proceed. **Consequence: the
  gate script itself must be fail-closed** — default to `exit 2` and only reach a
  passing exit on an explicit, confirmed allow.

## 3. Config
- **Path**: merged lowest-to-highest precedence: `~/.lingma/settings.json`
  (user), `.lingma/settings.json` (project, shareable),
  `.lingma/settings.local.json` (project-local, wins).
- **Format**: JSON. A `hooks` map keys each event to `matcher` entries (scope by
  tool name, e.g. `Bash`) plus a `hooks` array of `{type: "command", command: ...}`.
- **Also present**: a separate `permissions` block (`allow` / `deny` / `ask`
  lists) gives a declarative, non-script gate; MCP servers via `qoderclicn mcp add`;
  subagents and slash-commands as markdown files.

## 4. Transcript pointer
- The help center does not document a session-transcript path or format for the
  CLI. Treat this as **unknown** until confirmed on disk; the ctx read side is the
  authority once a wire file is located (expect it under `~/.lingma/` given the
  Claude-Code-lineage layout, but that is inference, not documented).

## 5. Capabilities and caveats
- Full observe + gate: witness with `PostToolUse` / `PostToolUseFailure` / `Stop`,
  gate with `PreToolUse` and `UserPromptSubmit`.
- The IDE-plugin variant (agent mode 2.5.0+) exposes MCP and Allow/Deny/Ask
  permission rules but not the scriptable command-hook engine described above —
  the CLI is the surface a hestia-style gate wires against.
- Product naming churns (Lingma → Qoder CN); pin the CLI version and confirm the
  `~/.lingma/` vs `~/.qoder-cn/` config root for the build in hand.
