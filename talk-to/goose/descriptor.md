---
harness: Goose
ctx_provider: goose
vendor: Block (Square)
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: n/a
subagent_hooks_inherited: untested
config_path: ~/.config/goose/config.yaml (+ permission.yaml)
config_format: yaml
resource_type: [local, api]
fidelity: documented
sources:
  - https://goose-docs.ai/docs/guides/config-files/
  - https://deepwiki.com/block/goose/6.2-permission-modes-and-tool-approval
  - https://github.com/block/goose/issues/4097
  - https://mintlify.wiki/block/goose/api/cli/session
---

# Talk-to: Goose

**Fidelity: documented** - based on Goose's official config-files and permission-mode docs. Goose gates tools with an **internal permission model**, not an external hook/script seam; that absence is the finding.

## 1. Identity
- **Harness**: [Goose](https://github.com/block/goose), Block (Square)'s open-source on-machine AI agent (CLI + desktop).
- **ctx provider (read)**: `goose`.
- **Lineage**: **independent.** Goose is a Rust agent with its own architecture; extensions are **MCP servers**, not a Claude-style hook engine.

## 2. Hook engine
- **No external hook/lifecycle engine.** Goose does not expose PreToolUse/PostToolUse-style events that run a user script to allow/deny a call. Gating is done by an **internal permission model** driven by `GOOSE_MODE`:
  - `auto` — run all tool calls without approval;
  - `approve` — consult `permission.yaml` per call (AlwaysAllow / AskBefore / NeverAllow), prompting the human otherwise;
  - `smart_approve` — an LLM-based `PermissionJudge` classifier decides whether a call is safe to auto-run;
  - `chat` — blocks all tool usage.
- **Blocking-capable**: `false` for this registry's purposes — a call *can* be denied, but only by the built-in modes / `permission.yaml` / a human, not by an external gate process wired into the loop. There is no fail-open/closed hook question because there is no hook seam. (Extensions are MCP servers that *add* tools, not intercept them.)

## 3. Config
- **Path**: `~/.config/goose/config.yaml` (provider, model, extensions, `GOOSE_MODE`); `~/.config/goose/permission.yaml` (per-tool levels via `goose configure`); `~/.config/goose/secrets.yaml`; auto-managed `permissions/tool_permissions.json`. Recipes under `{config_dir}/recipes/` and project `.goose/recipes/`.
- **Format**: YAML. `GOOSE_MODE` can also be set as an environment variable (env overrides file); changes require restarting goose.

## 4. Transcript pointer
- **Path pattern**: session transcripts are JSONL under `~/.local/share/goose/sessions/` (one JSONL per session, full conversation + tool history). This is the read side's input.

## 5. Capabilities and caveats
- **No programmatic intercept seam.** External supervision options are: choose `approve`/`chat` mode so nothing runs unattended, curate `permission.yaml` (NeverAllow the risky tools), or read the `sessions/*.jsonl` transcripts after the fact.
- `smart_approve` delegates the allow/deny decision to an LLM classifier — convenient but non-deterministic; do not treat it as a hard gate. For a fail-closed posture prefer explicit `permission.yaml` NeverAllow/AskBefore entries over trusting the judge.
