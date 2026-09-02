"""Corpus REACH — how much of src/iladub any corpus document actually executes.

WHY THIS EXISTS (R158). A loop that changes a function and reports "the other six
documents are byte-identical, therefore nothing regressed" is asserting nothing at
all if those documents never call the function. That has now happened twice with
published evidence (R45's five vacuous PASS rows; PR #109's inert 27-page zero
delta), and each time the probe that caught it was bespoke prose inside the loop
that needed it — `grep -rl 'reach probe' src/ scripts/ tests/` returned nothing.
This is that probe, committed, so a later loop re-runs it instead of rewriting it.

WHAT IT MEASURES. One cProfile'd `compile_document` per corpus document — plus a
profiled `ground_document` for the two documents carrying a cor:contract, because
the corpus battery has both legs — yields per-function call counts for every
function in src/iladub in a SINGLE pass. Reach for any function is then a lookup,
not another run.

WHAT A ZERO MEANS, EXACTLY. cProfile records a function only when it is CALLED, so
an absent entry means "never called by this document", NOT "never imported" and NOT
"dead code". A function reached by 0 of 7 documents may be exercised by unit tests,
by the CLI, or by no one; this instrument does not distinguish those, and a reader
who treats zero reach as dead code is overreading it. R146's rule applies: absence
of reach is not evidence of absence of purpose.

CLASSIFICATION (CLAUDE.md §8): PROCEDURAL, and irreducible. It measures which code
executed — an observation about a process, not a judgement over an evidence graph.
There is nothing here for SPARQL to derive or SHACL to constrain: no AXIOM form can
observe a Python call, and nothing is being read or proposed, so it is not NEURAL.
It carries no tuned constant.

USAGE
    ./.venv/bin/python scripts/reach_probe.py run    --out /tmp/reach   [--doc FILE]
    ./.venv/bin/python scripts/reach_probe.py report --out /tmp/reach   [NAME ...]

`run` is minutes per document (2.1x measured overhead: graincorp-capacity 12.0s ->
25.7s), so it writes a JSON cache `report` reads. Run it once, report many times.
NAME is a bare function name, optionally `file.py:name` when a name is defined in
more than one module (`_emit_candidate` is, in two).
"""
import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = str(REPO / "src" / "iladub")
COR = "https://w3id.org/iladub/corpus#"

# Short names for the table's columns; the manifest's file stem is unreadable at
# width. Any document absent from this map falls back to its stem.
SHORT = {
    "graincorp-stem-2026-07-31": "gstem", "graincorp-capacity-2026-08-04": "gcap",
    "cbh-stem-2026-08-03": "cbh", "ons-index-of-services-2026-02": "ons",
    "bfs-population-bilan-2023": "bfs", "apple-fy2026q3-statements": "apple",
    "who-wfa-boys-zscore-0-5": "who",
}


def manifest():
    """The corpus register, read as the oracle it already is (tests/test_corpus.py
    reads the same file for the same reason)."""
    from rdflib import Graph, Namespace, RDF
    g = Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle")
    ns = Namespace(COR)
    out = []
    for doc in g.subjects(RDF.type, ns.Document):
        def v(p):
            x = g.value(doc, p)
            return None if x is None else str(x)
        out.append({"file": v(ns.file), "contract": v(ns.contract),
                    "terms": v(ns.terms), "shapes": v(ns.shapes)})
    return sorted(out, key=lambda e: e["file"])


def _counts(profile):
    import pstats
    out = {}
    for (fn, _lineno, name), (_cc, nc, _tt, _ct, _cal) in pstats.Stats(profile).stats.items():
        if fn.startswith(SRC):
            out[f"{Path(fn).relative_to(REPO)}:{name}"] = nc
    return out


