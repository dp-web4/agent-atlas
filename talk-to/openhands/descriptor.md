---
harness: OpenHands
ctx_provider: openhands
vendor: All Hands AI
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [agent_action_confirmation, security_analyzer]
fails_open: unknown
subagent_hooks_inherited: untested
config_path: config.toml
config_format: toml
resource_type: [local, api]
fidelity: documented
sources:
  - https://docs.openhands.dev/sdk/guides/security
  - https://deepwiki.com/All-Hands-AI/OpenHands
  - https://arxiv.org/html/2511.03690v2
---

# Talk-to: OpenHands

**Fidelity: documented** - from OpenHands' official SDK security guide plus the
architecture wiki and the SDK paper. It is a Python event-stream agent, not a
command-hook CLI, so the "hook" surface is programmatic.

## 1. Identity
- **Harness**: OpenHands ([All Hands AI](https://www.all-hands.dev/), formerly
  OpenDevin), an open-source autonomous software-development agent running in a
  sandboxed (Docker) runtime.
- **ctx provider (read)**: `openhands`.
- **Lineage**: **independent.** Architecture is an **immutable event stream**:
  every action and observation is an event, and gating is done by components
  subscribed to that stream — not by external shell hooks or exit codes.

## 2. Hook engine
- **Mechanism (programmatic, in-process Python)**: two composable layers gate
  actions before execution —
  1. a **SecurityAnalyzer** (`SecurityAnalyzerBase.security_risk()`) labels each
     action `LOW`/`MEDIUM`/`HIGH`/`UNKNOWN`. Built-ins: `LLMSecurityAnalyzer`,
     `PatternSecurityAnalyzer`, `PolicyRailSecurityAnalyzer`,
     `EnsembleSecurityAnalyzer`.
  2. a **ConfirmationPolicy** decides whether that risk needs approval:
     `AlwaysConfirm`, `NeverConfirm`, `ConfirmRisky(threshold=HIGH,
     confirm_unknown=…)`.
- **Blocking-capable**: yes. Under `ConfirmRisky`, an action at/above the
  threshold pauses the conversation in `WAITING_FOR_CONFIRMATION`; the caller can
  `conversation.reject_pending_actions()` to deny while preserving agent context
  so it can retry a safer path. `AlwaysConfirm` gates every action. Wired via
  `conversation.set_security_analyzer()` / `set_confirmation_policy()`.
- **Failure mode**: **unknown / not documented for analyzer error.** The
  conservative signal is `confirm_unknown=True`, which routes `UNKNOWN` risk to
  confirmation (fail-safe by default). But two holes matter: (a)
  `conversation.execute_tool()` **bypasses both analyzer and policy entirely**,
  and (b) a reported bug crashes CLI v1 when the LLM emits a `security_risk` with
  no analyzer configured. Treat the gate as opt-in and easy to bypass; **do not
  assume it fails closed.**

## 3. Config
- **Path**: application config is `config.toml` (project root); the v1 SDK is
  configured **programmatically in Python**. A `security_policy_filename` param
  points at a Jinja2 template injected into the agent's system prompt.
- **Format**: TOML (app) / code (SDK).

## 4. Transcript pointer
- The event stream is the transcript: immutable action/observation events enabling
  deterministic replay (trajectory). Persisted via the SDK's file store; the exact
  path is deployment-dependent and not fixed in the docs reviewed. The event
  stream, not a single JSONL, is the read-side authority.

## 5. Capabilities and caveats
- Rich observe (subscribe to the event stream) and a real programmable gate, but
  the gate is in-process Python you must instantiate — there is no external
  command hook to drop in.
- `execute_tool()` bypass is the load-bearing caveat for any gate design.
