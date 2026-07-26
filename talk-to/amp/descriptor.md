---
harness: Amp
ctx_provider: none
vendor: Amp Inc. (formerly Sourcegraph; ampcode.com)
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [tool.call]
fails_open: unknown
subagent_hooks_inherited: untested
config_path: ~/.config/amp/settings.json
config_format: json
fidelity: documented
sources:
  - https://ampcode.com/manual
  - https://ampcode.com/manual/plugin-api
  - https://ampcode.com/news/tool-level-permissions
---

# Talk-to: Amp

**Fidelity: documented** - from Amp's official Owner's Manual and Plugin API reference; Amp is not yet in ctx's read registry, so this talk-to note leads the read side.

## 1. Identity   (note: not yet in ctx read registry — talk-to leads read here)
- **Harness**: Amp, an agentic coding tool (CLI + editor extension) at ampcode.com. Grew out of Sourcegraph; spun out as Amp Inc. (Quinn Slack, Beyang Liu) in late 2025, distinct from the now Enterprise-only Cody.
- **ctx provider (read)**: none. Use `amp` as the natural id; `ctx_provider: none`.
- **Lineage**: independent. Amp has its OWN plugin/hook engine with its own event names and return-value protocol — it is not a Claude-Code clone. Do not inherit the Claude failure model blindly; verify against Amp's own semantics.

## 2. Hook engine
- **Events** (plugin lifecycle hooks): `session.start`, `agent.start` (user submits a prompt), `tool.call` (before a tool runs), `tool.result` (after a tool, before the result returns to the model), `agent.end`.
- **Blocking-capable event**: `tool.call`. A handler returns an action object: `allow` (run as-is), `modify` (rewrite the tool input), `synthesize` (return a fabricated result, skip the tool), `reject-and-continue` (deny this call, let the agent proceed with others), or `error` (stop the thread worker with an ephemeral error). So blocking is **explicit-return**: to deny, a hook must actively return `reject-and-continue` (or `error`); the default `allow` runs the tool.
- **Failure mode**: **not documented, treat as fails-open.** The Plugin API spec defines the normal return values but does not state what happens when a hook crashes, times out, or fails to spawn. The design is default-allow (block only on an explicit reject return), and the manual notes HTTP-hook connection/timeout errors are non-blocking (execution continues) — both point to fail-open in practice. **Because the failure mode is unconfirmed and the design defaults to allow, the gate itself must be fail-closed by construction**: deny unless the hook returns a confirmed, explicit allow, and prefer command hooks (which can signal a blocking error) over HTTP hooks (whose failures are non-blocking).

## 3. Config
- **Path**: user settings `~/.config/amp/settings.json` (or `.jsonc`); workspace `.amp/settings.json` (searched upward from cwd); enterprise managed settings under an OS-managed path. Plugins live in `.amp/plugins/` (project) or `~/.config/amp/plugins/`.
- **Format**: JSON / JSONC; all keys use the `amp.` prefix (e.g. `amp.mcpServers`, `amp.mcpPermissions`, `amp.hooks`).
- **Knobs that matter**: MCP servers in workspace settings require explicit approval before running; `amp.mcpPermissions` pattern-matches allowed command/args/url. Legacy Toolboxes (`AMP_TOOLBOX` / `.amp/toolbox/`) are no longer supported — migrate to plugins.

## 4. Transcript pointer
- **Local path: not documented.** Amp organizes work as "threads" surfaced/shared via ampcode.com (the web feed); the manual does not specify an on-disk transcript file or location. A reader may need to pull threads via Amp's own surface rather than tail a local JSONL. ctx does not yet cover this harness's read side.

## 5. Capabilities and caveats
- **Observe**: wire the non-blocking events (`session.start` / `tool.result` / `agent.end`) to witness activity without risk.
- **Gate**: `tool.call` is a genuine pre-execution seam that can deny (`reject-and-continue`) or rewrite (`modify`) a call — richer than a plain allow/deny. But the undocumented error/timeout behavior means the gate must default-deny itself.
- **Caveat**: local transcript storage is unknown, so the read side may not be a simple file tail. Confirm the actual on-disk artifact before building a witness against it.
