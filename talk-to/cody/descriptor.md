---
harness: Cody
ctx_provider: none
vendor: Sourcegraph
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: n/a
subagent_hooks_inherited: untested
config_path: VS Code settings.json (cody.* keys)
config_format: json
fidelity: documented
sources:
  - https://sourcegraph.com/docs/cody/capabilities/autocomplete
  - https://sourcegraph.com/docs/cody/capabilities/openctx
  - https://sourcegraph.com/docs/cody/capabilities/agentic-context-fetching
  - https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans
---

# Talk-to: Cody

**Fidelity: documented** - from Sourcegraph's official Cody docs; Cody is not yet in ctx's read registry, so this talk-to note leads the read side.

## 1. Identity   (note: not yet in ctx read registry — talk-to leads read here)
- **Harness**: Cody, Sourcegraph's AI code assistant — inline autocomplete, chat, and "agentic chat" context fetching, embedded as an IDE extension (VS Code, JetBrains, etc.). Now an Enterprise-only product; Sourcegraph closed Cody Free/Pro in mid-2025 and steers individual users to Amp.
- **ctx provider (read)**: none. Use `cody` as the natural id; `ctx_provider: none`.
- **Lineage**: independent. Cody is an editor-embedded assistant, not a hook-driven terminal harness.

## 2. Hook engine
- **No hook engine, no local gate seam.** Cody drives the editor through VS Code's `InlineCompletionItemProvider` / chat UI; it exposes no lifecycle event a third party can register a blocking command against, and no pre-action allow/deny gate for its edits or tool calls.
- Its extension points are **context injection, not gating**: OpenCtx providers (`openctx.providers`) and MCP servers add read-only context that Cody may pull in; "agentic context fetching" (`cody.agenticContext`) lets Cody decide what extra context to gather. None of these can veto an action — they widen what the model sees, they do not stop what it does.
- Consequence for an integrator: **gate OUTSIDE the harness.** Because Cody's actions land as editor mutations, enforcement lives in the editor's own confirm/apply step, in the surrounding OS/sandbox, or in review/CI on the resulting commits — not in a Cody hook.

## 3. Config
- **Path**: the host editor's settings — for VS Code, `settings.json` with `cody.*` keys (e.g. `cody.agenticContext`, `openctx.providers`, MCP server config). Enterprise policy is administered server-side by Sourcegraph.
- **Format**: JSON (editor settings).
- **Knobs that matter**: `openctx.providers` and MCP config expand context; `cody.agenticContext` toggles autonomous context fetching. These tune behavior but none of them block an action.

## 4. Transcript pointer
- **Local path: not documented.** Cody keeps chat history in the editor extension's own state rather than a documented on-disk JSONL/Markdown transcript; there is no vendor-specified session file to tail. ctx does not yet cover this harness's read side, and the read side here is not a simple file.

## 5. Capabilities and caveats
- **Observe**: limited — no documented local transcript artifact; server-side (Enterprise) admin/audit surfaces are the realistic record.
- **Gate**: none in-harness. Cody is autocomplete/chat/agentic-context, not a gate-able tool runner; treat it as ungated at the harness layer.
- **Caveat**: Cody is Enterprise-only now and overlaps in vendor heritage with Amp — do not conflate the two; Amp has a real plugin/hook engine, Cody does not.
