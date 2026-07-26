---
harness: Cline
ctx_provider: cline
vendor: Cline (open source)
lineage: independent
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, UserPromptSubmit]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/Documents/Cline/Rules/Hooks/ (global) or .clinerules/hooks/ (project)
config_format: executable scripts (directory of named executables)
fidelity: documented
sources:
  - https://cline.ghost.io/cline-v3-36-hooks/
  - https://docs.cline.bot/features/hooks/hook-reference
  - https://deepwiki.com/cline/cline/7.3-hooks-system
  - https://docs.cline.bot/features/auto-approve
---

# Talk-to: Cline

**Fidelity: documented** - built from Cline's v3.36 hooks announcement and docs; the hook contract (JSON `cancel`, fail-open on error/timeout) is stated in official sources but not independently re-run here.

## 1. Identity
- **Harness**: [Cline](https://github.com/cline/cline), an open-source autonomous coding agent shipped as a VS Code extension (also an SDK/CLI). Hooks landed in **v3.36**.
- **ctx provider (read)**: `cline`.
- **Lineage**: **independent.** Cline's hook engine is *not* a Claude-Code clone — it uses its own event set and a JSON `cancel` contract rather than Claude's `exit 2` / `permissionDecision` convention. The high-level shape (Pre/Post tool events) rhymes with Claude, but the mechanics differ.

## 2. Hook engine
- **Events** (6): `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `TaskStart`, `TaskResume`, `TaskCancel`. Each hook is an executable that receives operation context as JSON on **stdin** and returns JSON on **stdout**.
- **Blocking mechanism**: a hook blocks by returning `{"cancel": true}` (with optional `errorMessage`); `"cancel": false` allows. `PreToolUse` is the primary gate (block a tool before it runs); `UserPromptSubmit` can cancel a prompt. A `contextModification` field can inject text into the model's context. `PostToolUse`/`TaskStart`/`TaskResume` are effectively observational.
- **Failure mode**: **fails open, and this is documented explicitly.** A hook that exits non-zero, returns invalid JSON, or times out (**30 s** timeout) does **not** stop the task — only an explicit `{"cancel": true}` halts execution. **A gate on Cline must therefore be the fail-closed party itself**: emit `{"cancel": true}` by default and only return `cancel:false` on an explicit confirmed pass; never rely on a crash/timeout to deny.
- **OS**: hooks are **macOS and Linux only** — Windows is unsupported as of v3.36.

## 3. Config
- **Path**: global `~/Documents/Cline/Rules/Hooks/`; project-local `.clinerules/hooks/`. Enabled via Cline Settings -> Features.
- **Format**: not a single config file — a **directory of executable scripts**, each named exactly after its hook type with **no file extension**, marked executable. (Auto-approve categories, the separate in-UI gate, live in VS Code settings.)
- **Knobs that matter**: hooks are silently skipped if the `.clinerules/hooks` path contains whitespace (known bug #7185); disabling hooks in settings has had leakage bugs (#7184/#7334) — audit that they are actually off/on.

## 4. Transcript pointer
- **Path pattern**: **unknown / not officially documented as a stable path.** Cline persists task history and API-conversation JSON inside the VS Code extension's `globalStorage` (per-task directories), not a documented user-facing transcript file. The read side (`ctx`) is the authority here and should treat the storage layout as version-dependent.

## 5. Capabilities and caveats
- Observe without risk by wiring only non-blocking events (`PostToolUse`, `TaskStart`); gate by wiring `PreToolUse`.
- The hook contract is JSON-return, **not** exit-code: a gate ported from a Claude-lineage harness must be rewritten to speak `{"cancel": true}` rather than `exit 2`.
