---
harness: Devin
ctx_provider: none
vendor: Cognition Labs
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: n/a
subagent_hooks_inherited: untested
config_path: unknown
config_format: unknown
resource_type: [subscription, api]
fidelity: documented
sources:
  - https://docs.devin.ai/api-reference/overview
  - https://docs.devin.ai/api-reference/sessions/create-a-new-devin-session
  - https://cognition.com/blog/devin-101-automatic-pr-reviews-with-the-devin-api
---

# Talk-to: Devin

**Fidelity: documented** - from Cognition's official Devin API docs; Devin is not yet in ctx's read registry, so this talk-to note leads the read side.

## 1. Identity   (note: not yet in ctx read registry — talk-to leads read here)
- **Harness**: Devin, Cognition Labs' autonomous cloud software engineer. It runs in Cognition's hosted cloud (its own VM/workspace), not as a local CLI on the operator's machine.
- **ctx provider (read)**: none. Use `devin` as the natural id; `ctx_provider: none`.
- **Lineage**: independent. Cloud-hosted agent with a REST/webhook/Slack surface — no local hook engine, so nothing in the Claude-Code lineage applies.

## 2. Hook engine
- **No local hook engine, no local gate seam.** Devin executes remotely; there is no PreToolUse-style event on the operator's box to intercept. Its integration surface is a **REST API** (`https://api.devin.ai/v1/sessions` to create a session, plus follow-up messages, file uploads; v3 `.../v3/organizations/*` and `.../v3/enterprise/*` for org/enterprise management), **webhooks** (e.g. Jira/Linear ticket events can trigger a Devin), and **Slack**.
- **Blocking**: not at the harness. You cannot deny an individual tool call inside Devin's cloud run from outside. Control is coarse and out-of-band — gate at the API boundary (decide whether to spin up a session, scope its credentials/secrets via service users + RBAC), review its output before merge, and constrain what its connected integrations (repo tokens, deploy keys) are allowed to touch.
- Consequence for an integrator: **gate OUTSIDE the harness, at the API/webhook boundary and in repo/CI review** — Devin has no in-process seam. This recorded absence is the finding: enforcement is a perimeter, not a hook.

## 3. Config
- **Path**: unknown / not a local file. Devin is configured via the hosted product (org settings, playbooks, knowledge, secrets) and via API key auth (personal `apk_user_*` / service `apk_*`; service users carry `cog_` identities with RBAC). No documented local config file on the operator's machine.
- **Format**: unknown (cloud/API-administered).

## 4. Transcript pointer
- **No local transcript.** Session state lives in Cognition's cloud and is reached through the API (create session, send follow-up messages, retrieve session status/output) rather than an on-disk file. The read side is an API pull, not a file tail, and ctx does not yet cover this harness's read side.

## 5. Capabilities and caveats
- **Observe**: via the API (session status/messages, audit logs, analytics on Enterprise) and via the PRs/commits Devin opens — not via a local log.
- **Gate**: none in-harness; the only real levers are whether to start a session, the scope of the credentials/secrets and RBAC you hand it, and human review of its PRs. Treat Devin as an external actor to be perimeter-controlled, not a gate-able local tool runner.
- **Caveat**: because it is fully hosted, an operator's local sandbox/hooks give no coverage — plan enforcement entirely on the API boundary and downstream review.
