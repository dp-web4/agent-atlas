# Talk-to descriptor schema

A **talk-to descriptor** documents a harness's integration surface: everything a
tool needs to hook into, drive, or gate the agent as it works, as opposed to the
read side, which is about consuming its transcript after the fact.

One descriptor per harness, as a markdown file in this directory (e.g.
[`kimi.md`](kimi.md)). Prose is fine; what matters is that every section below is
answered, with the failure semantics stated explicitly, because getting those
wrong is how a "blocking" gate silently fails open. Each descriptor should cite
where its facts were verified (a real config, a real run), not a vendor's docs.

## Sections

### 1. Identity
- **Harness**: display name.
- **ctx provider (read)**: the ctx `CaptureProvider` id this pairs with, so the
  read and talk-to halves are pinned together (e.g. `kimi_code_cli`). See
  [`../read/providers.md`](../read/providers.md).
- **Lineage**: if the harness clones another's hook engine (many are Claude Code
  lineage), say so and point at the canonical descriptor. Lineage carries the
  failure semantics with it.

### 2. Hook engine
- **Events**: the full event list the harness fires.
- **Blocking-capable events**: the subset that can *deny/block* an action, and how
  (exit code, decision JSON). Everything else is fire-and-forget.
- **Failure mode (load-bearing)**: what the engine does when a hook times out,
  fails to spawn, exits non-zero-unexpectedly, or throws. State plainly whether it
  **fails open** (resolves to *allow*) or **fails closed** (resolves to *deny*).
  If it fails open, the descriptor must say so in bold: *a gate on this harness has
  to be the fail-closed party itself; it cannot rely on the engine.*

### 3. Config
- **Path**: where the harness reads its hook/config from.
- **Format**: TOML / JSON / etc., and the shape that registers a hook.
- **Knobs that matter**: anything an integrator must set for a stable integration
  (e.g. pinning auto-update off so an audited binary does not drift).

### 4. Transcript pointer
- **Path pattern**: where the session transcript is written (this is also the read
  side's input; naming it here closes the loop).
- **Notable fields**: anything that changes how you integrate (e.g. the prompt
  lives in the transcript, so prompt capture reads the file rather than a hook).

### 5. Capabilities and caveats
- What you can and cannot do through the surface, and any harness-specific gotcha
  (including cases where the harness's own self-model is wrong about its hooks).

## Fidelity

Mark each descriptor's fidelity honestly, so a consumer knows how far to trust it:

- **verified** — wired against the real harness and exercised.
- **documented** — from the harness's own docs, not yet run.
- **inferred** — reverse-engineered, unconfirmed.

A descriptor that has never touched the real harness is `inferred` until it has.
