---
harness: Rovo Dev CLI
ctx_provider: rovodev
vendor: Atlassian
lineage: independent
hook_engine: false
blocking_capable: true
blocking_events: [toolPermissions]
fails_open: false
subagent_hooks_inherited: untested
config_path: ~/.rovodev/config.yml
config_format: yaml
resource_type: [subscription]
fidelity: documented
sources:
  - https://support.atlassian.com/rovo/docs/manage-rovo-dev-cli-settings/
  - https://support.atlassian.com/bitbucket-cloud/docs/rovo-dev-advanced-agentic-configuration/
  - https://support.atlassian.com/rovo/docs/connect-to-an-mcp-server-in-rovo-dev-cli/
  - https://support.atlassian.com/rovo/docs/rovo-dev-cli-commands/
---

# Talk-to: Rovo Dev CLI

**Fidelity: documented** - built from Atlassian's official Rovo Dev support
docs (CLI settings, advanced agentic configuration, MCP). Not exercised against
a live gate here.

## 1. Identity
- **Harness**: Rovo Dev CLI (Atlassian), invoked as `acli rovodev` - an agentic
  coding CLI wired to Jira/Confluence via a built-in Atlassian MCP.
- **ctx provider (read)**: `rovodev`.
- **Lineage**: independent (Atlassian's own agent), not a Claude-Code clone.

## 2. Hook engine
- **No lifecycle hook engine.** There is no `PreToolUse`/`PostToolUse`-style
  event system and no way to register scripts on agent lifecycle events - the
  docs describe none.
- **Gating is a static permission policy, not an external gate process.** Rovo
  Dev has a three-tier **`toolPermissions`** model: `allow` (auto-run), `ask`
  (prompt the human - the default), and `deny` (refuse), applied globally,
  per-tool, and per-bash-command (e.g. allow `ls.*`, deny the rest). Advanced
  configs support default-deny + allowlisting. In pipelines these merge as
  base -> user file -> overrides -> system-enforced (last wins).
- **Failure mode**: fail-open/closed of an external hook does **not apply** -
  decisions are made inside the agent from config, so there is no separate gate
  process to time out or crash. The default posture is conservative: unlisted
  tools resolve to **`ask`** (human prompt), and system-enforced overrides can
  clamp permissions in CI. Hence `fails_open: false` in the "no silent allow on
  error" sense - but note the mechanism is a config policy, not a spawned gate.

## 3. Config
- **Path**: `~/.rovodev/config.yml` (a custom path is selectable via
  `acli rovodev run --config-file`). MCP servers live in `~/.rovodev/mcp.json`
  (edit with `acli rovodev mcp`). In Bitbucket Pipelines, `.rovodev/config.yaml`
  plus `config.overrides` in `bitbucket-pipelines.yml`.
- **Format**: YAML (config) / JSON (mcp.json).
- **Knobs that matter**: `toolPermissions` (allow/ask/deny), per-bash-command
  rules, `persistenceDir`, and the experimental `enableWorkspaceStateSync`.

## 4. Transcript pointer
- **Path pattern**: sessions persist under `~/.rovodev/sessions` (the
  `persistenceDir`); logs at `~/.rovodev/logs/rovodev.log`. Docs do not confirm
  whether the session store is a full turn-by-turn transcript or checkpoint
  state - treat the exact read format as **needs confirmation**; ctx is the
  read-side authority.

## 5. Capabilities and caveats
- Gate risky tools via `toolPermissions: deny` / default-deny allowlists, and
  fall back to `ask` for human-in-the-loop approval - but this is coarse static
  policy, not a programmable per-call hook that can inspect payloads.
- No event surface means no witness/observe hook: to capture activity you read
  the session store rather than subscribe to events.

## Sources
- Manage Rovo Dev CLI settings - https://support.atlassian.com/rovo/docs/manage-rovo-dev-cli-settings/
- Rovo Dev: Advanced agentic configuration - https://support.atlassian.com/bitbucket-cloud/docs/rovo-dev-advanced-agentic-configuration/
- Connect to an MCP server in Rovo Dev CLI - https://support.atlassian.com/rovo/docs/connect-to-an-mcp-server-in-rovo-dev-cli/
- Rovo Dev CLI commands - https://support.atlassian.com/rovo/docs/rovo-dev-cli-commands/
