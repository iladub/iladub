"""tests/test_cbh_e2e.py — Loop Q Task 7 (spec 2026-08-04): the CBH end-to-end composition.

Corpus-marked, skip-if-absent like tests/test_corpus_stem.py. ONE module-scoped compile of
`corpus/ag-trade/cbh-stem-2026-08-03.pdf` via `compile_document` feeds three tests that
compose the WHOLE loop-Q chain in one document:

  (a) STRUCTURAL — the section-repair driver (§4.0/§4.1): four escalated ruled bands
      recognized as one intra-page repeating group, repaired, adopted, and chained into
      one 4-member logical table.
  (b) GROUNDING (§4.2) — `ground_document` against the CBH demo contract trio, with an
      abstaining Fake proposer (imitating tests/test_corpus_stem.py's ABSTAIN idiom): every
      GroundedNode behind exactly one accountable promotion; records carry the section
      captions as undiscriminated `is_section_marker` candidates; record identities are
      section-prefixed and distinct across sections.
  (c) THE CASCADE (§4.3) — the record identity prefixes (the table's FIRST caption, the
      value `feed.table_records` already used to keep GERALDTON's r0 distinct from
      KWINANA's r0) are the clean marker set spec §4.2's "attribution never waits for
      naming" boundary calls for; fed to `resolve_split_key_name`, they resolve the
      denormalized dimension to the contract's `port` field via the unique-admitting-field
      AXIOM arm — no LLM call needed on this specimen (a raising proposer proves the
      short-circuit) — with exactly one `iladub:PromotionDecision`. The notice strips that
      also arrive as `is_section_marker=True` candidates on the same records (Task 5:
      every caption of a captioned table is injected into every one of its records,
      undiscriminated) are NOT part of the marker set the cascade resolves against — they
      never became a record's identity prefix, so they play no part in the arm-2 whole-set
      membership check.

Tallies are printed (edition-dependent); structural invariants are asserted
(edition-independent, per the loop-K/loop-L/loop-M precedent these tests all follow).
"""
import pytest

from pathlib import Path

from rdflib import RDF, Graph, Namespace

REPO = Path(__file__).resolve().parent.parent
CBH = REPO / "corpus" / "ag-trade" / "cbh-stem-2026-08-03.pdf"
CONTRACT = "examples/shipping/cbh-contract.ttl"
TERMS = "examples/shipping/cbh-terms.ttl"
SHAPES = "examples/shipping/cbh-shapes.ttl"

ILADUB = Namespace("https://w3id.org/iladub#")
CBHNS = Namespace("https://example.org/cbh#")

pytestmark = pytest.mark.corpus

needs_cbh = pytest.mark.skipif(not CBH.is_file(),
                                reason="corpus not populated (scripts/fetch_corpus.py)")


class _RaisingProposer:
    """Proves the cascade's arm-2 short-circuit: calling this on this specimen must never
    happen — CBH's four bare port markers whole-set-admit exactly one contract field, so
    the NEURAL arm 3 is never reached."""
    def propose_split_key_name(self, markers, context):
        raise AssertionError("the proposer must not be called — CBH's port markers "
                              "whole-set-admit a UNIQUE contract field (arm 2)")


@pytest.fixture(scope="module")
def cbh_document():
    """The whole-document compile, ONCE per module (imitates tests/test_corpus_stem.py's
    `stem_document` fixture, F7 of loop M): ~55-60s measured, shared by all three tests
    below rather than re-paid per test. `DocumentReport` is frozen and read-only from here."""
    if not CBH.is_file():
        pytest.skip("corpus not populated (scripts/fetch_corpus.py)")
    from iladub.etkl.document import compile_document
    return compile_document(str(CBH))


