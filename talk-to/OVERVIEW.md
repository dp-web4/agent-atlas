# Talk-to coverage overview

> **Generated** from each `talk-to/<id>/descriptor.md` frontmatter by `gen-overview.py`. Do not edit by hand; regenerate after changing a descriptor. Every cell traces to a descriptor's frontmatter.

**45 harnesses.** 31 expose a hook/plugin gate engine, 2 gate only via static policy, 12 have no external gate seam (gate them from outside). 16 run Claude Code's hook engine (canonical or lineage) — the most-cloned integration surface. 4 are talk-to ahead of ctx's read side.

**Failure mode across the hook engines is not monolithic** — the load-bearing fact for anyone building a gate:

- **fails open** (19): a failed/timed-out blocking hook resolves to *allow*. The gate must be the fail-closed party itself.
- **fails closed** (5): a failed hook *denies* — safer, but a slow gate can halt the agent.
- **undocumented** (7): the vendor spec omits the error/timeout behavior. Treat as fail-open until verified.

Fidelity: 2 verified (wired against the real harness), 42 documented (from vendor docs), 1 inferred.

## Matrix

| Harness | id | ctx read | lineage | gate | fails-open | fidelity |
|---|---|:--:|---|---|---|---|
| Aider | `aider` | — | independent | no gate seam | — | documented |
| Amp | `amp` | — | independent | hook engine | undocumented | documented |
| Antigravity | `antigravity` | ✓ | claude | hook engine | closed | documented |
| AstrBot | `astrbot` | ✓ | independent | hook engine | undocumented | documented |
| Auggie (Augment Code) | `auggie` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Claude Code | `claude` | ✓ | canonical | hook engine | **open** ⚠ | verified |
| Cline | `cline` | ✓ | independent | hook engine | **open** ⚠ | documented |
| CodeBuddy | `codebuddy` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Codex CLI | `codex` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Cody | `cody` | — | independent | no gate seam | — | documented |
| Continue | `continue` | ✓ | independent | no gate seam | undocumented | documented |
| GitHub Copilot CLI | `copilot_cli` | ✓ | claude | hook engine | closed | documented |
| Crush | `crush` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Cursor | `cursor` | ✓ | independent | hook engine | **open** ⚠ | documented |
| DeepAgents (CLI) | `deepagents` | ✓ | independent | hook engine | closed | documented |
| Devin | `devin` | — | independent | no gate seam | — | documented |
| Droid (Factory.ai) | `factory_ai_droid` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Firebender | `firebender` | ✓ | independent | no gate seam | undocumented | documented |
| Forge Code | `forgecode` | ✓ | independent | static policy | closed | documented |
| Gemini CLI | `gemini` | ✓ | independent | hook engine | **open** ⚠ | documented |
| Goose | `goose` | ✓ | independent | no gate seam | — | documented |
| Hermes Agent | `hermes` | ✓ | independent | hook engine | **open** ⚠ | documented |
| Junie (JetBrains) | `junie` | ✓ | independent | no gate seam | undocumented | documented |
| Kilo Code | `kilo` | ✓ | opencode | hook engine | undocumented | documented |
| Kimi Code CLI | `kimi_code_cli` | ✓ | claude | hook engine | **open** ⚠ | verified |
| Kiro (AWS) | `kiro_cli` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Lingma / Qoder CN CLI | `lingma` | ✓ | claude | hook engine | **open** ⚠ | documented |
| MiMo Code | `mimocode` | ✓ | opencode | hook engine | undocumented | documented |
| Mistral Vibe | `mistral_vibe` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Mux | `mux` | ✓ | independent | no gate seam | undocumented | documented |
| NanoClaw | `nanoclaw` | ✓ | claude | hook engine | **open** ⚠ | inferred |
| OpenClaw | `openclaw` | ✓ | independent | hook engine | undocumented | documented |
| OpenCode | `opencode` | ✓ | independent | hook engine | closed | documented |
| OpenHands | `openhands` | ✓ | independent | hook engine | undocumented | documented |
| Pi | `pi` | ✓ | independent | hook engine | undocumented | documented |
| Qoder | `qoder` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Qwen Code | `qwen_code` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Roo Code | `roo_code` | ✓ | cline | no gate seam | — | documented |
| Rovo Dev CLI | `rovodev` | ✓ | independent | static policy | closed | documented |
| Shelley | `shelley` | ✓ | independent | hook engine | closed | documented |
| Tabnine CLI | `tabnine` | ✓ | claude | hook engine | **open** ⚠ | documented |
| Trae (AI IDE) | `trae` | ✓ | independent | no gate seam | undocumented | documented |
| Warp (Agent Mode) | `warp` | ✓ | independent | no gate seam | undocumented | documented |
| Windsurf (Cascade) | `windsurf` | ✓ | independent | hook engine | **open** ⚠ | documented |
| Zed (Agent Panel) | `zed` | ✓ | independent | no gate seam | undocumented | documented |

_ctx read: ✓ = ctx has a read provider for this id; — = talk-to ahead of read (`ctx_provider: none`)._
