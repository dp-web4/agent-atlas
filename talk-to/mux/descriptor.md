---
harness: Mux
ctx_provider: mux
vendor: Coder
lineage: independent
hook_engine: true
blocking_capable: false
blocking_events: []
fails_open: unknown
subagent_hooks_inherited: untested
config_path: ~/.mux/config.json
config_format: json
resource_type: [local, api]
fidelity: documented
sources:
  - https://mux.coder.com/reference/cli
  - https://mux.coder.com/hooks/init
  - https://mux.coder.com/AGENTS
  - https://github.com/coder/mux
---

# Talk-to: Mux

**Fidelity: documented** - built from Coder's official Mux docs (CLI reference,
init hooks, AGENTS) and the `coder/mux` repo. Not exercised against a live gate.

## 1. Identity
- **Harness**: Mux (by **Coder**) - a desktop app + CLI for isolated, parallel
  agentic development across git worktrees; built on Anthropic's Claude Agent
  SDK. Disambiguate hard from **Mux the video API** (mux.com / muxinc) and from
  **tmux/dmux** - this is `coder/mux`, docs at `mux.coder.com`.
- **ctx provider (read)**: `mux`.
- **Lineage**: independent. It consumes the Claude Agent SDK as a library but
  does not clone Claude Code's hook engine; its hook surface is its own and much
  narrower.

## 2. Hook engine
- **Hooks exist, but none are gates.** Mux supports **init hooks**: an
  executable `.mux/init` at the project root that runs on workspace creation
  (dependency install, build, DB setup). It also has **workflows**
  (`mux workflow run <script_path>`, experimental) addressed by explicit path -
  no discovery/list command. All repo-controlled automation (workflows, hooks,
  `.mux` config) is gated by **project trust** (Settings -> Security, or
  `mux trust`).
- **Blocking-capable events**: **none.** There is no `PreToolUse`-style hook
  that can deny an agent tool call - the documented hooks are setup/lifecycle
  side effects only. `blocking_capable: false`.
- **Failure mode**: for the init hook, "failures are logged but don't prevent
  workspace usage" - i.e. a failing setup hook does not block the agent (fail
  open in the setup sense). Since there is **no** tool-gating surface, classic
  fail-open/closed is not applicable; recorded as `unknown` because no blocking
  path exists to characterize.

## 3. Config
- **Path**: `~/.mux/config.json` (global: trust entries, GitHub auth like
  `serverAuthGithubOwner`). Project-level config + the `.mux/init` script live
  under `.mux/` in the repo.
- **Format**: JSON (global); `.mux/init` is a plain executable script.
- **Knobs that matter**: **trust** is the real control - untrusted projects will
  not execute workflow/hook code (`mux workflow run` fails before running a
  local script in an untrusted project).

## 4. Transcript pointer
- **Path pattern**: **unknown / not documented** in the public CLI and hooks
  docs. Mux runs per-workspace agent sessions but the transcript store location
  is not stated; ctx is the read-side authority and would need to reverse it.

## 5. Capabilities and caveats
- Use init hooks for per-workspace setup, not policy - Mux offers no way to
  intercept or veto an individual tool call.
- **Gate implication**: because there is no PreToolUse surface, Mux cannot host
  a fail-closed pre-tool gate. Any enforcement must live outside Mux (sandbox,
  filesystem/permission boundary, or the trust boundary itself). Trust is the
  only built-in guardrail and it is coarse (whole-project on/off).

## Sources
- CLI reference - https://mux.coder.com/reference/cli
- Init Hooks - https://mux.coder.com/hooks/init
- AGENTS - https://mux.coder.com/AGENTS
- coder/mux - https://github.com/coder/mux
