---
harness: GitHub Copilot CLI
ctx_provider: copilot_cli
vendor: GitHub
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [preToolUse, permissionRequest, userPromptSubmitted]
fails_open: false
subagent_hooks_inherited: untested
config_path: ~/.copilot/hooks/*.json
config_format: json
fidelity: documented
sources:
  - https://docs.github.com/en/copilot/reference/hooks-reference
  - https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks
  - https://docs.github.com/en/copilot/tutorials/copilot-cli-hooks
  - https://github.com/github/copilot-cli/issues/2540
---

# Talk-to: GitHub Copilot CLI

**Fidelity: documented** - built from GitHub's official Copilot hooks reference;
the fail-closed-on-crash / fail-open-on-timeout split is stated by the vendor and
is the load-bearing subtlety here.

## 1. Identity
- **Harness**: GitHub Copilot CLI (GitHub), generally available Feb 2026.
- **ctx provider (read)**: `copilot_cli`.
- **Lineage**: Claude-Code-lineage. Copilot exposes the Claude event set (with
  both camelCase and PascalCase aliases - `preToolUse`/`PreToolUse`,
  `postToolUse`, `userPromptSubmitted`/`UserPromptSubmit`, `agentStop`/`Stop`,
  `permissionRequest`/`PermissionRequest`, `preCompact`, `subagentStart/Stop`)
  and the `permissionDecision: "deny"` + `exit 2` contract; see
  [`../claude/descriptor.md`](../claude/descriptor.md). **But it diverges from the
  lineage on failure semantics** (below), so this descriptor is not just a
  pointer.

## 2. Hook engine
- **Events**: `sessionStart`, `sessionEnd`, `userPromptSubmitted`,
  `userPromptTransformed`, `preToolUse`, `postToolUse`, `postToolUseFailure`,
  `agentStop`, `subagentStart`, `subagentStop`, `errorOccurred`, `preCompact`,
  `permissionRequest`, `notification` (each with a PascalCase alias).
- **Blocking-capable events**: `preToolUse` is the primary gate - it returns
  stdout JSON `{ "permissionDecision": "allow|deny|ask", "permissionDecisionReason":
  "...", "modifiedArgs": {} }`, so it can deny *or rewrite* a tool call.
  `exit 2` is a silent deny (v1.0.69+) and **always denies even if stdout JSON
  says `allow`**. `permissionRequest` and `userPromptSubmitted` also gate.
- **Failure mode**: **mostly fails CLOSED, and this is the exception in the
  batch.** For `preToolUse` command hooks, `exit 2`, non-zero exits, and crashes
  all **deny** the tool call. **The one hole: timeouts always fail OPEN** - "a
  warning is surfaced and the tool call proceeds" - and the docs say timeouts are
  fail-open for *every* event, including admin-deployed policy hooks. So a gate
  that hangs is bypassed. Set a tight timeout and still deny by default; do not
  rely on the engine's crash-time fail-closed to cover a hung gate.

## 3. Config
- **Path**: `~/.copilot/hooks/*.json` (user; or `$COPILOT_HOME/hooks/`),
  `.github/hooks/*.json` (repository-level; the only form the cloud agent reads),
  inline in `.github/copilot/settings.json`, and enterprise policy dirs
  (`/etc/github-copilot/policy.d/`, `C:\ProgramData\GitHub\Copilot\policy.d\`).
  MCP config is separate at `~/.copilot/mcp-config.json`.
- **Format**: JSON - `{ "version": 1, "hooks": { "preToolUse": [ ... ] } }`.
  Hook config is loaded at CLI start.
- **Knobs that matter**: `version: 1` is required; per-hook `timeout` (the
  fail-open edge); repository vs user vs enterprise-policy layering.

## 4. Transcript pointer
- **Path pattern**: Copilot CLI keeps session state under `~/.copilot/`, but a
  stable per-session transcript path/format is not pinned down here. The
  `copilot_cli` ctx provider is the read-side authority.

## 5. Capabilities and caveats
- Strong gate by default: crashes and non-zero exits deny, unlike the fail-open
  Claude/Kimi/Codex/Gemini engines - so a Copilot gate is safer out of the box.
- **Timeout is the residual footgun**: a slow or hung gate is bypassed, and
  admin policy hooks are not exempt. Keep gate latency well under the configured
  timeout.
- `modifiedArgs` lets `preToolUse` rewrite rather than only deny (e.g. strip a
  flag), a capability the base Claude lineage lacks.
- Known bug: plugin-bundled `preToolUse` hooks (via `hooks.json`) have failed to
  fire in some versions (issue #2540) - verify the gate actually triggers before
  trusting it.
