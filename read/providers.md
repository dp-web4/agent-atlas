# Provider registry

The set of coding-agent harnesses agent-atlas knows about, with **read** coverage
(where its transcript lives / what format, via ctx) and **talk-to** coverage (its
integration surface, via a descriptor in [`../talk-to/`](../talk-to/)).

The provider identifiers and the read coverage are **derived from ctx's
`CaptureProvider` registry** (`crates/ctx-history-core/src/source.rs`,
[ctxrs/ctx](https://github.com/ctxrs/ctx), Apache-2.0). ctx is the authoritative
source of the read side; this table mirrors it and adds the talk-to column. When
ctx adds a provider, this table should be re-synced from it.

Read status here means "ctx has a provider for it." For the exact transcript path
and wire format per harness, consult ctx (its per-source format ids, e.g.
`kimi_code_cli_wire_jsonl_tree`, are the ground truth). Talk-to status means "a
descriptor exists in this repo against [`../talk-to/SCHEMA.md`](../talk-to/SCHEMA.md)."

## Coding-agent harnesses

| Harness | ctx provider (read) | talk-to descriptor |
|---|---|---|
| Claude Code | `claude` | [claude-code](../talk-to/claude-code.md) |
| Kimi Code CLI | `kimi_code_cli` | [kimi](../talk-to/kimi.md) |
| Codex | `codex` | - |
| Cursor | `cursor` | - |
| Gemini | `gemini` | - |
| Copilot CLI | `copilot_cli` | - |
| Qwen Code | `qwen_code` | - |
| Cline | `cline` | - |
| Roo Code | `roo_code` | - |
| Goose | `goose` | - |
| OpenCode | `opencode` | - |
| OpenHands | `openhands` | - |
| Continue | `continue` | - |
| Windsurf | `windsurf` | - |
| Zed | `zed` | - |
| Tabnine | `tabnine` | - |
| Warp | `warp` | - |
| Trae | `trae` | - |
| Crush | `crush` | - |
| Pi | `pi` | - |
| Kilo | `kilo` | - |
| Kiro CLI | `kiro_cli` | - |
| Antigravity | `antigravity` | - |
| Factory.ai Droid | `factory_ai_droid` | - |
| Auggie | `auggie` | - |
| Junie | `junie` | - |
| Firebender | `firebender` | - |
| Forge Code | `forgecode` | - |
| DeepAgents | `deepagents` | - |
| Mistral Vibe | `mistral_vibe` | - |
| Mux | `mux` | - |
| Rovo Dev | `rovodev` | - |
| OpenClaw | `openclaw` | - |
| Hermes | `hermes` | - |
| NanoClaw | `nanoclaw` | - |
| AstrBot | `astrbot` | - |
| Shelley | `shelley` | - |
| Lingma | `lingma` | - |
| Qoder | `qoder` | - |
| CodeBuddy | `codebuddy` | - |
| MiMoCode | `mimocode` | - |

## Dev-context sources (not agents)

ctx also reads non-agent developer context, carried here for completeness. These
have no talk-to surface (there is nothing to gate):

`shell`, `git`, `jj`, `gh` - and `custom` / `unknown` as catch-alls.

---

**Read: 41 coding-agent harnesses** (from ctx). **Talk-to: 2** with descriptors
today (`claude-code`, `kimi`); the other 39 are open contributions. Adding one is a
documentation task against [`../talk-to/SCHEMA.md`](../talk-to/SCHEMA.md), not a code port.
