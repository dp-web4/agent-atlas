---
harness: Aider
ctx_provider: none
vendor: Aider (Paul Gauthier, open source)
lineage: independent
hook_engine: false
blocking_capable: false
blocking_events: []
fails_open: n/a
subagent_hooks_inherited: untested
config_path: .aider.conf.yml
config_format: yaml
fidelity: documented
sources:
  - https://aider.chat/docs/config/aider_conf.html
  - https://aider.chat/docs/usage/lint-test.html
  - https://aider.chat/docs/config/options.html
---

# Talk-to: Aider

**Fidelity: documented** - from Aider's official docs (config, lint/test, options); Aider is not yet in ctx's read registry, so this talk-to note leads the read side.

## 1. Identity   (note: not yet in ctx read registry — talk-to leads read here)
- **Harness**: Aider, open-source terminal pair-programming CLI (Paul Gauthier / Aider-AI).
- **ctx provider (read)**: none. Use `aider` as the natural id; frontmatter `ctx_provider: none`.
- **Lineage**: independent. Aider predates and does not share the Claude-Code hook model; it has its own edit/commit loop, not a lifecycle-event engine.

## 2. Hook engine
- **No hook engine, no gate seam.** Aider exposes no PreToolUse-style event that a third party can register a blocking command against. There is no documented way to intercept and DENY an edit before it is written.
- What looks hook-adjacent is **not a gate**: `auto-lint` (default on) and `auto-test` (default off) run `lint-cmd` / `test-cmd` **after** Aider has already edited files. Their output is fed back into the model's next turn for self-correction — a post-hoc feedback loop, not a pre-action allow/deny. A failing lint or test does not roll the edit back by itself.
- Consequence for an integrator: **there is no in-harness seam to block on.** Gating Aider means fencing it from OUTSIDE — a filesystem/exec sandbox, a wrapping process, or CI on the commits it produces. Do not rely on lint/test to stop a bad action; they only report it afterward.

## 3. Config
- **Path**: `.aider.conf.yml`, searched in the home directory, the git repo root, and the current directory (repo/cwd override home). Also configurable via `.env` and CLI flags.
- **Format**: YAML.
- **Knobs that matter**: `auto-commits`, `auto-lint` + `lint-cmd` (per-language `"lang: command"`), `auto-test` + `test-cmd`. These shape behavior but none of them can veto an action pre-emptively.

## 4. Transcript pointer
- **Path pattern**: repo-root `.aider.chat.history.md` (human-readable Markdown transcript) and `.aider.input.history` (prompt input log). Overridable via `chat-history-file` / `input-history-file` (env `AIDER_CHAT_HISTORY_FILE` / `AIDER_INPUT_HISTORY_FILE`).
- The Markdown history is greppable and is the natural read-side input. ctx does not yet cover this harness's read side; this is where a reader would key off.

## 5. Capabilities and caveats
- **Observe: yes, after the fact.** The Markdown chat history plus the git commits Aider makes (`auto-commits`) give a full record to witness.
- **Gate: not in-harness.** No blocking event exists; enforcement has to live in the surrounding environment (sandbox, exec allowlist, pre-receive/CI on commits).
- Because lint/test are corrective-not-preventive, treat any "Aider is gated by its tests" assumption as false for security purposes.
