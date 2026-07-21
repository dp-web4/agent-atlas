# agent-history-v1 (vendored from ctx)

This directory is the **read contract**, vendored **unmodified** from
[ctxrs/ctx](https://github.com/ctxrs/ctx) under the Apache License 2.0:

- [`schema.json`](schema.json) — the `agent-history-v1` JSON schema.
- [`README.ctx.md`](README.ctx.md) — ctx's own contract documentation, verbatim.

It is the canonical interface for reading coding-agent history (the `status`,
`init`, `sources`, `importHistory`/`sync`, `search`, `show` operations). ctx is the
authoritative maintainer of this contract; this copy is here so agent-atlas is
self-contained on the read side. If it drifts from ctx, ctx wins; re-vendor from
upstream.

Copyright the ctx authors. See the repository-root [`LICENSE`](../../LICENSE) and
[`NOTICE`](../../NOTICE).
