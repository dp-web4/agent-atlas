# Talk-to coverage overview

> **Generated** from each `talk-to/<id>/descriptor.md` frontmatter by `gen-overview.py`. Do not edit by hand; regenerate after changing a descriptor. Every cell traces to a descriptor's frontmatter.

**46 harnesses.** 31 expose a hook/plugin gate engine, 2 gate only via static policy, 12 have no external gate seam (gate them from outside). 16 run Claude Code's hook engine (canonical or lineage) — the most-cloned integration surface. 5 are talk-to ahead of ctx's read side. 1 is a being rather than a driven harness (`kind: being`); 1 of those gate by construction — no effectors of their own, every intent judged before dispatch.

**Failure mode across the hook engines is not monolithic** — the load-bearing fact for anyone building a gate:

- **fails open** (19): a failed/timed-out blocking hook resolves to *allow*. The gate must be the fail-closed party itself.
- **fails closed** (5): a failed hook *denies* — safer, but a slow gate can halt the agent.
- **undocumented** (7): the vendor spec omits the error/timeout behavior. Treat as fail-open until verified.

Fidelity: 3 verified (wired against the real harness), 42 documented (from vendor docs), 1 inferred.

**Resource type** — how you pay to run the model, so how freely it can be used (a harness may offer several):

- **subscription** (26): usage-limited, seat/plan-covered, no per-call charge — the safe default for sustained work.
- **api** (31): metered pay-per-token — expensive, use with caution. Subscription tiers are increasingly a capped skin over the same API backend.
- **local** (22): self-hosted weights, no external billing — cost is compute.
- **free** (6): free tier, hard rate limits.

## Matrix

| Harness | id | ctx read | lineage | gate | fails-open | resource | fidelity |
|---|---|:--:|---|---|---|---|---|
| Aider | `aider` | — | independent | no gate seam | — | local, api | documented |
| Amp | `amp` | — | independent | hook engine | undocumented | subscription, api | documented |
| Antigravity | `antigravity` | ✓ | claude | hook engine | closed | subscription, free | documented |
| AstrBot | `astrbot` | ✓ | independent | hook engine | undocumented | local, api | documented |
| Auggie (Augment Code) | `auggie` | ✓ | claude | hook engine | **open** ⚠ | subscription | documented |
| Claude Code | `claude` | ✓ | canonical | hook engine | **open** ⚠ | subscription, api | verified |
| Cline | `cline` | ✓ | independent | hook engine | **open** ⚠ | local, api | documented |
| CodeBuddy | `codebuddy` | ✓ | claude | hook engine | **open** ⚠ | subscription | documented |
| Codex CLI | `codex` | ✓ | claude | hook engine | **open** ⚠ | subscription, api | verified |
| Cody | `cody` | — | independent | no gate seam | — | subscription, free | documented |
| Continue | `continue` | ✓ | independent | no gate seam | undocumented | local, api | documented |
| GitHub Copilot CLI | `copilot_cli` | ✓ | claude | hook engine | closed | subscription | documented |
| Crush | `crush` | ✓ | claude | hook engine | **open** ⚠ | local, api | documented |
| Cursor | `cursor` | ✓ | independent | hook engine | **open** ⚠ | subscription, api | documented |
| DeepAgents (CLI) | `deepagents` | ✓ | independent | hook engine | closed | local, api | documented |
| Devin | `devin` | — | independent | no gate seam | — | subscription, api | documented |
| Droid (Factory.ai) | `factory_ai_droid` | ✓ | claude | hook engine | **open** ⚠ | subscription, api | documented |
| Firebender | `firebender` | ✓ | independent | no gate seam | undocumented | subscription | documented |
| Forge Code | `forgecode` | ✓ | independent | static policy | closed | local, api | documented |
| Gemini CLI | `gemini` | ✓ | independent | hook engine | **open** ⚠ | subscription, api | documented |
| Goose | `goose` | ✓ | independent | no gate seam | — | local, api | documented |
| Hermes Agent | `hermes` | ✓ | independent | hook engine | **open** ⚠ | local, api | documented |
| Junie (JetBrains) | `junie` | ✓ | independent | no gate seam | undocumented | subscription | documented |
| Kilo Code | `kilo` | ✓ | opencode | hook engine | undocumented | local, api | documented |
| Kimi Code CLI | `kimi_code_cli` | ✓ | claude | hook engine | **open** ⚠ | subscription, api | verified |
| Kiro (AWS) | `kiro_cli` | ✓ | claude | hook engine | **open** ⚠ | subscription | documented |
| Lingma / Qoder CN CLI | `lingma` | ✓ | claude | hook engine | **open** ⚠ | subscription, free | documented |
| MiMo Code | `mimocode` | ✓ | opencode | hook engine | undocumented | local, api | documented |
| Mistral Vibe | `mistral_vibe` | ✓ | claude | hook engine | **open** ⚠ | subscription, api | documented |
| Mux | `mux` | ✓ | independent | no gate seam | undocumented | local, api | documented |
| NanoClaw | `nanoclaw` | ✓ | claude | hook engine | **open** ⚠ | subscription, api | inferred |
| OpenClaw | `openclaw` | ✓ | independent | hook engine | undocumented | local, api | documented |
| OpenCode | `opencode` | ✓ | independent | hook engine | closed | local, api | documented |
| OpenHands | `openhands` | ✓ | independent | hook engine | undocumented | local, api | documented |
| Pi | `pi` | ✓ | independent | hook engine | undocumented | local, api | documented |
| Qoder | `qoder` | ✓ | claude | hook engine | **open** ⚠ | subscription | documented |
| Qwen Code | `qwen_code` | ✓ | claude | hook engine | **open** ⚠ | api, local, free | documented |
| Roo Code | `roo_code` | ✓ | cline | no gate seam | — | local, api | documented |
| Rovo Dev CLI | `rovodev` | ✓ | independent | static policy | closed | subscription | documented |
| SAGE _(being)_ | `sage` | — | independent | built-in gate | closed | local | documented |
| Shelley | `shelley` | ✓ | independent | hook engine | closed | local, api | documented |
| Tabnine CLI | `tabnine` | ✓ | claude | hook engine | **open** ⚠ | subscription, local | documented |
| Trae (AI IDE) | `trae` | ✓ | independent | no gate seam | undocumented | subscription, free | documented |
| Warp (Agent Mode) | `warp` | ✓ | independent | no gate seam | undocumented | subscription, free | documented |
| Windsurf (Cascade) | `windsurf` | ✓ | independent | hook engine | **open** ⚠ | subscription, api | documented |
| Zed (Agent Panel) | `zed` | ✓ | independent | no gate seam | undocumented | subscription, api, local | documented |

_ctx read: ✓ = ctx has a read provider for this id; — = talk-to ahead of read (`ctx_provider: none`)._
