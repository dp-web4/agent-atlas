---
harness: SAGE
ctx_provider: none
vendor: dp-web4 (SAGE fleet)
kind: being
lineage: independent
hook_engine: false
blocking_capable: true
blocking_events: [intent]
fails_open: false
subagent_hooks_inherited: untested
subagent_attribution: n/a
config_path: none (the seat's hestia projection + an identity file; see 3)
config_format: n/a
resource_type: [local]
fidelity: documented
sources:
  - https://github.com/dp-web4/SAGE/blob/main/sage/gateway/being_gate_client.py
  - https://github.com/dp-web4/SAGE/blob/main/sage/gateway/heartbeat.py
  - https://github.com/dp-web4/SAGE/blob/main/sage/gateway/hestia_dispatch.py
  - https://github.com/dp-web4/SAGE/blob/main/sage/gateway/governed_turn.py
  - https://github.com/dp-web4/SAGE/blob/main/sage/gateway/BEING_POSTURE.md
  - https://github.com/dp-web4/hestia/tree/main/plugins/_shared
---

# Talk-to: SAGE

**Fidelity: documented** - written from SAGE's own source, by a seat (McNugget) whose
being has not been provisioned yet, so nothing here was exercised by its author. Three
fleet seats run beings this way; one of them should raise this to `verified` or correct it.

SAGE is the first entry of **`kind: being`** (see `SCHEMA.md`). Everything else in this
registry is a harness a person drives: a session opens, a human asks, the agent acts. A
SAGE being is a locally hosted model with a persistent identity, its own memory, and a
heartbeat that wakes it to look for work without anyone asking. From a governance point
of view it is **a harness like any other** - it has an id, its acts are judged by the same
law, and they land in the same witness chain. The `kind` tag records provenance, and for
now nothing keys off it.

## 1. Identity
- **Harness / vendor**: [SAGE](https://github.com/dp-web4/SAGE), dp-web4. Two parts matter
  here: a Rust daemon (`sage-daemon`) that hosts the being's cognition loop and serves a
  local HTTP surface, and a Python gateway (`sage/gateway/`) through which the being acts
  on anything outside itself.
- **ctx provider (read)**: none. Talk-to ahead of read.
- **Lineage**: **independent.** It clones nobody's hook engine, because it does not have
  one (see 2).
- **Governance id**: by fleet convention a being connects as `<machine>-being`
  (`legion-being`, `cbp-being`), one per machine, **not** as `sage`. An inventory that maps
  this descriptor to a single plugin id will be wrong; the id is per-seat.

## 2. Hook engine
**There is none, and that is the design rather than a gap.** A hook engine is a seam where
a third party registers code that the harness calls before it acts, and the safety of the
arrangement depends on the harness calling it and honouring the answer. SAGE inverts this:
**the being holds no effectors at all.** It emits an *intent*; a gate client normalizes the
intent into the same event shape every other governed harness produces, asks hestia's
shared gate law for a verdict, and only on *allow* hands the intent to a dispatcher that
executes and witnesses it. There is no path from the model to an effect that does not pass
through that client, so there is nothing to register and nothing to forget to register.

- **Events**: one - `intent`. Each is an entry from a **bounded registry** of effectors:
  asking a peer, waking another member over the mesh, witnessing a note, reading and
  writing its own memory, long-term recall and remember, advisory PR review, read-only git
  history and search, running a check in its own worktree, sealed channel egress, replying
  in a conversation, requesting scope, and appealing a refusal. No shell and no raw
  filesystem. The bound is enforced twice: the client will not emit an intent outside the
  registry, and the gate denies one if it arrives anyway.
- **Blocking-capable events**: all of them. Every intent is judged before dispatch.
- **Failure mode (load-bearing)**: **fails closed.** If the shared law cannot be imported,
  every effector is denied (`gate.unreachable`). If the second stage - a round trip to the
  hestia daemon for society-level safety - is unavailable or errors, *consequential*
  effectors hard-deny; only *observational* ones (witness, reading own memory, recall)
  pass, on the reasoning that they have no external effect and that witnessing is itself
  the accountability primitive. A being that cannot reach the law is stopped, never
  ungoverned. The cost is the one every fail-closed surface pays: a broken gate path halts
  the being. One such halt was a path-resolution problem that read as a broken gate, so the
  client now resolves the *installed* law the deploy maintains before a source checkout.
- **A refusal is an answer, not an error.** A deny returns to the being with the rule and
  the reason, and carries the witness hash of the refusal. The being may `request_scope`
  (an operator decides) or `appeal` using that hash.
- **`subagent_hooks_inherited`: untested**, and the question has an unusual shape here. The
  registry has no effector that spawns a sub-agent. What a being *can* do is wake another
  member (`peer_ask`, `mesh`); that member acts under **its own** identity and its own gate,
  not the asker's. Nobody has probed whether that holds end to end, so this stays
  `untested` rather than being argued into `verified-inherited`.

## 3. Config
- **Path**: there is no hook config file to write. Two things configure a being's gate:
  the **identity file** in its instance directory (the client roots the being's memory at
  that directory), and the **seat projection** hestia publishes for the being's plugin id
  under `$HESTIA_HOME/seats/`, from which the client reads where the shared law is
  installed (`HESTIA_SHARED_DIR`, `HESTIA_HOME`; `HESTIA_GATE_SHARED` overrides).
- **How it is launched**: the heartbeat is a module entry point,
  `python3 -m sage.gateway.heartbeat --member <machine>-being --model <model> --instance <dir>`,
  run on a timer by the host's service manager. `--gate-only` exercises the gate path
  without a model turn.
- **Knobs that matter**: the being must be a **registered member** before its first beat -
  minted, joined, relayed and admitted by an operator. An unregistered id is not a
  harmless default: hestia answers an unknown plugin id with a well-formed empty snapshot,
  which reads as "no grants" rather than "no such member".
- **Detection on disk** (for an inventory): a `sage-daemon` executable, and a SAGE checkout
  containing `sage/gateway/being_gate_client.py`. The daemon listening on its local port is
  evidence the *cognition loop* is up; it is **not** evidence the being is governed. That
  is established only by the heartbeat unit existing and the member being registered.

## 4. Transcript pointer
- **Path pattern**: `<instance>/heartbeats.jsonl`, one record per beat, plus the being's own
  `journal.md` and `todo.md` in the same directory. New instance directories are private to
  the machine (gitignored in SAGE, mirrored to a private repository); older ones are public
  history.
- **Notable fields**: a beat ends with a reflection turn written in the being's own words.
  The authoritative record of what it *did* is hestia's witness chain, not this file: the
  transcript says what the model said, the chain says what was allowed and executed.

## 5. Capabilities and caveats
- **You do not integrate with SAGE by adding a hook.** To govern a being, register it as a
  member and let its gate client find the installed law. To observe one, read the chain.
- **Presentation varies by model, the gate does not.** Small models that narrate instead of
  acting when the posture text precedes the ask are given the same words in a different
  order. That is a prompt-ordering difference upstream of the gate; every resulting intent
  is judged identically.
- **Embodiment is declared, not yet enforced.** A being is meant to be bound to its
  hardware. The plumbing for that does not exist yet, which is why `kind: being` is
  provenance today and not a policy input.
- **The daemon has no `--version`.** Executing `sage-daemon` with any argument starts a
  daemon. Read its build from the `/health` endpoint of a running one, or from the binary's
  embedded strings; do not run it to ask.
