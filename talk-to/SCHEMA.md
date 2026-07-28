# Talk-to descriptor schema

A **talk-to descriptor** documents a harness's integration surface: everything a
tool needs to hook into, drive, or gate the agent as it works, as opposed to the
read side, which is about consuming its transcript after the fact.

## Layout: one directory per harness

Each harness gets a directory named by its **ctx provider id** (the read-side
identifier, so the two halves join on the same key):

```
talk-to/
  <ctx_provider_id>/
    descriptor.md      # this schema
  claude/descriptor.md
  kimi_code_cli/descriptor.md
```

Naming the directory after the ctx provider id means a tool can pair the read and
talk-to halves of a harness by a single id, with no lookup table. The directory
also leaves room to grow later (a `examples/` with a sample hook config, a vendored
config template) without moving anything.

**Talk-to ahead of read.** Some harnesses have an integration surface worth
describing but are not yet in ctx's read registry. Give those a natural id for the
directory (e.g. `aider`, `amp`) and set `ctx_provider: none` in frontmatter. When ctx
later adds a read provider for the harness, rename the directory to the ctx id so the
two halves rejoin. These are listed in a separate section of
[`../read/providers.md`](../read/providers.md).

## Frontmatter (required): the machine-readable facts

Every `descriptor.md` opens with a YAML frontmatter block carrying the load-bearing
facts, so a tool can consume the registry without parsing prose. The single most
important field is `fails_open`: whether a blocking hook that errors resolves to
*allow*. Getting that wrong is how a "blocking" gate silently fails open.

```yaml
---
harness: Claude Code             # display name
ctx_provider: claude             # matches the directory name and read/providers.md
vendor: Anthropic
lineage: canonical               # canonical | <ctx_provider_id it clones> | independent
hook_engine: true                # does it expose ANY hook/plugin/gate surface?
blocking_capable: true           # can any event deny/block an action?
blocking_events: [PreToolUse, UserPromptSubmit, Stop]
fails_open: true                 # LOAD-BEARING: does a failed blocking hook resolve to allow? (true|false|unknown|n/a — n/a when hook_engine is false)
config_path: ~/.claude/settings.json
config_format: json              # json | toml | yaml | ...
resource_type: [subscription, api]  # access/cost profile(s) the model runs under (list; a harness can offer several)
fidelity: verified               # verified | documented | inferred
sources:
  - https://docs.anthropic.com/en/docs/claude-code/hooks
---
```

If a harness exposes no integration surface at all (a pure autocomplete plugin, a
closed cloud IDE), say so honestly: `hook_engine: false`, `blocking_capable: false`,
and a one-line prose note on why. Recorded absence is a real finding, not a gap.

### `resource_type`: the access/cost profile (list)

How you pay to run the harness's model determines how freely a governed member (or
an operator) can use it, so it is a first-class fact, not a footnote. It is a **list**
because one harness often offers more than one path (gemini-cli runs under a Code
Assist subscription *or* a metered API key), and the vocabulary is:

- **`subscription`** — covered by a seat/plan; **usage-limited** but no per-call
  charge (Claude Max, Gemini Code Assist, a ChatGPT/Codex plan). The safe default for
  sustained work: a hard cap, not a running meter.
- **`api`** — **metered pay-per-token**: expensive, use with caution, may or may not
  be usage-limited (Anthropic/OpenAI/Gemini API keys, Vertex AI). Note the
  convergence: subscription tiers are increasingly a usage-limited *skin* over the
  same API backend (gemini's Code Assist routes through `cloudcode-pa.googleapis.com`),
  so "subscription" means *capped*, not *free of the API*.
- **`free`** — a free tier: no payment, **hard rate limits** (a free API key, a free
  CLI tier). Fine for a shakedown, throttled for real work.
- **`local`** — self-hosted model weights, **no external billing** (ollama /
  llama.cpp behind the harness). Cost is compute, not per-token.

Use `[unknown]` when the access model has not been checked yet — an honest gap, like
`fails_open: unknown`.

## Prose sections

Below the frontmatter, answer each section. Prose is fine; state the failure
semantics explicitly.

### 1. Identity
- **Harness / vendor**: display name and who ships it.
- **ctx provider (read)**: the ctx `CaptureProvider` id this pairs with (also the
  directory name). See [`../../read/providers.md`](../../read/providers.md).
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
  If it fails open, say so in bold: *a gate on this harness has to be the
  fail-closed party itself; it cannot rely on the engine.*
- **`subagent_hooks_inherited`** (load-bearing): whether tool calls made by a
  SUB-AGENT / spawned sub-session fire the same hooks as the main loop. If they do
  not, `"spawn a subagent to do it"` is a one-step gate bypass that needs no
  cleverness at all, and any gate on the harness is worth much less than it looks.
  Values:
  `verified-inherited` (measured: a sub-agent call was denied AND witnessed),
  `verified-not-inherited` (measured: it was not),
  `untested` (**the default — nobody has looked**).
  `untested` is not a synonym for safe. It is the honest statement that the most
  consequential question about a harness's gate is open, and it must stay `untested`
  until someone has actually run a sub-agent probe against that harness.
- **`subagent_attribution`**: whose identity a sub-agent's actions are recorded
  under. `parent` means the record cannot distinguish main-loop from sub-agent
  action — enforcement can be intact while accountability granularity is not.

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

### Sources
- The `sources:` **frontmatter** list is the canonical citation surface (required):
  every fact traces to a link there. Cite official vendor docs where they exist. A
  prose `## Sources` section at the end is optional and encouraged when it helps to
  annotate what each link establishes.

## Fidelity

Mark each descriptor's fidelity honestly, so a consumer knows how far to trust it:

- **verified** - wired against the real harness and exercised.
- **documented** - from the harness's own official docs, not yet run.
- **inferred** - reverse-engineered or pieced together from indirect sources,
  unconfirmed.

A descriptor that has never touched the real harness is at most `documented`.

## Sourcing and licenses

Descriptors are built from official vendor documentation where it exists, and from
observation where it does not. **Extract the facts and cite the source URL; never
paste a vendor's documentation prose.** An event list, a config path, an exit-code
convention, and a fail-open/closed behavior are facts, not copyrightable expression;
the vendor's wording of them is. Write the descriptor in original prose, link the
doc you drew each fact from, and keep [`../NOTICE`](../NOTICE) accurate if any file
incorporates material under another project's license.
