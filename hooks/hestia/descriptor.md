---
provider: hestia
kind: hook-provider
vendor: dp-web4/hestia
match: provenance
harnesses: [claude, codex, gemini, kimi_code_cli]
gate_events: [PreToolUse, BeforeTool]
observe_events: [SessionStart, UserPromptSubmit, PostToolUse, PostToolUseFailure, AfterTool, SessionEnd, Stop]
can_block: true
fidelity: verified
sources:
  - https://github.com/dp-web4/hestia/tree/main/plugins
  - https://github.com/dp-web4/hestia/blob/main/plugins/agent-inventory/inventory.py
---

# hestia

The local governance layer. Its gates (`pre_tool_use.py` for Claude Code, Codex and Kimi;
`before_tool.py` for Gemini) evaluate each action against the machine's law and can deny it.
Its witness and observe hooks record outcomes. Its member-mesh hooks deliver notices at
SessionStart.

**Identified by provenance, not by path.** A hook is hestia's when one of these holds:
- its path is one a hestia plugin's `expects.json` declares installing (`install.dest` + `files`);
- its path is in the deploy record (`$HESTIA_HOME/current-build.json`);
- it lies inside hestia's own `plugins/` tree;
- its bytes are identical to a file hestia ships under `plugins/`.

The per-harness role of each hestia hook (gate vs observe) comes from that plugin's
`expects.json`. The event lists above are the union of those declarations.
