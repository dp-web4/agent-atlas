---
harness: Hermes Agent
ctx_provider: hermes
vendor: Nous Research
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [pre_tool_call]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.hermes/config.yaml
config_format: yaml
resource_type: [local, api]
fidelity: documented
sources:
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks
  - https://hermes-agent.nousresearch.com/docs/reference/cli-commands
  - https://hermes-agent.nousresearch.com/docs/user-guide/configuration/
  - https://github.com/nousresearch/hermes-agent
---

# Talk-to: Hermes Agent

**Fidelity: documented** - built from Nous Research's official Hermes Agent
docs (hooks, CLI, configuration) and the `NousResearch/hermes-agent` repo. Not
exercised against a live gate here.

## 1. Identity
- **Harness**: Hermes Agent (Nous Research) - a CLI + gateway coding agent
  ("the agent that grows with you"). Disambiguate from Hermes the HTTP/message
  frameworks and from the Nous "Hermes" model line; this is the agent harness.
- **ctx provider (read)**: `hermes`.
- **Lineage**: independent. Hermes ships its own three-tier hook architecture
  with its own event names. It does borrow Claude-Code's *shell-hook decision
  convention* (`{"decision":"block","reason":...}` is accepted alongside its
  native `{"action":"block","message":...}`), but the engine, event set, and
  failure model are its own - it is not a Claude-Code hook-engine clone.

## 2. Hook engine
- **Three hook systems**: (1) **Plugin hooks** registered in-process via
  `ctx.register_hook()` (~18 events: `pre_tool_call`, `post_tool_call`,
  `pre_llm_call`, `post_llm_call`, `pre_verify`, `on_session_start`,
  `on_session_end`, `subagent_start`/`subagent_stop`, `pre_approval_request`,
  transform hooks, etc.); (2) **Shell hooks** declared in `hooks:` in
  `~/.hermes/config.yaml` and run as subprocesses; (3) **Gateway hooks**
  (`~/.hermes/hooks/<name>/` with `HOOK.yaml` + handler) on events like
  `session:start`, `agent:step`, `command:*`.
- **Blocking-capable event**: only `pre_tool_call`. A plugin hook returns
  `{"action":"block","message":"..."}`; a shell hook returns that or the
  Claude-Code-style `{"decision":"block","reason":"..."}`. Everything else
  (post/transform/session events) is observational or mutational, not a gate.
- **Failure mode**: **the engine FAILS OPEN.** Docs state all three hook
  systems are non-blocking - timeouts, malformed JSON, non-zero exits, and
  thrown exceptions are caught and logged and the agent continues. A shell hook
  default timeout is 60s (max 300s). **Consequence: any gate wired on Hermes
  must be the fail-closed party itself** - emit an explicit block decision on
  the happy path only, and never rely on an errored hook to deny for you.
- **Consent gate**: each unique `(event, command)` shell hook prompts for
  approval on first use, persisted to `~/.hermes/shell-hooks-allowlist.json`.

## 3. Config
- **Path**: `~/.hermes/config.yaml` (shell hooks live in its `hooks:` block).
- **Format**: YAML. Plugin hooks load from `~/.hermes/plugins/<name>/`; gateway
  hooks from `~/.hermes/hooks/<name>/`; shell allowlist is the JSON file above.
- **Knobs that matter**: shell-hook `matcher` (regex), `timeout`, and
  `hooks_auto_accept`; inspect/test with the `hermes hooks` command.

## 4. Transcript pointer
- **Path pattern**: not authoritatively documented. Logs live under
  `~/.hermes/logs/` (an `orchestration.log` is referenced by convention), and a
  hook handler writes its own `activity.log`. Treat the exact per-session
  transcript path as **unknown**; ctx is the read-side authority and may need to
  reverse-engineer the session store.

## 5. Capabilities and caveats
- Observe cheaply by wiring non-blocking events (`post_tool_call`,
  `on_session_start`/`on_session_end`); gate by wiring `pre_tool_call`.
- The fail-open architecture is explicit and by design ("availability over
  strictness"), so a security gate cannot delegate deny-on-error to Hermes.

## Sources
- Event Hooks - https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks
- CLI Commands Reference - https://hermes-agent.nousresearch.com/docs/reference/cli-commands
- Configuration - https://hermes-agent.nousresearch.com/docs/user-guide/configuration/
- NousResearch/hermes-agent - https://github.com/nousresearch/hermes-agent
