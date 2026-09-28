---
provider: snarc
kind: hook-provider
vendor: dp-web4/snarc
match: paths
match_paths: [*/snarc/dist/hooks/handlers/*]
harnesses: [claude]
gate_events: []
observe_events: [SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, PostCompact, Stop]
can_block: false
fidelity: verified
sources:
  - https://github.com/dp-web4/snarc/tree/main/hooks/handlers
---

# snarc

Salience-gated memory for Claude Code sessions. Every handler reads the event and the
transcript, records context into snarc's own store, and exits 0. There is no deny path and
no permission decision.

This was verified from source on 2026-09-28 at `c296cc8` (`hooks/handlers/*.ts`). The
PreToolUse handler in particular captures the reasoning text written since the last tool
call, and exits 0 on every path, including when the text is trivial. Its registration on
PreToolUse makes it look like a gate, but it is not one.
