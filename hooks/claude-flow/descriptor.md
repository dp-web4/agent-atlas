---
provider: claude-flow
kind: hook-provider
vendor: ruvnet/claude-flow
match: paths
match_paths: [*claude-flow*, */hook-handler.cjs, */auto-memory-hook.mjs, *ruv-swarm*]
harnesses: [claude]
gate_events: []
observe_events: []
can_block: false
fidelity: inferred
sources:
  - https://github.com/ruvnet/claude-flow
---

# claude-flow

An orchestration toolkit whose helper suite registers hooks in Claude Code (`hook-handler.cjs`,
`auto-memory-hook.mjs`) and ships companion MCP tooling (`ruv-swarm`). These patterns came from
hestia agent-inventory's `THIRD_PARTY_MARKERS`, which recognised it so that one of its
**dead** hooks is not mistaken for a dead hestia gate. The roles and blocking capability of its
hooks have not been read, so every field beyond `match_paths` is `inferred`, and the event
lists are left empty rather than guessed.
