#!/usr/bin/env python
"""measure_dec_membrane — the reproducible oracle for the decision membrane (O1 and O4).

Spec: docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md
Plan: docs/superpowers/plans/2026-08-10-the-decision-membrane.md (Task 1)

WHAT IT MEASURES.  Every corpus document is compiled (and, where a contract exists,
grounded) and the resulting graph is validated against the two shipped shape files that
carry iladub's differentiator — `vocab/shapes/dec-shapes.ttl` (the deliberation half) and
`vocab/shapes/iladub-shapes.ttl` (the epistemics half) — **parsed separately and reported
separately**, because they are complementary halves and a merged report hides which half
refuses.

WHY BOTH CLOSURES.  Each graph is validated twice:

  SHIPPED = `membrane.subclass_closure` — what `compile._validate` actually does since spec
            2026-08-06 (subclass-only; domain/range typing is gone by design).
  RDFS    = `membrane.rdfs_closure` — what a CONSUMER applying our published axioms sees
            (Fluree, an external reasoner). R69's violation depends on `dec:confidence`'s
            `rdfs:domain` and therefore does NOT fire under SHIPPED. Running only the shipped
            closure would report "conforms" on a live publication defect, which is exactly
            the blindness this loop exists to remove. This differential IS falsifier O4.

HOW THE VERDICT IS READ.  Counts come out of the SHACL **results graph**
(`sh:ValidationResult` / `sh:focusNode` / `sh:resultPath` / `sh:resultMessage`), never by
string-matching the report text. `membrane._conforms_from_report` documents why: a substring
test once flipped a violating graph to "conforming" because the engine echoes offending
literals into `sh:value`.

ENGINE.  pySHACL with `inference="none"`, `advanced=True`, over the closure-expanded graph —
matching `membrane._validate_pyshacl` exactly. This script deliberately does NOT go through
`membrane.validate`: that seam dispatches to rudof where installed and always uses the shipped
closure, and this oracle must pin one engine and run both closures.

Gate classification (CLAUDE.md §8): PROCEDURAL measurement harness. It makes no domain
decision — the decisions are the SHACL shapes, which this script only applies and counts.
Irreducible: compiling a PDF and invoking a validator is engine glue; the arithmetic is
counting, not judgement. No tuned constant, tolerance or threshold appears here.

Usage:
    ./.venv/bin/python scripts/measure_dec_membrane.py --scope compile|grounding|both
    ./.venv/bin/python scripts/measure_dec_membrane.py --scope both --doc cbh-stem

Exit code 0 when every measured scope conforms under both closures, non-zero otherwise —
so it can be used as a gate.

THERE IS NO GRAPH CACHE, DELIBERATELY. The plan offered one (keyed by pdf sha256 + a digest
of `src/**/*.py`) to avoid paying the ~290 s corpus compile on every run. It was built,
MEASURED, and removed, because the round-trip through a serialisation is not verdict-neutral:

    Literal(round(0.3, 2), datatype=XSD.decimal)   # holon.py:374, verbatim
      fresh in memory : .value is a Python float, ill_typed is None  -> pySHACL REFUSES
                        it against dec:ConfidenceShape's sh:datatype xsd:decimal
      after nt/ttl    : .value is a Decimal,      ill_typed is False -> pySHACL ACCEPTS

Same lexical form, same datatype IRI, opposite verdict. Caching the compiled graph therefore
dropped **24 real refusals** from the compile-scope RDFS total (194 -> 170) — one per
escalated candidate — while every other number stayed identical, which is precisely the
regression-hiding failure a cache is supposed to be worth risking. Compile time is the
honest price. Do not re-add a cache without re-measuring this differential.
"""
from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Namespace, RDF
from rdflib.namespace import SH

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "corpus"
COR = Namespace("https://w3id.org/iladub/corpus#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")

ONTOLOGY_FILES = ("dec.ttl", "iladub.ttl", "etkl.ttl", "tab.ttl")
SHAPE_FILES = ("dec-shapes.ttl", "iladub-shapes.ttl")
CLOSURES = ("SHIPPED", "RDFS")


