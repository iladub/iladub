"""The corpus register's membrane (spec 2026-08-02 §4): the tracked manifest conforms
to tests/corpus-shapes.ttl. Always-on — the register is tracked; no network, no corpus/.
Closed-world constraint side of the §8 split: the membrane validates what may enter the
battery; it derives nothing."""
import json
import subprocess
from pathlib import Path

from pyshacl import validate
from rdflib import RDF, Graph, Namespace, URIRef
from rdflib.namespace import SH

from tests.corpus_firings import lift_firings, lift_snapshots
from tests.test_corpus_firings import _commit, _git, _publish, _repo

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tests" / "corpus-manifest.ttl"
SHAPES = REPO / "tests" / "corpus-shapes.ttl"
BASELINE = REPO / "tests" / "corpus-baseline"
BFS = "urn:iladub:corpus:bfs-population-bilan-2023"
ONS = "urn:iladub:corpus:ons-index-of-services-2026-02"

PREFIXES = """@prefix cor: <https://w3id.org/iladub/corpus#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

BASE = ('<urn:x> a cor:Document ; cor:file "f.pdf" ; cor:url "https://example.org/f" ; '
        'cor:series "s" ')


def _conforms(data: Graph):
    ok, _, report = validate(
        data, shacl_graph=Graph().parse(SHAPES, format="turtle"),
        inference="rdfs", advanced=True)
    return ok, report


def _neg(ttl: str):
    ok, report = _conforms(Graph().parse(data=PREFIXES + ttl, format="turtle"))
    assert not ok, f"membrane failed to refuse:\n{ttl}"


def test_manifest_conforms():
    """The manifest is validated TOGETHER with the firings lifted from the committed baseline
    (R259 task 3): cor:DisposalShape joins an authored cor:disposes to a lifted cor:firing, so
    validating the manifest alone would refuse the first real disposal."""
    g = Graph().parse(MANIFEST, format="turtle")
    g += lift_firings(g, BASELINE)
    g += lift_snapshots(g)
    ok, report = _conforms(g)
    assert ok, report


def test_refuses_compilesabove_without_floor():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:CompilesAbove ; '
         'cor:sha256 "%s" ; cor:adjudication [ cor:by "x" ] .' % ("0" * 64))


def test_refuses_unknown_family():
    _neg(BASE + '; cor:family "crypto" ; cor:expectedVerdict cor:Unadjudicated .')


def test_refuses_adjudicated_verdict_without_pin():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:SemanticEscalation ; '
         'cor:ambiguity "which header row" ; cor:adjudication [ cor:by "x" ] .')


def test_refuses_escalation_without_named_ambiguity():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:SemanticEscalation ; '
         'cor:sha256 "%s" ; cor:adjudication [ cor:by "x" ] .' % ("0" * 64))


def test_refuses_partial_contract_triple():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
         'cor:contract "examples/x.ttl" .')


def test_refuses_malformed_sha256():
    _neg(BASE + '; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
         'cor:sha256 "not-a-hash" .')


# A reading is the register's machine-readable measurement (vocab/internal/corpus.ttl
# § Readings). These three refusals are what make a row traceable rather than merely
# present: an undated value is not evidence of anything, and a value with neither a
# commit nor a path is a number nobody can check.

READING = ('<urn:x> a cor:Document ; cor:file "f.pdf" ; cor:url "https://example.org/f" ; '
           'cor:series "s" ; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
           'cor:reading [ a cor:Reading ; %s ] .')


def test_refuses_reading_without_a_date():
    _neg(READING % ('cor:value "0.5"^^xsd:decimal ; cor:recordedIn "docs/x.md"'))


def test_refuses_reading_without_a_value():
    _neg(READING % ('cor:readAt "2026-09-08"^^xsd:date ; cor:recordedIn "docs/x.md"'))


def test_refuses_untraceable_reading():
    """No commit and no path: the value cannot be checked, only believed."""
    _neg(READING % ('cor:value "0.5"^^xsd:decimal ; cor:readAt "2026-09-08"^^xsd:date'))


FIRING = ('<urn:x> a cor:Document ; cor:file "f.pdf" ; cor:url "https://example.org/f" ; '
          'cor:series "s" ; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ; '
          'cor:firing [ %s ] .')
OK_FIRING = ('cor:reason "KIND_NOT_SUPPORTED" ; cor:live "3"^^xsd:nonNegativeInteger ; '
             'cor:superseded "0"^^xsd:nonNegativeInteger ; '
             'cor:recordedIn "tests/corpus-baseline/f.json"')


def test_admits_a_well_formed_firing():
    ok, report = _conforms(Graph().parse(data=PREFIXES + FIRING % OK_FIRING, format="turtle"))
    assert ok, report


def test_refuses_firing_without_live_count():
    _neg(FIRING % OK_FIRING.replace('cor:live "3"^^xsd:nonNegativeInteger ; ', ''))


def test_refuses_firing_with_a_negative_count():
    _neg(FIRING % OK_FIRING.replace('"0"^^xsd:nonNegativeInteger', '"-1"^^xsd:integer'))


def test_refuses_firing_with_two_reasons():
    _neg(FIRING % (OK_FIRING + ' ; cor:reason "DATAGRID_RESIDUE"'))


def test_refuses_untraceable_firing():
    _neg(FIRING % OK_FIRING.replace(' ; cor:recordedIn "tests/corpus-baseline/f.json"', ''))


# D2 (spec 2026-09-18 § 3 as strengthened by § 8; rewritten by spec 2026-10-19 § 4.4, R323): a
# disposal is judged against its OWN dated, durable snapshot of the baseline, never the current one.
# The negatives inject into the REAL manifest's bfs / ons documents, with the REAL lifted firings.
COR = Namespace("https://w3id.org/iladub/corpus#")
M1 = "cor:disposes without exactly one cor:judgedAgainst snapshot"
M2 = "cor:judgedAgainst names a snapshot of a different document than the one holding this adjudication"
M3 = "cor:judgedAgainst names a snapshot that is not durable on main"
M4 = ("cor:disposes names a reason with no LIVE cor:firing in the snapshot this adjudication "
      "was judged against")


def _d2_refusals(g: Graph) -> set[str]:
    """The sh:resultMessage of every result whose source shape is cor:DisposalShape or one of its
    sh:property shapes: WHICH constraint refused, not merely that something did."""
    shapes = Graph().parse(SHAPES, format="turtle")
    D = COR.DisposalShape
    own = {D, *shapes.objects(D, SH.property)}
    _, rg, _ = validate(g, shacl_graph=shapes, inference="rdfs", advanced=True)
    return {str(m) for r in rg.subjects(RDF.type, SH.ValidationResult)
            if rg.value(r, SH.sourceShape) in own for m in rg.objects(r, SH.resultMessage)}


def _baseline_path(doc_iri: str) -> str:
    g = Graph().parse(MANIFEST, format="turtle")
    pdf = "corpus/" + str(g.value(URIRef(doc_iri), COR.file))
    for p in sorted(BASELINE.glob("*.json")):
        if json.loads(p.read_text()).get("pdf") == pdf:
            return p.relative_to(REPO).as_posix()
    raise AssertionError(f"no baseline file for {doc_iri}")


def _with_disposal(doc_iri: str, reason: str, snapshot_of: str | None = None) -> Graph:
    """The real manifest plus an injected disposal judged against a durable snapshot of
    `snapshot_of or doc_iri`'s baseline file at HEAD's blob. The lifts run AFTER the injection:
    the injected judgedAgainst node does not exist before it."""
    path = _baseline_path(snapshot_of or doc_iri)
    blob = subprocess.run(["git", "-C", str(REPO), "rev-parse", f"HEAD:{path}"], check=True,
                          capture_output=True, text=True).stdout.strip()
    g = Graph().parse(MANIFEST, format="turtle")
    g.parse(data=PREFIXES + f'<{doc_iri}> cor:adjudication [ cor:by "t" ; '
            f'cor:on "2026-10-16"^^xsd:date ; cor:rationale "t" ; cor:disposes {reason} ; '
            f'cor:judgedAgainst [ a cor:Snapshot ; cor:recordedIn "{path}" ; cor:blob "{blob}" ] ] .',
            format="turtle")
    g += lift_firings(g, BASELINE)
    g += lift_snapshots(g)
    return g


def test_admits_disposal_of_a_live_firing():          # positive control (Review Focus 4)
    g = _with_disposal(BFS, '"KIND_NOT_SUPPORTED"')
    ok, report = _conforms(g)
    assert ok, report
    assert _d2_refusals(g) == set()


def test_admits_disposal_typed_xsd_string():
    """rdflib keeps "X" and "X"^^xsd:string as two distinct terms; the join is SPARQL VALUE
    equality (`=`), under which they are equal, so the membrane admits either spelling."""
    g = _with_disposal(BFS, '"KIND_NOT_SUPPORTED"^^xsd:string')
    ok, report = _conforms(g)
    assert ok, report
    assert _d2_refusals(g) == set()


def test_refuses_disposal_of_an_unfired_reason():     # spec O2
    assert _d2_refusals(_with_disposal(BFS, '"TRANSPOSED"')) == {M4}


def test_refuses_disposal_of_a_misspelt_reason():     # spec § 8.3, O1 as amended
    assert _d2_refusals(_with_disposal(BFS, '"NOT_A_REASON"')) == {M4}


def test_refuses_disposal_of_superseded_only_ink():   # spec § 8, strengthened D2
    assert _d2_refusals(_with_disposal(BFS, '"ROUND_TRIP_FAIL"')) == {M4}   # 0 live / 6 superseded


def test_refuses_disposal_on_the_wrong_document():
    assert _d2_refusals(_with_disposal(ONS, '"REGION_TILING_FAILED"')) == {M4}  # ons: 0 live / 2 superseded


def test_refuses_language_tagged_disposal():
    """A reason code is a constant, not prose: "X"@en is not value-equal to the lifted "X" under
    SPARQL `=` (the join is value equality, not STR()), so it is refused, not silently matched."""
    assert _d2_refusals(_with_disposal(BFS, '"KIND_NOT_SUPPORTED"@en')) == {M4}


def test_refuses_disposal_without_a_reading():
    g = Graph().parse(MANIFEST, format="turtle")
    g.parse(data=PREFIXES + f'<{BFS}> cor:adjudication [ cor:by "t" ; '
            'cor:on "2026-10-19"^^xsd:date ; cor:rationale "t" ; '
            'cor:disposes "KIND_NOT_SUPPORTED" ] .', format="turtle")
    g += lift_firings(g, BASELINE)
    g += lift_snapshots(g)
    assert _d2_refusals(g) == {M1}


def test_refuses_disposal_judged_against_another_documents_reading():
    # ons fires KIND_NOT_SUPPORTED live too, so only constraint 2 can refuse this
    assert _d2_refusals(_with_disposal(BFS, '"KIND_NOT_SUPPORTED"', snapshot_of=ONS)) == {M2}


def _synthetic(blob):
    return Graph().parse(data=PREFIXES + f"""
        <urn:d:a> a cor:Document ; cor:file "fam/a.pdf" ; cor:url "https://example.org/a" ;
            cor:series "s" ; cor:family "health" ; cor:expectedVerdict cor:Unadjudicated ;
            cor:adjudication [ cor:by "t" ; cor:on "2026-10-19"^^xsd:date ; cor:rationale "t" ;
                cor:disposes "R_X" ;
                cor:judgedAgainst [ a cor:Snapshot ;
                    cor:recordedIn "tests/corpus-baseline/a.json" ; cor:blob "{blob}" ] ] .""",
        format="turtle")


def _lifted(m, repo):
    return m + lift_firings(m, repo / "tests" / "corpus-baseline") + lift_snapshots(m, repo=repo)


def test_r323_disposal_is_judged_at_its_own_reading(tmp_path):     # spec § 5, R323 as ruled
    repo = _repo(tmp_path)
    old = _commit(repo, [("R_X", "escalated")], "fires")
    _commit(repo, [], "repaired")                                  # 0 live NOW
    _publish(repo)
    g = _lifted(_synthetic(old), repo)
    ok, report = _conforms(g)
    assert ok and _d2_refusals(g) == set(), report


def test_refuses_disposal_whose_own_reading_holds_no_live_firing(tmp_path):
    repo = _repo(tmp_path)
    old = _commit(repo, [("R_X", "superseded")], "1")
    _publish(repo)
    assert _d2_refusals(_lifted(_synthetic(old), repo)) == {M4}


def test_refuses_disposal_judged_against_a_non_durable_reading(tmp_path):
    repo = _repo(tmp_path)
    _commit(repo, [("R_X", "escalated")], "base")
    _publish(repo)
    _git(repo, "checkout", "-q", "-b", "feat")
    mid = _commit(repo, [("R_X", "escalated")] * 2, "mid")         # the #354-shaped blob
    _commit(repo, [("R_X", "escalated")] * 3, "head")
    assert _d2_refusals(_lifted(_synthetic(mid), repo)) == {M3}
