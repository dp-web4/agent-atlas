---
harness: AstrBot
ctx_provider: astrbot
vendor: AstrBotDevs
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [on_llm_request, on_using_llm_tool, on_decorating_result, event_message_type, command]
fails_open: unknown
subagent_hooks_inherited: untested
config_path: data/cmd_config.json (core); per-plugin _conf_schema.json + metadata.yaml
config_format: json / yaml
resource_type: [local, api]
fidelity: documented
sources:
  - https://docs.astrbot.app/en/dev/star/guides/listen-message-event.html
  - https://docs.astrbot.app/en/dev/star/plugin.html
  - https://github.com/AstrBotDevs/AstrBot
---

# Talk-to: AstrBot

**Fidelity: documented** - AstrBot's official developer docs describe the Star
plugin decorators, the lifecycle hooks, and `event.stop_event()`. The failure
mode (what happens when a handler raises) is not documented, so it is marked
unknown.

## 1. Identity
- **Harness**: AstrBot (`AstrBotDevs/AstrBot`), a multi-platform LLM chatbot /
  agent framework (QQ, Telegram, Discord, WeChat, etc.) with a Python plugin
  system and a web dashboard. It is a chat-agent framework, not a terminal coding
  CLI.
- **ctx provider (read)**: `astrbot`.
- **Lineage**: **independent.** Its extension model is the "Star" plugin
  abstraction with `@filter.*` decorators and an async `EventBus` pipeline — no
  relation to Claude Code's `PreToolUse` exit-code hook engine.

## 2. Hook engine
- **Events / decorators**: message filters — `@filter.command`,
  `@filter.command_group`, `@filter.event_message_type`,
  `@filter.platform_adapter_type`, `@filter.permission_type` (admin gate); and
  lifecycle hooks — `on_astrbot_loaded`, `on_waiting_llm_request`,
  `on_llm_request`, `on_llm_response`, `on_agent_begin`, `on_using_llm_tool`,
  `on_llm_tool_respond`, `on_agent_done`, `on_decorating_result`,
  `after_message_sent`. Plugins also register agent tools via `@filter.llm_tool`.
- **Blocking-capable**: a handler calls `event.stop_event()` to halt the pipeline
  — "all subsequent steps will not be executed," including other plugins and the
  LLM request. Handlers run in `priority` order (higher first), so a high-priority
  handler can veto before the model or a tool runs (`on_llm_request` blocks the
  model call; `on_using_llm_tool` runs before tool execution). `permission_type`
  gates handlers to admins. This is a real gate, but it operates at the
  **message / LLM-turn** granularity of a chat pipeline, not a per-shell-command
  tool gate.
- **Failure mode**: **unknown.** The docs do not state whether an exception in a
  handler aborts the pipeline or is swallowed and processing continues. Do not
  assume — a gate built here must call `stop_event()` explicitly on its deny path
  and must not rely on raising to block. Treat as fail-open until verified.

## 3. Config
- **Core config**: merged from `DEFAULT_CONFIG`, `cmd_config.json`, and env vars
  (config DB / `data/` at runtime, e.g. `data/cmd_config.json`).
- **Per-plugin config**: a plugin declares a `_conf_schema.json` schema and ships
  a `metadata.yaml`; user values are persisted by the dashboard. Format is JSON
  for schema/values, YAML for plugin metadata.

## 4. Transcript pointer
- Conversation history is stored in a **SQLite** database (`data/data_v4.db`).
  There is no per-session JSONL transcript; the read side would query the DB.
  ctx is the read-side authority once the schema is mapped (treat exact table
  layout as to-be-confirmed).

## 5. Capabilities and caveats
- Observe with the post-hooks (`on_llm_response`, `on_llm_tool_respond`,
  `after_message_sent`); gate with the pre-hooks (`on_llm_request`,
  `on_using_llm_tool`) plus `stop_event()` and `permission_type`.
- **Biggest caveat**: fail-open/closed is undocumented — a security gate must
  enforce denial explicitly via `stop_event()`, never by throwing, until the
  exception path is verified against a real build.
- Granularity is chat-turn / LLM-call level, so this is a good witness+policy
  surface for a conversational agent but not a substitute for OS-level command
  sandboxing.
