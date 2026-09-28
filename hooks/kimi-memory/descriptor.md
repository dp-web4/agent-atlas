---
provider: kimi-memory
kind: hook-provider
vendor: dp-web4/shared-context (kimi-memory)
match: paths
match_paths: [*/kimi-memory/hooks/*]
harnesses: [kimi_code_cli]
gate_events: []
observe_events: [SessionStart, PostToolUse, PostToolUseFailure, SessionEnd]
can_block: false
fidelity: documented
sources:
  - https://github.com/dp-web4/shared-context/tree/main/kimi-memory/hooks
---

# kimi-memory

A memory service for Kimi Code sessions. No deny path or permission decision was found in its
hooks' source on 2026-09-28 (`session-start.js`, `post-tool-use.js`, `session-end.js`), so it
observes only. It was not exercised, so fidelity is `documented`.