# --------------------------------------------------------------------------- inputs

def manifest_entries():
    """The corpus register, read as the oracle it is (same source as tests/test_corpus.py:38).

    Contract/terms/shapes come from the manifest rather than being hard-coded here, so a
    manifest change cannot silently desynchronise this oracle from the shipped battery.
    """
    g = Graph().parse(REPO / "tests" / "corpus-manifest.ttl", format="turtle")
    out = []
    for doc in g.subjects(RDF.type, COR.Document):
        f = str(g.value(doc, COR.file))
        out.append({
            "file": f,
            "stem": Path(f).stem,
            "sha256": str(g.value(doc, COR.sha256)) if g.value(doc, COR.sha256) else None,
            "contract": str(g.value(doc, COR.contract)) if g.value(doc, COR.contract) else None,
            "terms": str(g.value(doc, COR.terms)) if g.value(doc, COR.terms) else None,
            "shapes": str(g.value(doc, COR.shapes)) if g.value(doc, COR.shapes) else None,
        })
    return sorted(out, key=lambda e: e["stem"])


def load_ontology() -> Graph:
    ont = Graph()
    for f in ONTOLOGY_FILES:
        ont.parse(REPO / "vocab" / "ontology" / f, format="turtle")
    return ont


def load_shapes() -> dict[str, Graph]:
    return {f: Graph().parse(REPO / "vocab" / "shapes" / f, format="turtle")
            for f in SHAPE_FILES}


# --------------------------------------------------------------------------- validation

def _closed(data: Graph, ont: Graph, closure: str) -> Graph:
    from iladub.etkl import membrane
    if closure == "SHIPPED":
        return membrane.subclass_closure(data, ont)
    if closure == "RDFS":
        return membrane.rdfs_closure(data, ont)
    raise ValueError(f"unknown closure {closure!r}")


def validate_one(data: Graph, shapes: Graph, ont: Graph, closure: str) -> dict:
    """(conforms, refusing focus nodes, validation results, refusal breakdown).

    The breakdown is keyed by (sh:resultPath, sh:resultMessage) with a count and one example
    focus node — enough to name WHAT refuses without dumping thousands of results.
    """
    from pyshacl import validate as _v
    conforms, results, _text = _v(_closed(data, ont, closure), shacl_graph=shapes,
                                  inference="none", advanced=True)
    foci = set()
    breakdown: dict[tuple[str, str], list] = defaultdict(lambda: [0, None])
    n_results = 0
    for r in results.subjects(RDF.type, SH.ValidationResult):
        n_results += 1
        focus = results.value(r, SH.focusNode)
        if focus is not None:
            foci.add(focus)
        path = results.value(r, SH.resultPath)
        msg = results.value(r, SH.resultMessage)
        key = (_qname(path), str(msg) if msg is not None else "")
        breakdown[key][0] += 1
        if breakdown[key][1] is None:
            breakdown[key][1] = focus
    return {
        "conforms": bool(conforms),
        "focus_nodes": foci,
        "foci": len(foci),
        "results": n_results,
        "breakdown": dict(breakdown),
    }


_PREFIXES = {
    "https://w3id.org/iladub/dec#": "dec:",
    "https://w3id.org/iladub/etkl#": "etkl:",
    "https://w3id.org/iladub#": "iladub:",
    "https://w3id.org/iladub/tab#": "tab:",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs:",
    "http://www.w3.org/ns/prov#": "prov:",
}


def _qname(term) -> str:
    if term is None:
        return "(node constraint)"
    s = str(term)
    for ns, pfx in _PREFIXES.items():
        if s.startswith(ns):
            return pfx + s[len(ns):]
    return s


# --------------------------------------------------------------------------- graphs

