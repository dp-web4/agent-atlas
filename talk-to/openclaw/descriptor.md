---
harness: OpenClaw
ctx_provider: openclaw
vendor: OpenClaw project (Peter Steinberger); built on Anthropic's Claude Agent SDK
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [before_tool_call, before_install]
fails_open: unknown
subagent_hooks_inherited: untested
config_path: ~/.openclaw/openclaw.json
config_format: json5
fidelity: documented
sources:
  - https://docs.openclaw.ai/plugins/hooks
  - https://docs.openclaw.ai/automation/hooks
  - https://docs.openclaw.ai/gateway/configuration-reference
  - https://milvus.io/blog/openclaw-formerly-clawdbot-moltbot-explained-a-complete-guide-to-the-autonomous-ai-agent.md
---

# Talk-to: OpenClaw

**Fidelity: documented** - built from the official `docs.openclaw.ai` hook,
automation, and configuration references, cross-checked against project
overviews. Not exercised against a live gate here.

## 1. Identity
- **Harness**: OpenClaw - an open-source, persistent AI-agent **gateway/daemon**
  (multi-channel: Slack/Discord/Telegram/Matrix/etc.) created by Peter
  Steinberger, originally released as **Clawdbot / Moltbot** (late 2025). It is
  model-agnostic and builds on Anthropic's Claude Agent SDK, but it is its own
  runtime, not a coding-CLI. Disambiguate hard from **OpenClaw the game engine**
  (the Captain Claw reimplementation), an unrelated project.
- **ctx provider (read)**: `openclaw`.
- **Lineage**: **independent.** The "claw" in the name does *not* signal
  Claude-Code lineage here - OpenClaw has its own ~40-event typed plugin-hook
  system with its own names and its own (mixed) failure semantics. It is not the
  Claude-Code hook engine and should not inherit that descriptor.

## 2. Hook engine
- **Two surfaces**: (1) **Internal hooks / webhooks** (operator side-effects on
  event keys like `command:new`, `session:compact:before`, `message:received`,
  `gateway:startup`) - these **cannot block**; and (2) **typed plugin hooks**
  (~40 events across agent-turn, tools, messages, sessions, subagents,
  lifecycle) which have explicit contracts, priorities, and block/cancel
  semantics.
- **Blocking-capable events**: `before_tool_call` is the tool gate - a plugin
  handler returns `{ block: true, blockReason, params?, requireApproval? }`
  (it can also rewrite params or pause for `/approve`). Decision hooks such as
  `before_install` can likewise refuse an action.
- **Failure mode**: **MIXED - marked `unknown` deliberately.** Docs distinguish
  *observation* hooks (failures logged, delivery result unchanged = fail open)
  from *decision* hooks (e.g. `before_install`: "handler failures block the
  install fail-closed"). BUT the timeout rule is fail-open even for decisions:
  when a handler's timeout expires OpenClaw "stops awaiting that handler and
  moves on" (the tool proceeds). So an errored `before_tool_call` may fail
  closed while a *slow* one fails open. **Do not assume OpenClaw denies for
  you - build any gate to be fail-closed and fast (well under the hook
  timeout).**

## 3. Config
- **Path**: `~/.openclaw/openclaw.json` (state dir overridable via
  `OPENCLAW_STATE_DIR`).
- **Format**: JSON5 (comments + trailing commas allowed). Plugins under
  `plugins.*` (`enabled`, `allow`/`deny`, `load.paths`, per-plugin `hooks`
  incl. `allowConversationAccess`); internal hooks under `hooks.*`; webhooks use
  `Authorization: Bearer <token>` or `x-openclaw-token`.
- **Knobs that matter**: `plugins.entries.<id>.hooks.allowConversationAccess`
  gates whether a non-bundled plugin can read raw conversation content.

## 4. Transcript pointer
- **Path pattern**: session transcripts and audit events live in OpenClaw's
  **shared state database** under the state dir (default `~/.openclaw`), not a
  per-session JSONL tree. Exact schema/table is not spelled out in the public
  config reference; treat the concrete read path as needing confirmation.

## 5. Capabilities and caveats
- Full observe + gate via typed plugin hooks; `before_tool_call` supports block,
  param-rewrite, and human-approval flows.
- The mixed error/timeout semantics are the trap: fail-closed-on-error but
  fail-open-on-timeout. A gate must decide fast and default to deny.
- Vendor note: some doc headers say "built on Anthropic's Claude Agent SDK" -
  that is a dependency, not authorship; the project ships as OpenClaw.

## Sources
- Plugin hooks - https://docs.openclaw.ai/plugins/hooks
- Automation hooks - https://docs.openclaw.ai/automation/hooks
- Configuration reference - https://docs.openclaw.ai/gateway/configuration-reference
- What Is OpenClaw (formerly Clawdbot/Moltbot) - https://milvus.io/blog/openclaw-formerly-clawdbot-moltbot-explained-a-complete-guide-to-the-autonomous-ai-agent.md
