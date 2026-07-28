---
harness: Qwen Code
ctx_provider: qwen_code
vendor: Alibaba (QwenLM)
lineage: claude
hook_engine: true
blocking_capable: true
blocking_events: [PreToolUse, PermissionRequest, UserPromptSubmit]
fails_open: true
subagent_hooks_inherited: untested
config_path: ~/.qwen/settings.json (also project .qwen/settings.json)
config_format: json
resource_type: [api, local, free]
fidelity: documented
sources:
  - https://qwenlm.github.io/qwen-code-docs/en/users/features/hooks/
  - https://github.com/QwenLM/qwen-code/blob/main/docs/users/features/hooks.md
  - https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/
  - https://qwenlm.github.io/qwen-code-docs/en/users/features/checkpointing/
---

# Talk-to: Qwen Code

**Fidelity: documented** - built from Qwen Code's official hooks and settings docs; the hook engine is a near-identical Claude-Code clone, so its failure model is inherited rather than independently re-run.

## 1. Identity
- **Harness**: Qwen Code ([Alibaba / QwenLM](https://github.com/QwenLM/qwen-code)), a coding-agent CLI forked from Google's Gemini CLI.
- **ctx provider (read)**: `qwen_code`.
- **Lineage**: although the CLI shell descends from Gemini CLI, its *hook engine* is a Claude-Code-lineage clone: same event names, `exit code 2` to block, `hookSpecificOutput.permissionDecision: "deny"` JSON, `.../settings.json` config, and the same fail-open default. See [`../claude/descriptor.md`](../claude/descriptor.md) for the shared failure model.

## 2. Hook engine
- **Events**: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `SessionStart`, `SessionEnd`, `Stop`, `StopFailure`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`, `Notification`, `PermissionRequest`, `TodoCreated`, `TodoCompleted`. Hook executors can be command (stdin/stdout JSON) or HTTP.
- **Blocking-capable events**: `PreToolUse` denies a tool call via `exit 2` (stderr fed back to the model) or `permissionDecision: "deny"`; `PermissionRequest` denies via `decision.behavior: "deny"`; `UserPromptSubmit` can block prompt submission. `TodoCreated`/`TodoCompleted` can block persistence during validation. `PostToolUse` and the rest are observational.
- **Failure mode**: **fails open.** Exit `0` = success, exit `2` = blocking error, any other exit = *non-blocking* error (operation proceeds); timeouts default to 60 s and resolve to allow. HTTP-hook error semantics are not spelled out in the docs. **A gate on Qwen Code must be fail-closed by construction**: deny by default, `exit 0` only on an explicit confirmed pass, never rely on the engine to deny for you.

## 3. Config
- **Path**: `~/.qwen/settings.json` (user) and project `.qwen/settings.json`.
- **Format**: JSON. Top-level `"hooks"` object maps each event to an array of matcher objects, each with a `"hooks"` array of executor definitions (type, command/url, name, timeout).
- **Knobs that matter**: `disableAllHooks: true` kills every hook at once (top-level, alongside `hooks`) — an audit tripwire worth watching.

## 4. Transcript pointer
- **Path pattern**: on-disk chat recording at `~/.qwen/projects/<sanitized-cwd>/chats/<sessionId>.jsonl`, used for continue/resume. Checkpoints live under `~/.qwen/tmp/<project_hash>/checkpoints`; optional OpenAI-wire logging under `~/.qwen/logs/openai/`.
- **Notable fields**: JSONL per-turn conversation and tool-call records — the read side's input.

## 5. Capabilities and caveats
- Full observe + gate: wire non-blocking events (`SessionStart`/`PostToolUse`/`SessionEnd`) to witness, `PreToolUse`/`PermissionRequest` to gate.
- Because the engine is a Claude-Code clone, a hestia-style adapter can largely reuse the Claude plugin, changing only the config path (`.qwen/settings.json`) and the transcript path.
