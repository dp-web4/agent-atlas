---
provider: claude-flow
kind: hook-provider
vendor: ruvnet/claude-flow
match: paths
match_paths: [*claude-flow*, */hook-handler.cjs, */auto-memory-hook.mjs, *ruv-swarm*]
harnesses: [claude]
gate_events: unknown
observe_events: unknown
can_block: unknown
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
lists and `can_block` are `unknown` rather than guessed. (An earlier draft wrote `false` and
`[]` here, and a consumer read those as an assessment.)