@pytest.fixture(scope="module")
def cbh_grounded(cbh_document):
    """Grounds the compiled document once against the CBH demo contract trio (§4.4), with
    an abstaining proposer (test_corpus_stem.py's ABSTAIN idiom: field_iri=None -> any
    non-exact-match concept falls straight to quarantine, so the port/commodity SCHEME
    membership oracle — not a proposer guess — is what grounds anything here)."""
    from iladub.feed import ground_document
    from iladub.ground import load_contract
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

    contract = load_contract(CONTRACT)
    terms = Graph().parse(TERMS, format="turtle")
    shapes = Graph().parse(SHAPES, format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, str(CBHNS) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(cbh_document.graph, contract, abstain, terms, shapes, g)
    return contract, terms, shapes, result, g


# --- (a) structural: repair, chain, score -------------------------------------------

@needs_cbh
def test_cbh_sections_repaired_and_chained(cbh_document):
    """The section-repair driver (spec §4.0/§4.1), measured end-to-end on the real
    document: four still-escalated ruled bands (CBH's doubled-edge geometry defeats
    band-level peel/weld, spec §4.0's own worked case) are recognized as one intra-page
    repeating group, repaired via the ink-witness path, and every one of the four
    admits through the membrane -> adopted -> chained into ONE 4-member logical table.

    The score floor is 0.90 — deliberately AT-OR-BELOW the measured value (corpus-manifest
    convention: never pin the measured number itself as the floor), so this is a
    regression guard, not a re-assertion of the measurement. The measured score is
    PRINTED for the controller's cross-check, never hardcoded as an assertion bound."""
    rep = cbh_document
    print(f"\nCBH document: score={rep.score:.4f} pages={len(rep.pages)} "
          f"repaired_bands={rep.repaired_bands} chains={rep.chains}")
    assert rep.score >= 0.90, f"score {rep.score:.4f} below the 0.90 floor"
    # four repaired sections, all adopted (repaired_bands only ever holds ADOPTED bands —
    # DocumentReport's own docstring: a candidate whose pass-2 re-read still escalates
    # leaves no entry here)
    assert len(rep.repaired_bands) == 4, rep.repaired_bands
    assert len({page for page, _ in rep.repaired_bands}) == 1     # CBH is a 1-page document
    # a 4-chain: the driver stitched all four repaired sections into one logical table
    four_chains = [c for c in rep.chains if len(c) == 4]
    assert len(four_chains) == 1, rep.chains


# --- (b) grounding: promotion invariant, section-key candidates, distinct identities ---

@needs_cbh
def test_cbh_grounds_with_section_key_candidates(cbh_document, cbh_grounded):
    """Grounding (spec §4.2) against the CBH demo contract trio: every GroundedNode behind
    exactly one accountable promotion (the §3 invariant, run here on the FULL repaired
    document, not a synthetic fixture); records of a repaired section carry that section's
    captions as undiscriminated `is_section_marker` candidates (Task 5's injection, read
    back here through the real grounding path rather than a hand-built graph); and record
    identities are section-prefixed and stay distinct across sections (no two ports'
    row 0 collide)."""
    from iladub.feed import table_records

    contract, terms, shapes, result, g = cbh_grounded
    grounded = set(g.subjects(RDF.type, ILADUB.GroundedNode))
    candidates = set(g.subjects(RDF.type, ILADUB.CandidateConcept))
    print(f"\nCBH grounding: records={result.records} grounded={result.grounded} "
          f"still-quarantined={result.proposed} candidate-pool={len(candidates)}")
    assert len(grounded) == result.grounded > 0
    assert result.proposed > 0                     # honest quarantine tally, not zero

    # the §3 invariant: every grounded node behind EXACTLY one promotion decision
    for n in grounded:
        assert len(list(g.objects(n, ILADUB.wasPromotedBy))) == 1

    # section-key candidates: at least one record carries a section marker whose text is
    # one of the contract's own scheme-port labels (GERALDTON etc.), proving Task 5's
    # injection reached the real document, not just its unit fixture.
    from rdflib.namespace import SKOS
    recs = table_records(cbh_document.graph)
    marker_texts = {c.text for r in recs for c in r.concepts if c.is_section_marker}
    port_labels = {str(terms.value(s, SKOS.prefLabel))
                   for s in terms.subjects(SKOS.inScheme, CBHNS["scheme-port"])}
    print(f"distinct is_section_marker texts: {len(marker_texts)}  "
          f"port-scheme labels present among them: {marker_texts & port_labels}")
    assert marker_texts & port_labels, marker_texts

    # identities: section-prefixed and distinct — two different sections' "row 0" never
    # collide (the record subject IS the prefixed row_id, per feed._record_uri)
    prefixed = [r.row_id for r in recs if " > " in r.row_id]
    assert prefixed, "no section-prefixed records at all"
    assert len(prefixed) == len(set(prefixed)), "section-prefixed identities collided"
    sections = {rid.split(" > ")[0] for rid in prefixed}
    print(f"section-prefixed records: {len(prefixed)} across sections: {sorted(sections)}")
    assert len(sections) >= 2, sections            # more than one section actually keyed


# --- (c) the cascade: dimension-name resolution end to end --------------------------

@needs_cbh
def test_cbh_cascade_resolves_port(cbh_document, cbh_grounded):
    """The naming cascade (spec §4.3), fed the REAL document's record identities rather
    than a synthetic marker list: the distinct section-prefix values (the table's FIRST
    caption per repaired section, per feed.table_records's "attribution never waits for
    naming" idiom — Task 5) are CBH's clean key-marker set. Fed to
    `resolve_split_key_name`, they whole-set-admit exactly one CBH contract field
    (`port`) -> the unique-admitting-field AXIOM arm asserts, no LLM call, exactly one
    `iladub:PromotionDecision`.

    The notice strips (e.g. 'BERTH MAY BE UNAVAILABLE...') are ALSO injected as
    `is_section_marker=True` candidates on the very same records (Task 5's undiscriminated
    injection), but never became a record's identity PREFIX (feed.table_records only
    prefixes with the table's FIRST caption) — so they are asserted here NOT to be part of
    the marker set the cascade actually resolves against, the concrete measured meaning of
    spec §4.3's "non-member markers quarantine as values regardless" boundary."""
    from iladub.feed import table_records
    from iladub.splitkey import resolve_split_key_name

    contract, terms, shapes, result, g = cbh_grounded
    recs = table_records(cbh_document.graph)

    prefix_markers = sorted({r.row_id.split(" > ")[0] for r in recs if " > " in r.row_id})
    all_marker_texts = {c.text for r in recs for c in r.concepts if c.is_section_marker}
    notices = all_marker_texts - set(prefix_markers)
    print(f"\nCBH cascade: prefix (identity-key) markers = {prefix_markers}")
    print(f"notice-only is_section_marker texts (present on records, excluded from the "
          f"cascade's marker set) = {len(notices)}")
    assert notices, "expected at least one notice-only marker on this specimen"
    assert not (notices & set(prefix_markers))     # disjoint by construction

    cascade_graph = Graph()
    res = resolve_split_key_name(prefix_markers, contract, terms, _RaisingProposer(),
                                  cascade_graph)
    print(f"resolution: outcome={res.outcome} name={res.name} arm={res.arm} "
          f"ambiguity_score={res.ambiguity_score}")

    assert res.outcome == "asserted"
    assert res.name == "port"
    assert res.arm == "unique-admitting-field"          # the AXIOM arm, asserted explicitly
    assert res.ambiguity_score == 1
    assert res.field is not None and res.field.fills_property == str(CBHNS.port)

    grounded_nodes = list(cascade_graph.subjects(RDF.type, ILADUB.GroundedNode))
    promotions = list(cascade_graph.subjects(RDF.type, ILADUB.PromotionDecision))
    assert len(grounded_nodes) == 1
    assert len(promotions) == 1
    assert cascade_graph.value(grounded_nodes[0], ILADUB.wasPromotedBy) is not None
    assert cascade_graph.value(grounded_nodes[0], ILADUB.groundsTo) == CBHNS.port
