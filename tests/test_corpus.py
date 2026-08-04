"""The manifest-driven corpus battery (spec 2026-08-02 §4): for every manifest
document present in corpus/, compile through the PUBLIC document API and assert the
manifest's expected verdict. Absent documents SKIP visibly; the battery never edits
the manifest (verdict discipline — a verdict change is a measured event a loop
records in a reviewed commit). Engine glue is justified PROCEDURAL (§8).

Run locally: ./.venv/bin/python -m pytest -m corpus tests/test_corpus.py -s
"""
import functools
import hashlib
import signal
import time
from pathlib import Path

import pytest
from rdflib import Graph, Namespace, RDF

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "corpus"
COR = Namespace("https://w3id.org/iladub/corpus#")

pytestmark = pytest.mark.corpus

# Wall-clock ceiling per document — test infrastructure, not a tuned semantic
# constant (precedent: tests/etkl/test_derivation_perf.py). Derivation (measured):
# the whole 3-page stem compile cost 180 s at loop-N close
# (tests/test_corpus_stem.py::stem_document) + ~23% headroom. Under the
# fluent-reader invariant (spec §2) a HANG is a harness defect — the alarm turns it
# into a visible failure. R39 (row-group-nesting.rq, ~93 s of that budget) is the
# named perf slice that will lower this. Never raise it to make a document pass:
# report the overrun instead.
BUDGET_S = 222


def manifest_entries(manifest_path):
    """The register, read as the oracle it is: one dict per cor:Document."""
    g = Graph().parse(manifest_path, format="turtle")
    out = []
    for doc in g.subjects(RDF.type, COR.Document):
        def v(p):
            return g.value(doc, p)
        out.append({
            "iri": str(doc),
            "file": str(v(COR.file)),
            "sha256": str(v(COR.sha256)) if v(COR.sha256) is not None else None,
            "verdict": v(COR.expectedVerdict),
            "floor": float(v(COR.scoreFloor)) if v(COR.scoreFloor) is not None else None,
            "contract": str(v(COR.contract)) if v(COR.contract) is not None else None,
            "terms": str(v(COR.terms)) if v(COR.terms) is not None else None,
            "shapes": str(v(COR.shapes)) if v(COR.shapes) is not None else None,
        })
    return sorted(out, key=lambda e: e["file"])


ENTRIES = manifest_entries(REPO / "tests" / "corpus-manifest.ttl")


def require_pinned_edition(entry, corpus_root):
    """Skip (absent / unpinned) or FAIL (edition drift); returns the on-disk path.
    Drift fails rather than skips: measuring an unpinned edition would silently
    decouple the register from the evidence."""
    dest = Path(corpus_root) / entry["file"]
    if not dest.is_file():
        pytest.skip(f"corpus not populated: {entry['file']} (scripts/fetch_corpus.py)")
    if entry["sha256"] is None:
        pytest.skip(f"unpinned edition: {entry['file']} (first fetch, then pin cor:sha256)")
    got = hashlib.sha256(dest.read_bytes()).hexdigest()
    assert got == entry["sha256"], (
        f"{entry['file']}: on-disk edition {got[:12]}… is not the pinned "
        f"{entry['sha256'][:12]}… — refetch, or pin the new edition in a reviewed commit")
    return dest


class _alarm:
    """SIGALRM budget guard (pytest runs us in the main thread)."""

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._fire)
        signal.alarm(BUDGET_S)

    def _fire(self, *_):
        raise AssertionError(
            f"BUDGET EXCEEDED: compile ran past {BUDGET_S}s (R39 family) — "
            f"report the overrun; do not raise the budget")

    def __exit__(self, *_):
        signal.alarm(0)


@functools.lru_cache(maxsize=None)
def _compiled(path: str):
    """One compile per document per session: the stem alone costs ~180 s and the
    grounding test reads the same frozen DocumentReport (loop-M F7 precedent —
    ground_document writes into a caller-supplied graph, never the source)."""
    from iladub.etkl.document import compile_document
    t0 = time.monotonic()
    with _alarm():
        rep = compile_document(path)
    return rep, time.monotonic() - t0


def check_verdict(rep, entry):
    """Assert the manifest's expected verdict against a DocumentReport; returns the
    per-region verdict tuples for the caller's print."""
    verdicts = [(r.kind.name, r.verdict, r.reason)
                for p in rep.pages for r in p.regions]
    if entry["verdict"] == COR.CompilesAbove:
        assert rep.score >= entry["floor"], (
            f"score {rep.score:.4f} < floor {entry['floor']} — do NOT lower the "
            f"floor; report the measured score (Global Constraints)")
        assert any(r.verdict == "asserted"
                   for p in rep.pages for r in p.regions), verdicts
    elif entry["verdict"] == COR.SemanticEscalation:
        assert any(r.verdict == "escalated"
                   for p in rep.pages for r in p.regions), verdicts
    # cor:Unadjudicated: compile returning AT ALL is the gate (never crash, never
    # hang); the printed measurement is adjudication evidence, asserted by no one here.
    return verdicts


@pytest.mark.parametrize("entry", ENTRIES, ids=[e["file"] for e in ENTRIES])
def test_expected_verdict(entry):
    dest = require_pinned_edition(entry, CORPUS)
    rep, dt = _compiled(str(dest))
    verdicts = check_verdict(rep, entry)
    print(f"\n{entry['file']}: score={rep.score:.4f} pages={len(rep.pages)} "
          f"chains={[len(c) for c in rep.chains]} wall={dt:.0f}s")
    if entry["verdict"] == COR.Unadjudicated:
        print(f"  UNADJUDICATED — regions: {verdicts}")


@pytest.mark.parametrize(
    "entry", [e for e in ENTRIES if e["contract"]],
    ids=[e["file"] for e in ENTRIES if e["contract"]])
def test_grounding_where_contracted(entry):
    """Spec §4: '+ grounding where a contract exists'. The §3 invariant is the gate:
    every grounded node behind exactly one accountable promotion."""
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

    ILADUB = Namespace("https://w3id.org/iladub#")
    dest = require_pinned_edition(entry, CORPUS)
    rep, _ = _compiled(str(dest))
    contract = load_contract(str(REPO / entry["contract"]))
    terms = Graph().parse(str(REPO / entry["terms"]), format="turtle")
    shapes = Graph().parse(str(REPO / entry["shapes"]), format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, "https://example.org/shipping#x", 0.1, "n/a",
        "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(rep.graph, contract, abstain, terms, shapes, g)
    grounded = list(g.subjects(RDF.type, ILADUB.GroundedNode))
    print(f"\n{entry['file']}: records={result.records} grounded={len(grounded)} "
          f"still-quarantined={result.proposed}")
    assert grounded, "a contracted document must ground SOMETHING"
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1


def test_corpus_coverage_report():
    """Spec §4: absent documents skip WITH A VISIBLE COUNT — this is the count."""
    present = [e["file"] for e in ENTRIES if (CORPUS / e["file"]).is_file()]
    absent = [e["file"] for e in ENTRIES if not (CORPUS / e["file"]).is_file()]
    print(f"\ncorpus coverage: {len(present)}/{len(ENTRIES)} present; absent: {absent}")
