---
harness: NanoClaw
ctx_provider: nanoclaw
vendor: nanoco.ai
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, UserPromptSubmit, Stop]
fails_open: true
subagent_hooks_inherited: untested
config_path: none (hooks configured programmatically via Claude Agent SDK ClaudeAgentOptions); .mcp.json for MCP servers
config_format: python / json
fidelity: inferred
sources:
  - https://github.com/nanocoai/nanoclaw
  - https://code.claude.com/docs/en/agent-sdk/hooks
---

# Talk-to: NanoClaw

**Fidelity: inferred** - NanoClaw's own docs are thin on hook internals, but it
states plainly that it runs directly on Anthropic's Claude Agent SDK, whose hook
engine is well documented. The hook facts below come from the SDK; NanoClaw's own
surface (no config files, SQLite stores) is documented in its repo.

## 1. Identity
- **Harness**: NanoClaw (`nanocoai/nanoclaw`), a lightweight, container-isolated
  alternative to OpenClaw that bridges messaging apps (WhatsApp, Telegram, Slack,
  Discord, Gmail) to an agent with memory and scheduled jobs.
- **ctx provider (read)**: `nanoclaw`.
- **Lineage**: **Claude-Code-lineage.** It "runs directly on Anthropic's Agents
  SDK" and drives Claude models through Claude Code's toolset, so its hook engine
  *is* the Claude Agent SDK hook engine. Inherits the failure model in
  [`../claude/descriptor.md`](../claude/descriptor.md). (The "claw" family name
  signals the lineage; here it is confirmed by the SDK dependency, not just the
  name.)

## 2. Hook engine
- **Events**: the Claude Agent SDK set — `PreToolUse`, `PostToolUse`,
  `UserPromptSubmit`, `Stop`, `SubagentStop`, `PreCompact`, `Notification`,
  `SessionStart`, `SessionEnd`.
- **Blocking-capable events**: `PreToolUse` (and `UserPromptSubmit`, `Stop`). In
  the SDK a hook is a Python callable registered via a `HookMatcher` in
  `ClaudeAgentOptions`; it denies by returning `hookSpecificOutput` with
  `permissionDecision: "deny"` (deny beats ask beats allow). A `can_use_tool`
  permission callback is the parallel gate path.
- **Failure mode**: **fails open**, per the Claude lineage — a hook that errors or
  fails to resolve a decision falls through to allow. **The gate must be
  fail-closed by construction**: deny by default, allow only on an explicit
  confirmed pass.

## 3. Config
- NanoClaw deliberately **avoids config files** ("to make changes, tell Claude
  Code what you want"); hooks are wired in code through `ClaudeAgentOptions`, not a
  `settings.json`. The repo does carry a `.claude/` directory and an `.mcp.json`
  (MCP server registration, JSON).
- Because the gate lives in Python, it is registered in the fork's agent setup
  rather than an external settings file — keep that code path stable and audited.

## 4. Transcript pointer
- NanoClaw persists per-session state in **SQLite** (`inbound.db` / `outbound.db`),
  not the Claude Code `~/.claude/projects/**.jsonl` tree. The exact schema/path is
  not documented; treat the read format as **inferred** and confirm on disk. ctx
  is the read-side authority once the DB is located.

## 5. Capabilities and caveats
- Full observe + gate via the SDK hook set, but wired programmatically — there is
  no drop-in `settings.json` hook the way canonical Claude Code offers, so a gate
  integrates by editing the fork's agent options.
- Runs agents in containers and injects credentials at request time via OneCLI's
  "Agent Vault" (per-agent policy + rate limits) — a separate credential boundary
  from the hook gate, not a substitute for it.
- Self-modifying by design (Claude Code can rewrite the fork), so pin and audit the
  agent-setup code that carries the gate.
