#!/usr/bin/env python3
"""Generate OVERVIEW.md from the talk-to descriptor frontmatter.

The overview is a derived artifact: every fact in it comes from a
`talk-to/<id>/descriptor.md` frontmatter block, so the matrix can never drift from
the descriptors. Regenerate after editing any descriptor:

    python3 talk-to/gen-overview.py

No dependencies; parses the simple `key: value` frontmatter directly.
"""
import os
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ("harness", "ctx_provider", "vendor", "kind", "lineage", "hook_engine",
          "blocking_capable", "fails_open", "fidelity", "resource_type")


def parse_frontmatter(path):
    fm, inside = {}, False
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            s = line.rstrip("\n")
            if s.strip() == "---":
                if not inside:
                    inside = True
                    continue
                break
            if inside and ":" in s and not s.startswith((" ", "-", "\t")):
                k, _, v = s.partition(":")
                fm[k.strip()] = v.split("#", 1)[0].strip()
    return fm


def gate_class(fm):
    if fm.get("hook_engine") == "true" and fm.get("blocking_capable") == "true":
        return "hook engine"
    if fm.get("blocking_capable") == "true":
        # A being holds no effectors: its gate is built in, not registered and not a static
        # allow-list. Calling that "static policy" would misdescribe it (SCHEMA.md, `kind`).
        return "built-in gate" if fm.get("kind") == "being" else "static policy"
    return "no gate seam"


def fail_cell(fm):
    return {"true": "**open** ⚠", "false": "closed",
            "unknown": "undocumented", "n/a": "—"}.get(fm.get("fails_open", ""), "?")


def res_list(fm):
    """resource_type is a YAML list rendered as a string ('[subscription, api]'); normalize to a
    clean set of tokens for display + counting."""
    raw = fm.get("resource_type", "").strip().strip("[]")
    return [t.strip() for t in raw.split(",") if t.strip()]


def res_cell(fm):
    toks = res_list(fm)
    return ", ".join(toks) if toks else "?"


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, "*", "descriptor.md"))):
        fm = parse_frontmatter(path)
        fm["_id"] = os.path.basename(os.path.dirname(path))
        rows.append(fm)

    n = len(rows)
    hook = [r for r in rows if gate_class(r) == "hook engine"]
    static = [r for r in rows if gate_class(r) == "static policy"]
    none = [r for r in rows if gate_class(r) == "no gate seam"]
    builtin = [r for r in rows if gate_class(r) == "built-in gate"]
    beings = [r for r in rows if r.get("kind") == "being"]
    claude_line = [r for r in rows if r.get("lineage") in ("claude", "canonical")]
    open_ = [r for r in hook if r.get("fails_open") == "true"]
    closed = [r for r in hook if r.get("fails_open") == "false"]
    undoc = [r for r in hook if r.get("fails_open") == "unknown"]
    ahead = [r for r in rows if r.get("ctx_provider") == "none"]
    verified = [r for r in rows if r.get("fidelity") == "verified"]

    out = []
    out.append("# Talk-to coverage overview\n")
    out.append("> **Generated** from each `talk-to/<id>/descriptor.md` frontmatter by "
               "`gen-overview.py`. Do not edit by hand; regenerate after changing a "
               "descriptor. Every cell traces to a descriptor's frontmatter.\n")
    out.append(f"**{n} harnesses.** {len(hook)} expose a hook/plugin gate engine, "
               f"{len(static)} gate only via static policy, {len(none)} have no external "
               f"gate seam (gate them from outside). {len(claude_line)} run Claude Code's "
               f"hook engine (canonical or lineage) — the most-cloned integration surface. "
               f"{len(ahead)} are talk-to ahead of ctx's read side."
               + (f" {len(beings)} {'is a being' if len(beings) == 1 else 'are beings'} rather than a "
                  f"driven harness (`kind: being`); {len(builtin)} of those gate by construction "
                  "— no effectors of their own, every intent judged before dispatch." if beings else "")
               + "\n")
    out.append("**Failure mode across the hook engines is not monolithic** — the load-"
               "bearing fact for anyone building a gate:\n")
    out.append(f"- **fails open** ({len(open_)}): a failed/timed-out blocking hook resolves "
               "to *allow*. The gate must be the fail-closed party itself.")
    out.append(f"- **fails closed** ({len(closed)}): a failed hook *denies* — safer, but a "
               "slow gate can halt the agent.")
    out.append(f"- **undocumented** ({len(undoc)}): the vendor spec omits the error/timeout "
               "behavior. Treat as fail-open until verified.\n")
    out.append(f"Fidelity: {len(verified)} verified (wired against the real harness), "
               f"{len([r for r in rows if r.get('fidelity')=='documented'])} documented "
               f"(from vendor docs), {len([r for r in rows if r.get('fidelity')=='inferred'])} "
               "inferred.\n")

    def rescount(tok):
        return len([r for r in rows if tok in res_list(r)])
    unknown_res = len([r for r in rows if not res_list(r) or res_list(r) == ["unknown"]])
    out.append("**Resource type** — how you pay to run the model, so how freely it can be used "
               "(a harness may offer several):\n")
    out.append(f"- **subscription** ({rescount('subscription')}): usage-limited, seat/plan-covered, "
               "no per-call charge — the safe default for sustained work.")
    out.append(f"- **api** ({rescount('api')}): metered pay-per-token — expensive, use with caution. "
               "Subscription tiers are increasingly a capped skin over the same API backend.")
    out.append(f"- **local** ({rescount('local')}): self-hosted weights, no external billing — cost "
               "is compute.")
    out.append(f"- **free** ({rescount('free')}): free tier, hard rate limits."
               + (f" _{unknown_res} not yet checked (`unknown`)._" if unknown_res else "") + "\n")

    hdr = ("| Harness | id | ctx read | lineage | gate | fails-open | resource | fidelity |\n"
           "|---|---|:--:|---|---|---|---|---|")
    out.append("## Matrix\n")
    out.append(hdr)
    for r in rows:
        read = "—" if r.get("ctx_provider") == "none" else "✓"
        out.append("| {h} | `{i}` | {rd} | {ln} | {g} | {fo} | {rs} | {fi} |".format(
            h=r.get("harness", r["_id"]) + (" _(being)_" if r.get("kind") == "being" else ""), i=r["_id"], rd=read,
            ln=r.get("lineage", "?"), g=gate_class(r), fo=fail_cell(r),
            rs=res_cell(r), fi=r.get("fidelity", "?")))
    out.append("")
    out.append("_ctx read: ✓ = ctx has a read provider for this id; — = talk-to ahead of "
               "read (`ctx_provider: none`)._")

    dest = os.path.join(HERE, "OVERVIEW.md")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"wrote {dest} ({n} harnesses)")


if __name__ == "__main__":
    main()
