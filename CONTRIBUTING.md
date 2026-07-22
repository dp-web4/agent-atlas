# Contributing

agent-atlas is a registry; contributions are almost always documentation, not code.

## Add a talk-to descriptor (the common case)

Pick a harness from [`read/providers.md`](read/providers.md) and improve (or create)
`talk-to/<ctx-provider-id>/descriptor.md` against
[`talk-to/SCHEMA.md`](talk-to/SCHEMA.md) — the directory is named by the harness's
ctx provider id (the read-side join key). Fill the YAML frontmatter, answer every
section, and above all state the **failure mode** honestly: whether the hook engine
fails open or fails closed. Mark the descriptor's **fidelity** (`verified` /
`documented` / `inferred`) per its real state, and cite your sources. A descriptor
built from vendor docs is `documented`; it becomes `verified` only once wired against
the real harness and run.

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

By contributing you agree your contribution is licensed under Apache-2.0. Build
descriptors from official vendor documentation where it exists and from observation
where it does not, but **extract the facts and cite the source URL; never paste a
vendor's documentation prose.** Event names, config paths, exit-code conventions, and
fail-open/closed behavior are facts, not copyrightable expression; the vendor's
wording of them is. Write in original prose and link each source. Keep
[NOTICE](NOTICE) accurate if you add material derived from another project.
