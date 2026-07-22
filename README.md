# agent-atlas

**An open dictionary for how any tool can read from, and talk to, any coding agent.**

Every coding-agent harness (Claude Code, Codex, Cursor, Gemini, Kimi, Cline, Goose, and dozens more) stores its session history somewhere, in some format, and exposes some way to hook into it. Today every tool that wants to work across harnesses reverse-engineers each one from its binaries. agent-atlas is a single, versioned, contributable registry that retires that tax, in two halves:

- **Read** - where each harness keeps its transcript, and in what format. How to *observe* what an agent did. This half builds directly on the excellent work already done by [**ctx**](https://github.com/ctxrs/ctx) (its `agent-history-v1` contract and its provider registry across 41 harnesses).
- **Talk-to** - each harness's *integration surface*: its hook system (which events exist, which can **block**, and their failure semantics), its config format, and its capabilities. How to *drive and gate* an agent, not just read its history. This is the half that doesn't exist yet, and it's what agent-atlas adds.

Put the two together and you get the full "how to work with harness X": read what it did, and hook into what it's about to do.

## Why this exists

A tool that only reads is a search box. A tool that can also talk-to can supervise, gate, witness, or extend an agent as it works. The read side has a strong open foundation in ctx; the talk-to side has been redone privately by everyone who needs it. agent-atlas makes the talk-to side a shared, open artifact too, and pins the two halves together per harness.

The whole thing describes the *tools*, never anyone's private work, so there is zero data egress. Privacy-sensitive teams can adopt and contribute freely.

## Layout

```
read/                       # how to read each harness (from ctx, Apache-2.0)
  agent-history-v1/         # ctx's read contract (schema + spec), vendored
  providers.md              # the harness registry: read + talk-to coverage per harness
talk-to/                    # how to drive/gate each harness (this project's contribution)
  SCHEMA.md                 # the integration-surface descriptor schema
  <ctx-provider-id>/        # one directory per harness, named by its ctx id (the join key)
    descriptor.md           # frontmatter (machine-readable facts) + prose descriptor
  claude/descriptor.md
  kimi_code_cli/descriptor.md
```

Each harness directory is named by its **ctx provider id**, so the read side
(`providers.md`) and the talk-to side join on one id with no lookup table. Every
`descriptor.md` opens with YAML frontmatter carrying the load-bearing facts
(`fails_open`, `blocking_events`, `config_path`, `fidelity`, `sources`) so a tool can
consume the registry without parsing prose.

## Coverage today

- **Read: 41 coding-agent harnesses**, inherited from ctx's provider registry. See [`read/providers.md`](read/providers.md).
- **Talk-to: 41 descriptors**, one per harness, each with a `fidelity` mark in its frontmatter:
  - **verified** (2): [`claude`](talk-to/claude/descriptor.md) and [`kimi_code_cli`](talk-to/kimi_code_cli/descriptor.md), derived from live adapters in [hestia](https://github.com/dp-web4/hestia) and exercised in production.
  - **documented / inferred** (the rest): built from each vendor's official docs, cited per fact, not yet wired against the real harness.

The fidelity mark is the honesty knob: a `documented` descriptor is a solid starting point drawn from vendor docs; raising it to `verified` means someone wired it against the real harness and ran it. Both improving a descriptor and lifting its fidelity are documentation tasks, not code ports. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Relationship to ctx

agent-atlas **extends** ctx, it does not fork or replace it. The read side *is* ctx's contract and registry, vendored with attribution under Apache-2.0. The talk-to side is the complementary half. Everything here is Apache-2.0 (matching ctx) on purpose: this is meant to be a standard others adopt, and the license keeps the door open for the talk-to descriptors to be upstreamed into ctx itself if its maintainers want them. Contributions in either direction are welcome.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). The read side is derived from [ctxrs/ctx](https://github.com/ctxrs/ctx) (Apache-2.0); the talk-to side is original work from the [dp-web4](https://github.com/dp-web4) project.

> Web4 note (optional, for those who follow it): this registry is exactly what the [Web4 standard](https://github.com/dp-web4/web4) calls a *dictionary entity*, a living, versioned, fidelity-tracked semantic bridge across domains. You do not need Web4 to use agent-atlas; it is a plain open registry. The formalization is available if useful.