def compiled_graph(entry) -> tuple[Graph, float]:
    """The DocumentReport graph for one corpus document, IN MEMORY. Returns (graph, seconds).

    Never round-tripped through a serialisation — see the module docstring: a round-trip
    normalises `Literal(float, datatype=xsd:decimal)` into a well-typed Decimal and silently
    drops 24 real refusals.
    """
    from iladub.etkl.document import compile_document
    t0 = time.monotonic()
    rep = compile_document(str(CORPUS / entry["file"]))
    return rep.graph, time.monotonic() - t0


def grounded_graph(entry, source: Graph) -> tuple[Graph, object]:
    """Ground a compiled document exactly as tests/test_corpus.py:146-166 does — the same
    abstaining FakeGroundingProposer — so this oracle's numbers and the shipped battery's are
    measurements of the same act. Returns (populated graph, FeedResult)."""
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal
    contract = load_contract(str(REPO / entry["contract"]))
    terms = Graph().parse(str(REPO / entry["terms"]), format="turtle")
    shapes = Graph().parse(str(REPO / entry["shapes"]), format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, "https://example.org/shipping#x", 0.1, "n/a",
        "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(source, contract, abstain, terms, shapes, g)
    return g, result


# --------------------------------------------------------------------------- reporting

def census(g: Graph) -> dict:
    return {
        "triples": len(g),
        "DecisionHolon": len(set(g.subjects(RDF.type, DEC.DecisionHolon))),
        "CandidateConcept": len(set(g.subjects(RDF.type, ILADUB.CandidateConcept))),
        "GroundedNode": len(set(g.subjects(RDF.type, ILADUB.GroundedNode))),
        "PromotionDecision": len(set(g.subjects(RDF.type, ILADUB.PromotionDecision))),
    }


def report_document(label: str, g: Graph, shapes: dict[str, Graph], ont: Graph,
                    extra: str = "") -> dict:
    c = census(g)
    print(f"\n--- {label} ---")
    print(f"    triples={c['triples']}  dec:DecisionHolon={c['DecisionHolon']}  "
          f"iladub:CandidateConcept={c['CandidateConcept']}  "
          f"iladub:GroundedNode={c['GroundedNode']}  "
          f"iladub:PromotionDecision={c['PromotionDecision']}{extra}")
    # Focus nodes are UNIONED across the two shape files WITHIN one document, not summed:
    # under the RDFS closure the SAME candidate refuses under both halves, and counting it
    # twice would report 22 for apple where the spec's §3 table reports 11. The results
    # column is where the two halves add. Across documents the per-document counts are
    # SUMMED, never unioned — see `print_totals`.
    totals = {cl: {"focus_nodes": set(), "results": 0} for cl in CLOSURES}
    for shape_file, sg in shapes.items():
        for cl in CLOSURES:
            v = validate_one(g, sg, ont, cl)
            totals[cl]["focus_nodes"] |= v["focus_nodes"]
            totals[cl]["results"] += v["results"]
            verdict = "conforms" if v["conforms"] else "REFUSES"
            print(f"    {shape_file:<20} {cl:<8} {verdict:<9} "
                  f"foci={v['foci']:<5} results={v['results']}")
            for (path, msg), (n, ex) in sorted(v["breakdown"].items(),
                                               key=lambda kv: -kv[1][0]):
                print(f"        [{n:>4}] {path:<24} :: {msg}")
                print(f"               e.g. {ex}")
    print("    " + "  ".join(
        f"{cl}: {len(totals[cl]['focus_nodes'])} distinct refusing foci / "
        f"{totals[cl]['results']} results" for cl in CLOSURES))
    return totals


def print_totals(title: str, totals: dict, docs: int):
    """Focus nodes: DISTINCT within a document (across the two shape files), SUMMED across
    documents.

    Summing across documents is not a convenience — it is the only correct reading. Each
    document is a separate graph and a separate validation run, so its focus nodes are its
    own. MEASURED (2026-08-10): `compile_document` gives every corpus document the SAME
    default `doc_uri` base, so apple and who-wfa BOTH mint the candidate IRI
    `https://example.org/etkl/doc/p0#region2` — 24 refusing candidates across three
    documents, but only 23 distinct IRIs. A cross-document union silently reports 25 where
    the true count is 26, hiding one real defect behind an accident of default naming.
    """
    print(f"\n{title} ({docs} document{'s' if docs != 1 else ''}; focus nodes DISTINCT "
          f"within a document, SUMMED across documents)")
    print(f"  | {'closure':<8} | {'refusing focus nodes':>20} | {'validation results':>18} |")
    print(f"  |{'-' * 10}|{'-' * 22}|{'-' * 20}|")
    for cl in CLOSURES:
        print(f"  | {cl:<8} | {totals[cl]['foci']:>20} | {totals[cl]['results']:>18} |")


# --------------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--scope", choices=("compile", "grounding", "both"), default="both")
    ap.add_argument("--doc", default=None,
                    help="restrict to corpus documents whose stem contains this substring")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(REPO / "src"))
    ont = load_ontology()
    shapes = load_shapes()
    entries = [e for e in manifest_entries() if (CORPUS / e["file"]).is_file()]
    if args.doc:
        entries = [e for e in entries if args.doc in e["stem"]]
    missing = [e["file"] for e in manifest_entries() if not (CORPUS / e["file"]).is_file()]

    print(f"measure_dec_membrane — engine=pySHACL inference=none advanced=True")
    print(f"  ontology : {' + '.join(ONTOLOGY_FILES)}")
    print(f"  shapes   : {' + '.join(SHAPE_FILES)}  (parsed and reported SEPARATELY)")
    print(f"  closures : SHIPPED=membrane.subclass_closure  RDFS=membrane.rdfs_closure")
    print(f"  documents: {len(entries)} present"
          + (f"; ABSENT (not measured): {missing}" if missing else ""))

    compile_totals = {cl: {"foci": 0, "results": 0} for cl in CLOSURES}
    ground_totals = {cl: {"foci": 0, "results": 0} for cl in CLOSURES}
    n_compiled = n_grounded = 0
    graphs: dict[str, Graph] = {}

    need_compile = args.scope in ("compile", "both")
    need_ground = args.scope in ("grounding", "both")

    if need_compile or need_ground:
        print("\n" + "=" * 78)
        print("COMPILE SCOPE" if need_compile else "COMPILE (for grounding input only)")
        print("=" * 78)
        for e in entries:
            if need_ground and not need_compile and not e["contract"]:
                continue                       # not needed as grounding input
            g, dt = compiled_graph(e)
            graphs[e["stem"]] = g
            if not need_compile:
                print(f"\n--- {e['stem']} --- compiled ({dt:.0f}s), not measured at this scope")
                continue
            t = report_document(e["stem"], g, shapes, ont, extra=f"  wall={dt:.0f}s")
            n_compiled += 1
            for cl in CLOSURES:
                compile_totals[cl]["foci"] += len(t[cl]["focus_nodes"])
                compile_totals[cl]["results"] += t[cl]["results"]
        if need_compile:
            print_totals("COMPILE SCOPE TOTALS", compile_totals, n_compiled)

    if need_ground:
        print("\n" + "=" * 78)
        print("GROUNDING SCOPE")
        print("=" * 78)
        for e in entries:
            if not e["contract"]:
                continue
            gg, res = grounded_graph(e, graphs[e["stem"]])
            t = report_document(e["stem"], gg, shapes, ont,
                                extra=f"  records={res.records} grounded={res.grounded} "
                                      f"quarantined={res.proposed}")
            n_grounded += 1
            for cl in CLOSURES:
                ground_totals[cl]["foci"] += len(t[cl]["focus_nodes"])
                ground_totals[cl]["results"] += t[cl]["results"]
        print_totals("GROUNDING SCOPE TOTALS", ground_totals, n_grounded)

    refusals = sum(compile_totals[cl]["foci"] + ground_totals[cl]["foci"] for cl in CLOSURES)
    print(f"\nVERDICT: {'CONFORMS' if refusals == 0 else 'REFUSES'} "
          f"({refusals} refusing focus nodes summed over every scope and closure)")
    return 0 if refusals == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
