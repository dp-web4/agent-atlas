# Provider registry

The set of coding-agent harnesses agent-atlas knows about, with **read** coverage
(where its transcript lives / what format, via ctx) and **talk-to** coverage (its
integration surface, via a descriptor in [`../talk-to/`](../talk-to/)).

The provider identifiers and the read coverage are **derived from ctx's
`CaptureProvider` registry** (`crates/ctx-history-core/src/source.rs`,
[ctxrs/ctx](https://github.com/ctxrs/ctx), Apache-2.0). ctx is the authoritative
source of the read side; this table mirrors it and adds the talk-to column. When
ctx adds a provider, this table should be re-synced from it.

**The `ctx provider` id is the join key.** Each talk-to descriptor lives at
`../talk-to/<ctx-provider-id>/descriptor.md`, so the read and talk-to halves of a
harness pair on the same id with no lookup table. Read status here means "ctx has a
provider for it"; for the exact transcript path and wire format, consult ctx (its
per-source format ids, e.g. `kimi_code_cli_wire_jsonl_tree`, are ground truth).
Talk-to status means "a descriptor exists against
[`../talk-to/SCHEMA.md`](../talk-to/SCHEMA.md)"; its `fidelity` (verified /
documented / inferred) is in the descriptor's frontmatter.

## Coding-agent harnesses

| Harness | ctx provider (read) | talk-to descriptor |
|---|---|---|
| Claude Code | `claude` | [claude](../talk-to/claude/descriptor.md) |
| Kimi Code CLI | `kimi_code_cli` | [kimi_code_cli](../talk-to/kimi_code_cli/descriptor.md) |
| Codex | `codex` | [codex](../talk-to/codex/descriptor.md) |
| Cursor | `cursor` | [cursor](../talk-to/cursor/descriptor.md) |
| Gemini | `gemini` | [gemini](../talk-to/gemini/descriptor.md) |
| Copilot CLI | `copilot_cli` | [copilot_cli](../talk-to/copilot_cli/descriptor.md) |
| Qwen Code | `qwen_code` | [qwen_code](../talk-to/qwen_code/descriptor.md) |
| Cline | `cline` | [cline](../talk-to/cline/descriptor.md) |
| Roo Code | `roo_code` | [roo_code](../talk-to/roo_code/descriptor.md) |
| Goose | `goose` | [goose](../talk-to/goose/descriptor.md) |
| OpenCode | `opencode` | [opencode](../talk-to/opencode/descriptor.md) |
| OpenHands | `openhands` | [openhands](../talk-to/openhands/descriptor.md) |
| Continue | `continue` | [continue](../talk-to/continue/descriptor.md) |
| Windsurf | `windsurf` | [windsurf](../talk-to/windsurf/descriptor.md) |
| Zed | `zed` | [zed](../talk-to/zed/descriptor.md) |
| Tabnine | `tabnine` | [tabnine](../talk-to/tabnine/descriptor.md) |
| Warp | `warp` | [warp](../talk-to/warp/descriptor.md) |
| Trae | `trae` | [trae](../talk-to/trae/descriptor.md) |
| Crush | `crush` | [crush](../talk-to/crush/descriptor.md) |
| Pi | `pi` | [pi](../talk-to/pi/descriptor.md) |
| Kilo | `kilo` | [kilo](../talk-to/kilo/descriptor.md) |
| Kiro CLI | `kiro_cli` | [kiro_cli](../talk-to/kiro_cli/descriptor.md) |
| Antigravity | `antigravity` | [antigravity](../talk-to/antigravity/descriptor.md) |
| Factory.ai Droid | `factory_ai_droid` | [factory_ai_droid](../talk-to/factory_ai_droid/descriptor.md) |
| Auggie | `auggie` | [auggie](../talk-to/auggie/descriptor.md) |
| Junie | `junie` | [junie](../talk-to/junie/descriptor.md) |
| Firebender | `firebender` | [firebender](../talk-to/firebender/descriptor.md) |
| Forge Code | `forgecode` | [forgecode](../talk-to/forgecode/descriptor.md) |
| DeepAgents | `deepagents` | [deepagents](../talk-to/deepagents/descriptor.md) |
| Mistral Vibe | `mistral_vibe` | [mistral_vibe](../talk-to/mistral_vibe/descriptor.md) |
| Mux | `mux` | [mux](../talk-to/mux/descriptor.md) |
| Rovo Dev | `rovodev` | [rovodev](../talk-to/rovodev/descriptor.md) |
| OpenClaw | `openclaw` | [openclaw](../talk-to/openclaw/descriptor.md) |
| Hermes | `hermes` | [hermes](../talk-to/hermes/descriptor.md) |
| NanoClaw | `nanoclaw` | [nanoclaw](../talk-to/nanoclaw/descriptor.md) |
| AstrBot | `astrbot` | [astrbot](../talk-to/astrbot/descriptor.md) |
| Shelley | `shelley` | [shelley](../talk-to/shelley/descriptor.md) |
| Lingma | `lingma` | [lingma](../talk-to/lingma/descriptor.md) |
| Qoder | `qoder` | [qoder](../talk-to/qoder/descriptor.md) |
| CodeBuddy | `codebuddy` | [codebuddy](../talk-to/codebuddy/descriptor.md) |
| MiMoCode | `mimocode` | [mimocode](../talk-to/mimocode/descriptor.md) |

## Talk-to ahead of read (not yet in ctx)

Harnesses with an integration surface worth describing that ctx does not yet have a
read provider for. These use a natural id and `ctx_provider: none`; when ctx adds a
read provider, rename the directory to the ctx id so the two halves rejoin.

| Harness | ctx provider (read) | talk-to descriptor |
|---|---|---|
| Aider | *(none yet)* | [aider](../talk-to/aider/descriptor.md) |
| Amp | *(none yet)* | [amp](../talk-to/amp/descriptor.md) |
| Cody | *(none yet)* | [cody](../talk-to/cody/descriptor.md) |
| Devin | *(none yet)* | [devin](../talk-to/devin/descriptor.md) |

## Dev-context sources (not agents)

ctx also reads non-agent developer context, carried here for completeness. These
have no talk-to surface (there is nothing to gate):

`shell`, `git`, `jj`, `gh` - and `custom` / `unknown` as catch-alls.

---

**Read: 41 coding-agent harnesses** (from ctx). **Talk-to: 45 descriptors** — 41
joined to a ctx read provider plus 4 ahead of read (`aider`, `amp`, `cody`, `devin`).
Each carries a `fidelity` mark in its frontmatter (`verified` for `claude` and
`kimi_code_cli`, which run against live hestia adapters; `documented` / `inferred` for
the rest, sourced from vendor docs). For a one-screen taxonomy of all descriptors —
gate type, lineage, and fail-open/closed behavior — see
[`../talk-to/OVERVIEW.md`](../talk-to/OVERVIEW.md). Improving a descriptor, or raising
its fidelity by wiring it against the real harness, is a documentation task against
[`../talk-to/SCHEMA.md`](../talk-to/SCHEMA.md), not a code port.
