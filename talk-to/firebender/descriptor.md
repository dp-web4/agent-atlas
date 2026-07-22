---
harness: Firebender
ctx_provider: firebender
vendor: Firebender, Inc.
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: unknown
config_path: firebender.json (project root); .firebender/rules/*.mdc
config_format: json (rules: markdown/mdc with YAML frontmatter)
fidelity: documented
sources:
  - https://docs.firebender.com/multi-agent/global-rules
  - https://plugins.jetbrains.com/plugin/25224-firebender
  - https://firebender.com/
---

# Talk-to: Firebender

**Fidelity: documented** - built from Firebender's official docs and its JetBrains
Marketplace listing; no programmable hook/gate surface exists to exercise.

## 1. Identity
- **Harness**: Firebender - an AI coding agent that ships as a JetBrains
  IDE plugin (IntelliJ family / Android Studio), per its
  [Marketplace listing](https://plugins.jetbrains.com/plugin/25224-firebender).
  It runs inside the IDE, not as a standalone local CLI.
- **ctx provider (read)**: `firebender`.
- **Lineage**: independent. Not a Claude-Code hook-engine clone; it has no
  shell-hook engine at all.

## 2. Hook engine
- **None.** The documentation describes autocomplete, chat, and inline AI edits
  driven by a deterministic config file plus prose rules. There are no lifecycle
  events, no `PreToolUse`-style gate, and no exit-code/decision contract a third
  party could wire a tool into.
- The closest thing to access control is a file **ignore** mechanism: ignored
  files are excluded from chat context and autocomplete suggestions. This shapes
  what the model *sees*; it does not gate what an agent *does*, and per the docs
  it does **not** restrict terminal or MCP tools. So it is not a blocking gate in
  the sense this registry means.
- **blocking_capable: false.** There is no way to intercept and deny a tool call.

## 3. Config
- **Path**: `firebender.json` at the project root (deterministic config surface);
  rules live in `.firebender/rules/*.mdc` (project) and `~/.firebender/rules/*.mdc`
  (personal, cross-project).
- **Format**: JSON for `firebender.json`; Markdown-with-YAML-frontmatter (`.mdc`)
  for rules. Rules support `alwaysApply` and `.gitignore`-style `globs`, and
  hot-reload on save.
- **Knobs that matter**: rules are advisory context, not enforcement. Nothing here
  can hard-stop an action.

## 4. Transcript pointer
- **Unknown.** No official session-transcript/log path is documented, and as an
  in-IDE plugin its conversation state is not exposed as a local JSONL/session tree
  the way CLI harnesses expose one. The ctx read side is the authority here; treat
  the transcript location as undiscovered until confirmed against a live install.

## 5. Capabilities and caveats
- Observe-and-gate is **not** available: no event stream to witness and no pre-tool
  gate to deny. Firebender is a context/rules-shaping surface, not a
  hookable engine.
- Recorded absence is the finding: any "talk-to" integration would have to operate
  outside Firebender (e.g. at the OS/filesystem layer), because the harness offers
  no in-band extension point for blocking.

## Sources
- Rules / config / ignore behavior - https://docs.firebender.com/multi-agent/global-rules
- JetBrains plugin identity (IDE-only) - https://plugins.jetbrains.com/plugin/25224-firebender
- Product overview - https://firebender.com/
