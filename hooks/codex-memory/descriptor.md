---
provider: codex-memory
kind: hook-provider
vendor: dp-web4/shared-context (codex-memory)
match: paths
match_paths: [*/codex-memory/hook.mjs]
harnesses: [codex]
gate_events: []
observe_events: [SessionStart, UserPromptSubmit, PostToolUse, PreCompact, Stop, SessionEnd]
can_block: false
fidelity: documented
sources:
  - https://github.com/dp-web4/shared-context/tree/main/codex-memory
---

# codex-memory

A memory service for Codex sessions. One entry point (`hook.mjs`) is registered on several
events. No deny path or permission decision was found in its source on 2026-09-28, so it
observes only. It was not exercised, so fidelity is `documented`.