def run_one(entry, out_dir):
    """Both legs of the corpus battery, profiled: compile always, grounding where a
    contract exists. The two legs are summed — reach is 'does this document execute
    it', and the battery runs both on every contracted document.

    ONE DOCUMENT PER PROCESS, and this is load-bearing rather than tidy — measured,
    because the first version of this script compiled all seven in one process and
    reported `_build_membrane` at 1/7 instead of 7/7. It is `functools.lru_cache`d:
    document one pays the call, documents two through seven are served the cache and
    cProfile records nothing for them. Any memoized or run-once function reads as
    reached by exactly one document — whichever the loop happened to visit first —
    so a shared process makes the instrument silently understate reach for the whole
    class. `run` therefore re-invokes this module per document (see `main`)."""
    import cProfile
    sys.path.insert(0, str(REPO / "src"))
    from iladub.etkl.document import compile_document

    pdf = REPO / "corpus" / entry["file"]
    if not pdf.is_file():
        print(f"SKIP (not populated): {entry['file']}")
        return
    stem = Path(entry["file"]).stem
    t0 = time.monotonic()
    pr = cProfile.Profile()
    pr.enable()
    rep = compile_document(str(pdf))
    pr.disable()
    calls = _counts(pr)
    legs = ["compile"]

    if entry["contract"]:
        from rdflib import Graph
        from iladub.feed import ground_document
        from iladub.ground import load_contract
        from iladub.propose_ground import FakeGroundingProposer, GroundingProposal
        abstain = FakeGroundingProposer(GroundingProposal(
            None, "https://example.org/shipping#x", 0.1, "n/a",
            "urn:iladub:suggester/fake"))
        pr2 = cProfile.Profile()
        pr2.enable()
        ground_document(rep.graph, load_contract(str(REPO / entry["contract"])), abstain,
                        Graph().parse(str(REPO / entry["terms"]), format="turtle"),
                        Graph().parse(str(REPO / entry["shapes"]), format="turtle"),
                        Graph(), validate_shapes=True)
        pr2.disable()
        for k, v in _counts(pr2).items():
            calls[k] = calls.get(k, 0) + v
        legs.append("grounding")

    dt = time.monotonic() - t0
    dest = Path(out_dir) / f"{stem}.json"
    dest.write_text(json.dumps({"file": entry["file"], "short": SHORT.get(stem, stem),
                                "legs": legs, "wall": dt, "score": rep.score,
                                "calls": calls}, indent=1))
    print(f"{SHORT.get(stem, stem):>6}: score={rep.score:.4f} wall={dt:.0f}s "
          f"legs={'+'.join(legs)} funcs={len(calls)} -> {dest}")


def load(out_dir):
    docs = {}
    for f in sorted(Path(out_dir).glob("*.json")):
        j = json.loads(f.read_text())
        docs[j["short"]] = j
    order = [s for s in SHORT.values() if s in docs] + \
            [s for s in docs if s not in SHORT.values()]
    return docs, order


def report(out_dir, names):
    docs, order = load(out_dir)
    if not docs:
        sys.exit(f"no cache in {out_dir} — run `reach_probe.py run --out {out_dir}` first")
    n = len(order)
    print(f"corpus reach — {n} document(s): " +
          ", ".join(f"{d} ({'+'.join(docs[d]['legs'])}, score {docs[d]['score']:.4f})"
                    for d in order) + "\n")
    allk = set()
    for d in order:
        allk |= set(docs[d]["calls"])

    if names:
        w = max(len(x) for x in names) + 2
        hdr = f"{'defining file':<22} {'function':<{w}} " + \
              " ".join(f"{d:>6}" for d in order) + "  reach"
        print(hdr)
        print("-" * len(hdr))
        for name in names:
            hits = sorted(k for k in allk
                          if k.rsplit(":", 1)[1] == name.rsplit(":", 1)[-1]
                          and (":" not in name or k.rsplit(":", 1)[0].endswith(name.rsplit(":", 1)[0])))
            if not hits:
                print(f"{'--':<22} {name:<{w}} " + " ".join(f"{'--':>6}" for _ in order) +
                      "    0/%d  NEVER CALLED (see module docstring: not 'dead')" % n)
                continue
            for k in hits:
                c = [docs[d]["calls"].get(k, 0) for d in order]
                mod = k.rsplit(":", 1)[0].replace("src/iladub/", "")
                print(f"{mod:<22} {name.rsplit(':', 1)[-1]:<{w}} " +
                      " ".join(f"{x:>6}" for x in c) +
                      f"   {sum(1 for x in c if x)}/{n}")
        print()

    dist = Counter(sum(1 for d in order if docs[d]["calls"].get(k, 0)) for k in allk)
    print(f"CORPUS-WIDE, over {len(allk)} src/iladub functions called at least once:")
    for k in sorted(dist):
        print(f"  reached by {k}/{n} documents: {dist[k]:>4}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("--out", required=True)
    r.add_argument("--doc", help="manifest cor:file of a single document")
    o = sub.add_parser("_one"); o.add_argument("--out", required=True)
    o.add_argument("--doc", required=True)
    p = sub.add_parser("report"); p.add_argument("--out", required=True)
    p.add_argument("names", nargs="*")
    a = ap.parse_args()
    if a.cmd == "_one":
        [e] = [e for e in manifest() if e["file"] == a.doc]
        run_one(e, a.out)
    elif a.cmd == "run":
        Path(a.out).mkdir(parents=True, exist_ok=True)
        for e in manifest():
            if a.doc and e["file"] != a.doc:
                continue
            # A FRESH interpreter per document — see run_one's docstring.
            subprocess.run([sys.executable, __file__, "_one",
                            "--out", a.out, "--doc", e["file"]], check=True)
    else:
        report(a.out, a.names)


if __name__ == "__main__":
    main()
