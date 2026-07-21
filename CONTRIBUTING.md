# Contributing

agent-atlas is a registry; contributions are almost always documentation, not code.

## Add a talk-to descriptor (the common case)

Pick a harness from [`read/providers.md`](read/providers.md) whose talk-to column
is ` - `, and write `talk-to/<harness>.md` against
[`talk-to/SCHEMA.md`](talk-to/SCHEMA.md). Answer every section, and above all state
the **failure mode** honestly: whether the hook engine fails open or fails closed.
Mark the descriptor's **fidelity** (`verified` / `documented` / `inferred`) per its
real state, and cite where you checked. A descriptor that has never touched the
real harness is `inferred` until it has.

If the harness clones another's hook engine (many clone Claude Code's), a thin
descriptor that points at the canonical one and notes the config path and any
divergence is enough.

## Add or update read coverage

The read side is inherited from [ctx](https://github.com/ctxrs/ctx). If ctx adds or
changes a provider, re-sync [`read/providers.md`](read/providers.md) from ctx's
`CaptureProvider` registry rather than editing entries by hand, and keep the
attribution intact.

## Upstreaming to ctx

This project is Apache-2.0 on purpose, matching ctx, so talk-to descriptors can be
contributed *into* ctx if its maintainers want the integration surface to live
alongside the read side. If you are a ctx maintainer reading this: the talk-to half
is yours to adopt. Open an issue and let's coordinate.

## Provenance and license

By contributing you agree your contribution is licensed under Apache-2.0. Do not
paste a vendor's proprietary docs; describe the integration surface from
observation, the way the seed descriptors do. Keep [NOTICE](NOTICE) accurate if you
add material derived from another project.
