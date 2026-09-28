---
provider: web4-governance
kind: hook-provider
vendor: dp-web4/claude-code (plugins/web4-governance)
match: paths
match_paths: [*/plugins/web4-governance/hooks/*]
harnesses: [claude]
gate_events: [PreToolUse]
observe_events: [SessionStart, PostToolUse]
can_block: true
fidelity: documented
sources:
  - https://github.com/dp-web4/claude-code/tree/main/plugins/web4-governance/hooks
---

# web4-governance (Claude Code plugin)

A Claude Code plugin with its own policy evaluation. Its `pre_tool_use.py` returns a deny
verdict (`verdict.kind == "deny"`), so **it is a gate that is not hestia's**. A machine that
wires it on PreToolUse has two gates, and an inventory should say so. Its SessionStart and
PostToolUse hooks (`session_start.py`, `plugin_relevance.py`, `post_tool_use.py`) observe.

The deny path was read from source on 2026-09-28, but not exercised, so fidelity is
`documented`. On CBP that day only its SessionStart and PostToolUse hooks were registered.
