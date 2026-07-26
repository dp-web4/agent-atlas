---
harness: Kilo Code
ctx_provider: kilo
vendor: Kilo (Kilo-Org)
lineage: opencode
hook_engine: true
blocking_capable: true
blocking_events: [tool.execute.before, permission.ask]
fails_open: unknown
subagent_hooks_inherited: untested
config_path: ~/.config/kilo/kilo.jsonc (project kilo.jsonc / .kilo/kilo.jsonc)
config_format: jsonc
fidelity: documented
sources:
  - https://kilo.ai/docs/automate/extending/plugins
  - https://kilo.ai/docs/getting-started/settings
  - https://github.com/Kilo-Org/kilocode/issues/5827
  - https://kilo.ai/cli
---

# Talk-to: Kilo Code

**Fidelity: documented** - from Kilo's official plugin and settings docs; not
exercised live by this registry.

## 1. Identity
- **Harness**: Kilo Code ([Kilo-Org/kilocode](https://github.com/Kilo-Org/kilocode)),
  an open-source agentic coding platform shipping as a VS Code / JetBrains
  extension, a `@kilocode/cli` terminal agent, and cloud.
- **ctx provider (read)**: `kilo`.
- **Lineage**: **OpenCode.** Kilo began as a fork of **Cline + Roo Code**, then
  rebuilt on OpenCode's portable server shared by CLI, VS Code, and cloud. Its
  plugin/hook surface is OpenCode's TypeScript hook interface
  (`tool.execute.before`, `tool.execute.after`, `chat.message`, `permission.ask`,
  …) — **not** the Claude-Code `exit 2` shell-hook model. It blocks by throwing
  in-process, not via exit codes.

## 2. Hook engine
- **Model**: a **plugin system** — TypeScript/JavaScript modules loaded at
  startup that default-export a descriptor (`id` + async `server` function
  returning a hooks object). Plugins work in **both the Kilo CLI and the VS Code
  extension**.
- **Events**: 15+ lifecycle hooks including `config`, `event`, `tool`,
  `tool.execute.before`, `tool.execute.after`, `tool.definition`, `chat.message`,
  `chat.params`, `permission.ask`, `command.execute.before`, `shell.env`, `auth`,
  `provider`, plus experimental transform/compaction hooks.
- **Blocking-capable**: yes — **`tool.execute.before` blocks a tool by throwing
  an error** (docs' example throws to block reading `.env` files); `permission.ask`
  participates in the approval decision. Blocking is exception-based, not an exit
  code or decision-JSON.
- **Failure mode**: **unknown / undocumented.** Kilo's docs describe throwing to
  block but never state what happens if a *non-blocking* hook throws or a plugin
  fails to load beyond "load failures are surfaced as session errors." Because
  blocking is a thrown exception inside the agent loop, a gate hook that crashes
  before it throws its deny could let the tool through. **Treat as fail-open until
  confirmed**: throw to deny explicitly; never rely on an unrelated error to stop
  a tool.

## 3. Config
- **Path**: global `~/.config/kilo/kilo.jsonc`; project `kilo.jsonc` or
  `.kilo/kilo.jsonc`. Plugins are registered as config arrays (npm packages or
  local file paths), auto-discovered in `plugin/`/`plugins/` dirs, or added via
  `kilo plugin <name>`.
- **Format**: JSONC. In the VS Code extension the same settings are editable via
  the Settings UI (Agent Behaviour → MCP Servers, etc.).
- **Note**: a separate request to expose standalone session lifecycle hooks in
  `.kilo/config.json` ([issue #5827](https://github.com/Kilo-Org/kilocode/issues/5827))
  was **closed as not planned** — the sanctioned extension point is the plugin
  system above, so that "no hooks" read is outdated.

## 4. Transcript pointer
- **Path**: **not documented** in the sources reviewed. Kilo runs on OpenCode's
  server, which persists session state, but the on-disk transcript path/format is
  not stated in official docs here. ctx is the read-side authority; a plugin
  wiring `chat.message`/`tool.execute.after` is the reliable observe path.

## 5. Capabilities and caveats
- Observe + gate both available through one plugin (witness on
  `tool.execute.after`/`chat.message`, block on `tool.execute.before`), and the
  same plugin runs in CLI and VS Code — a real advantage over UI-only approval.
- Cost: the gate is a TS/JS plugin, not a shell script, and its fail-open/closed
  behavior is unverified — the load-bearing unknown to pin down before trusting it.
