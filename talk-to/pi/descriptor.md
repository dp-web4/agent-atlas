---
harness: Pi
ctx_provider: pi
vendor: Earendil Works (Mario Zechner / "badlogic")
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [tool_call (permission gate)]
fails_open: unknown
config_path: ~/.pi/agent/settings.json (project .pi/settings.json)
config_format: json
fidelity: documented
sources:
  - https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md
  - https://github.com/earendil-works/pi
  - https://www.npmjs.com/package/@mariozechner/pi-coding-agent
---

# Talk-to: Pi

**Fidelity: documented** - taken from the official `earendil-works/pi`
(mirror `badlogic/pi-mono`) coding-agent README and package docs; not exercised
live by this registry.

## 1. Identity
- **Harness**: Pi coding agent CLI — a minimalist, provider-agnostic BYOK
  terminal agent ([earendil-works/pi](https://github.com/earendil-works/pi),
  npm `@earendil-works/pi-coding-agent` / `@mariozechner/pi-coding-agent`),
  authored by Mario Zechner ("badlogic"). Four built-in tools: read, write,
  edit, bash; everything else is an extension.
- **ctx provider (read)**: `pi`.
- **Disambiguation**: "Pi" is an overloaded name. This descriptor is the
  earendil-works/badlogic TypeScript CLI. It is **not** `davidondrej/pi-agent`
  (a separate agent toolkit that happens to share the name), and not Inflection's
  consumer "Pi" chatbot. Verified via the repo's package name and four-tool design.
- **Lineage**: **independent.** Pi does not clone Claude Code's shell-hook
  engine; gating is programmatic through a TypeScript extension API, not
  `exit 2` shell hooks.

## 2. Hook engine
- **Model**: an in-process **TypeScript extension API**, not external shell
  hooks. A default-exported function receives an `ExtensionAPI` and can register
  tools, commands, keybindings, UI, and event handlers such as
  `pi.on("tool_call", async (event, ctx) => { ... })`.
- **Blocking-capable**: yes — extensions can register **permission gates and
  path protection** around tool execution (e.g. block writes/reads to protected
  paths), and custom confirmation flows. Runtime allow-listing is also available
  via CLI flags `--tools`, `--exclude-tools`, `--no-builtin-tools`.
- **Failure mode**: **unknown / undocumented.** The docs describe gates but do
  not state what happens if a gate handler throws or hangs. Because the gate is
  ordinary in-process TS, an unhandled throw could resolve either way depending
  on the loop's try/catch. **Treat it as fail-open until confirmed**: a gate
  should deny explicitly and never depend on an exception to stop a tool.

## 3. Config
- **Path**: global `~/.pi/agent/settings.json`; project `.pi/settings.json`
  overrides it. Trust decisions in `~/.pi/agent/trust.json`.
- **Format**: JSON.
- **Extensions load from**: `~/.pi/agent/extensions/`, project `.pi/extensions/`,
  or pi packages. This is where a gate/witness extension would live.

## 4. Transcript pointer
- **Path pattern**: `~/.pi/agent/sessions/`, auto-saved **JSONL**, organized by
  working directory. Sessions are stored as a **tree** (each record carries `id`
  and `parentId`) to support branching/navigation — a reader must respect the
  parent-pointer structure, not assume a linear log.

## 5. Capabilities and caveats
- Full observe + gate is possible **in-process** (register a `tool_call` handler
  to witness, a permission gate to block) — but it means shipping a TS extension,
  not dropping a shell script in a config.
- The context-frugal design (small system prompt, tools loaded on demand, no
  hidden context injection) means less ambient state to lean on; a gate must read
  what it needs explicitly.
- Fail-open/closed is the one load-bearing unknown here; confirm it against a
  live install before trusting a gate.
