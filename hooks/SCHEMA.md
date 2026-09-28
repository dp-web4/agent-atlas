# Hooks: who provides a hook, and what it does

`talk-to/` describes **harnesses**: the engines that run hooks (Claude Code, Codex, Kimi…), with
whether a blocking hook fails open. This directory describes **hook providers**: the tools whose
scripts sit IN those engines' hook tables (hestia, snarc, a plugin, a memory service). A tool that
inventories a machine's hooks uses these descriptors to **qualify** each hook it finds, answering
three questions:
- who provided it;
- what role it plays on each event;
- whether it can block an action.

It looks this up instead of guessing from the hook's text.

Added 2026-09-28. hestia's agent-inventory had been deciding ownership by whether a hook's file
mentioned "hestia". So snarc's observe-only PreToolUse handler, whose comment says "(hestia owns
that)", was listed as one of the machine's governance gates.

## Layout

```
hooks/<provider-id>/descriptor.md
```

## Frontmatter (flat on purpose: `key: value`, inline `[a, b]` lists, `- item` lines only)

```yaml
---
provider: snarc                    # matches the directory name
kind: hook-provider
vendor: dp-web4/snarc
match: paths                       # paths | provenance
match_paths: [*/snarc/dist/hooks/handlers/*]   # fnmatch globs against the hook's REAL path
                                   # (and its command, for a hook whose file is gone)
harnesses: [claude]                # talk-to ids whose hook tables it registers in
gate_events: []                    # events on which it can BLOCK (deny / exit 2 / decision)
observe_events: [SessionStart, UserPromptSubmit, PreToolUse, PostToolUse]
can_block: false                   # LOAD-BEARING: can ANY of its hooks deny an action? true | false | unknown
fidelity: verified                 # verified (read from source and exercised) | documented | inferred
---
```

- `match: provenance` means the provider identifies its own files, and a path pattern is not
  trusted. hestia uses this: its hooks are the files its installers declare or its deploy
  records, or byte-identical copies of files it ships. A foreign hook under a directory
  named `hestia` is therefore not hestia's.
- **`unknown` is a value, not a gap.** `can_block: unknown` (and `gate_events: unknown`) says the
  capability has NOT been assessed. A consumer MUST carry it through to its output as unknown,
  never read it as false: knowing WHO provides a hook is not knowing whether it can block. A
  missing `can_block` is read as `unknown`, for the same reason. `false` is only for a provider
  whose hooks were shown not to block (fidelity `documented` or `verified`). Added after GPT's
  review of this PR: claude-flow's body said "not assessed" while its frontmatter said `false`,
  and the consumer, reading only the frontmatter, dropped it from its foreign-gate report.
- A hook on a `gate_events` event of a `can_block: true` provider is a **gate**, whoever provides
  it. A consumer that governs a machine should report a foreign gate, not hide it.
- A hook that matches no provider is **unqualified**, and a consumer reports it as such. It is
  never defaulted to anyone.

The body says how the claims were checked, in the same spirit as `talk-to/`: cite sources, and
state fidelity honestly.
