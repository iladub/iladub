"""Loop Q Task 6 (spec 2026-08-04 §4.3) — the split-key naming cascade. One test per
cascade arm plus the cross-cutting invariants: every asserted name behind exactly one
iladub:PromotionDecision, and confidence NEVER promotes (a high-scored zero-admitting
proposal still quarantines)."""
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDFS, SKOS

from iladub.ground import load_contract
from iladub.propose_ground import FakeSplitKeyNameProposer, ScoredKeyCandidate
from iladub.splitkey import resolve_split_key_name

ILADUB = Namespace("https://w3id.org/iladub#")
CBH = Namespace("https://example.org/cbh#")
CONTRACT = "examples/shipping/cbh-contract.ttl"
TERMS = "examples/shipping/cbh-terms.ttl"

WA_PORTS = ["GERALDTON", "KWINANA", "ALBANY", "ESPERANCE"]     # 4 of the 5 shipped ports
GIST_CATEGORY = "https://w3id.org/semanticarts/ns/ontology/gist/Category"


def _contract():
    return load_contract(CONTRACT)


def _terms():
    return Graph().parse(TERMS, format="turtle")


class _RaisingProposer:
    """Proves a cascade arm short-circuits: calling this must never happen."""
    def propose_split_key_name(self, markers, context):
        raise AssertionError("the proposer must not be called on this arm")


def _grounded_nodes(g):
    return list(g.subjects(RDF.type, ILADUB.GroundedNode))


def _promotion_decisions(g):
    return list(g.subjects(RDF.type, ILADUB.PromotionDecision))


def _candidate_concepts(g):
    return list(g.subjects(RDF.type, ILADUB.CandidateConcept))


# --- Arm 1: AXIOM, explicit naming --------------------------------------------------

def test_explicit_naming_short_circuits():
    """A shared 'Key: Value' marker form names the dimension straight from the source —
    no contract lookup (empty terms graph), no LLM (a proposer that raises if called)."""
    markers = ["Port: GERALDTON", "Port: KWINANA", "Port: ALBANY"]
    g = Graph()
    res = resolve_split_key_name(markers, _contract(), Graph(), _RaisingProposer(), g)
    assert res.outcome == "asserted"
    assert res.name == "Port"
    assert res.arm == "explicit-naming"
    assert len(_grounded_nodes(g)) == 1
    assert len(_promotion_decisions(g)) == 1
    gn = _grounded_nodes(g)[0]
    assert g.value(gn, ILADUB.wasPromotedBy) is not None
    assert g.value(gn, ILADUB.status) == ILADUB.asserted


def test_explicit_naming_abstains_on_a_bare_marker():
    """CBH fails arm 1 (spec §4.3): its markers are bare values, no 'Key:' prefix — a
    single non-conforming marker abstains the WHOLE arm, even when every other marker
    DOES conform (the arm requires uniform explicit form across the full set)."""
    from iladub.splitkey import _explicit_name
    assert _explicit_name(["Port: GERALDTON", "Port: KWINANA"]) == "Port"     # uniform -> fires
    assert _explicit_name(["Port: GERALDTON", "KWINANA"]) is None            # mixed -> abstains
    assert _explicit_name(["GERALDTON", "KWINANA"]) is None                  # CBH's actual shape


def test_explicit_naming_abstains_on_differing_keys():
    """F3: two markers, each individually a valid 'Key: Value' form, but with DIFFERENT
    keys ('Port' vs 'Berth') — no single shared key names the dimension, so the arm
    abstains (_explicit_name returns None) and the cascade proceeds past it, exactly like
    a fully bare marker set."""
    from iladub.splitkey import _explicit_name
    assert _explicit_name(["Port: X", "Berth: Y"]) is None

    g = Graph()
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("region", GIST_CATEGORY, 0.5, "no shared explicit key"),
    ))
    res = resolve_split_key_name(["Port: X", "Berth: Y"], _contract(), _terms(), proposer, g)
    assert res.arm not in ("explicit-naming", "explicit-unverified")   # cascade proceeded


def test_explicit_unverified_key_quarantines():
    """F1 (CRITICAL, §3 violation reproduced by the reviewer): an explicit 'Key: Value'
    form whose key names NO contract field must NEVER assert — minting a synthetic
    groundsTo IRI and asserting on presence alone fabricates a target the membrane cannot
    verify (GroundedNodeShape only checks minCount, not resolution). 'Berth: 12A' /
    'Berth: 7B' against cbh-contract (which has no `berth` field) must quarantine the
    recovered name 'Berth' as a CandidateConcept — nothing asserted, nothing
    wasPromotedBy."""
    markers = ["Berth: 12A", "Berth: 7B"]
    g = Graph()
    res = resolve_split_key_name(markers, _contract(), _terms(), _RaisingProposer(), g)
    assert res.outcome == "quarantined"
    assert res.name is None
    assert res.arm == "explicit-unverified"
    assert res.field is None
    assert not _grounded_nodes(g)
    assert not _promotion_decisions(g)
    assert not list(g.subjects(ILADUB.wasPromotedBy, None))        # nothing promoted, at all
    cc = _candidate_concepts(g)
    assert len(cc) == 1
    assert g.value(cc[0], ILADUB.status) == ILADUB.proposed
    assert str(g.value(cc[0], ILADUB.surfaceText)) == "Berth: 12A, Berth: 7B"


# --- Arm 2: AXIOM, unique admitting contract field ----------------------------------

def test_unique_admitting_asserts_port_with_promotion_decision():
    """CBH's bare markers vs the cbh-contract: only the `port` field's scheme admits the
    whole marker set (commodity's scheme doesn't contain any of them) -> exactly one
    admitting field -> asserts, no LLM needed."""
    g = Graph()
    res = resolve_split_key_name(WA_PORTS, _contract(), _terms(), _RaisingProposer(), g)
    assert res.outcome == "asserted"
    assert res.name == "port"
    assert res.arm == "unique-admitting-field"
    assert res.ambiguity_score == 1
    assert res.field is not None and res.field.fills_property == str(CBH.port)
    assert len(_grounded_nodes(g)) == 1
    assert len(_promotion_decisions(g)) == 1
    gn = _grounded_nodes(g)[0]
    assert g.value(gn, ILADUB.groundsTo) == CBH.port
    assert g.value(gn, ILADUB.wasPromotedBy) is not None


def test_partial_membership_abstains_step_2():
    """A marker set with one value OUTSIDE the port scheme (a typo/new port) is only a
    PARTIAL match -> never asserts at step 2, falls to step 3 (proposer arm)."""
    g = Graph()
    markers = WA_PORTS + ["NOT-A-REAL-PORT"]
    proposed = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("port", GIST_CATEGORY, 0.7, "geography vocabulary"),
    ))
    res = resolve_split_key_name(markers, _contract(), _terms(), proposed, g)
    assert res.arm != "unique-admitting-field"
    assert res.ambiguity_score == 0                       # port no longer whole-set-admits


# --- Arm 3: NEURAL, BAML scored proposal --------------------------------------------

def _doctored_terms_two_admitting():
    """A terms graph where BOTH `port` and `commodity` schemes admit the whole WA-ports
    marker set — the negative fixture spec §4.4 calls for, built in-test (not committed:
    the real cbh-terms.ttl stays an honest, non-doctored public-nomenclature vocabulary)."""
    terms = _terms()
    for i, label in enumerate(WA_PORTS):
        c = URIRef(str(CBH) + "commodity-decoy-%d" % i)
        terms.add((c, RDF.type, SKOS.Concept))
        terms.add((c, SKOS.inScheme, CBH["scheme-commodity"]))
        terms.add((c, SKOS.prefLabel, Literal(label)))
    return terms


def test_two_admitting_fake_proposer_picks_among_verified():
    """>=2 admitting fields (port AND the doctored commodity scheme both admit the whole
    set): the Fake proposer's ranked candidates are matched against the VERIFIED admitting
    fields only — the winner (highest-scoring MATCH) asserts."""
    g = Graph()
    terms = _doctored_terms_two_admitting()
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("port", GIST_CATEGORY, 0.91, "geography vocabulary"),
        ScoredKeyCandidate("commodity", GIST_CATEGORY, 0.40, "less likely"),
    ))
    res = resolve_split_key_name(WA_PORTS, _contract(), terms, proposer, g)
    assert res.outcome == "asserted"
    assert res.name == "port"
    assert res.arm == "proposer-pick-among-verified"
    assert res.ambiguity_score == 2
    assert len(_grounded_nodes(g)) == 1
    assert len(_promotion_decisions(g)) == 1
    gn = _grounded_nodes(g)[0]
    assert g.value(gn, ILADUB.groundsTo) == CBH.port


def test_two_admitting_ignores_a_proposal_that_names_no_verified_field():
    """The proposer's TOP candidate doesn't name either verified field ('berth' matches
    neither port nor commodity) -> the cascade must not fabricate a pick; it walks down to
    the next candidate that DOES match a verified field."""
    g = Graph()
    terms = _doctored_terms_two_admitting()
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("berth", GIST_CATEGORY, 0.95, "top guess, but unverified"),
        ScoredKeyCandidate("commodity", GIST_CATEGORY, 0.30, "verified, lower score"),
    ))
    res = resolve_split_key_name(WA_PORTS, _contract(), terms, proposer, g)
    assert res.outcome == "asserted"
    assert res.name == "commodity"
    assert len(_grounded_nodes(g)) == 1


def test_two_admitting_no_candidate_matches_any_verified_field():
    """F4: >=2 admitting fields, but NO proposed candidate names EITHER verified field
    ('berth' and 'region' match neither 'port' nor 'commodity') -> honest refusal, not a
    fabricated pick: nothing asserts, and the arm is reported explicitly as
    'proposer-no-verified-match' (distinct from the 0-admitting 'proposer-quarantine')."""
    g = Graph()
    terms = _doctored_terms_two_admitting()
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("berth", GIST_CATEGORY, 0.95, "top guess, unverified"),
        ScoredKeyCandidate("region", GIST_CATEGORY, 0.80, "also unverified"),
    ))
    res = resolve_split_key_name(WA_PORTS, _contract(), terms, proposer, g)
    assert res.outcome == "quarantined"
    assert res.name is None
    assert res.arm == "proposer-no-verified-match"
    assert res.ambiguity_score == 2
    assert not _grounded_nodes(g)
    assert not _promotion_decisions(g)
    cc = _candidate_concepts(g)
    assert len(cc) == 1
    assert g.value(cc[0], RDFS.label) == Literal("berth")          # the top-scored proposal


def test_zero_admitting_quarantines_candidate_concept():
    """No contract field admits the whole marker set: the top proposal stays a quarantined
    CandidateConcept — nothing asserted, no GroundedNode, no PromotionDecision."""
    g = Graph()
    markers = ["NORTH ZONE", "SOUTH ZONE"]
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("region", GIST_CATEGORY, 0.6, "zone vocabulary"),
    ))
    res = resolve_split_key_name(markers, _contract(), _terms(), proposer, g)
    assert res.outcome == "quarantined"
    assert res.name is None
    assert res.arm == "proposer-quarantine"
    assert res.ambiguity_score == 0
    assert not _grounded_nodes(g)
    assert not _promotion_decisions(g)
    cc = _candidate_concepts(g)
    assert len(cc) == 1
    assert g.value(cc[0], ILADUB.status) == ILADUB.proposed


def test_confidence_never_promotes():
    """A 0.99-scored zero-admitting proposal still quarantines — confidence is never a
    substitute for a verified oracle (§3, the B1.2 confidence≠validity lesson)."""
    g = Graph()
    markers = ["NORTH ZONE", "SOUTH ZONE"]
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("port", GIST_CATEGORY, 0.99, "very confident guess"),
    ))
    res = resolve_split_key_name(markers, _contract(), _terms(), proposer, g)
    assert res.outcome == "quarantined"
    assert not _grounded_nodes(g)
    assert not _promotion_decisions(g)
    cc = _candidate_concepts(g)[0]
    assert float(g.value(cc, ILADUB.confidence)) == 0.99
    assert g.value(cc, ILADUB.status) == ILADUB.proposed          # never 'asserted'


# --- Cross-cutting invariants -------------------------------------------------------

def test_every_grounded_node_has_exactly_one_promotion():
    """Across all three ASSERTING arms, sharing one graph: every GroundedNode carries
    EXACTLY one wasPromotedBy, and every PromotionDecision produced exactly one
    GroundedNode (1:1, no fan-out/fan-in)."""
    g = Graph()
    resolve_split_key_name(["Port: GERALDTON"], _contract(), Graph(), _RaisingProposer(), g)
    resolve_split_key_name(WA_PORTS, _contract(), _terms(), _RaisingProposer(), g)
    terms2 = _doctored_terms_two_admitting()
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("port", GIST_CATEGORY, 0.91, "geography vocabulary"),
        ScoredKeyCandidate("commodity", GIST_CATEGORY, 0.40, "less likely"),
    ))
    resolve_split_key_name(WA_PORTS, _contract(), terms2, proposer, g)

    gns = _grounded_nodes(g)
    assert len(gns) == 3
    for gn in gns:
        promoters = list(g.objects(gn, ILADUB.wasPromotedBy))
        assert len(promoters) == 1, (gn, promoters)

    pds = _promotion_decisions(g)
    assert len(pds) == 3
    for pd in pds:
        produced = [gn for gn in gns if g.value(gn, ILADUB.wasPromotedBy) == pd]
        assert len(produced) == 1, (pd, produced)


def test_asserted_shapes_conform_to_epistemics_shacl():
    """The shipped promotion-invariant SHACL (used by ground.py's own tests) must accept
    what this cascade asserts, and the quarantine path must never leak an 'asserted'
    CandidateConcept."""
    from iladub.validate import validate

    def _knowledge():
        kg = Graph()
        for f in ("vocab/ontology/iladub.ttl", "vocab/ontology/dec.ttl"):
            kg.parse(f, format="turtle")
        return kg

    def _shapes():
        return Graph().parse("vocab/shapes/iladub-shapes.ttl", format="turtle")

    g = Graph()
    resolve_split_key_name(WA_PORTS, _contract(), _terms(), _RaisingProposer(), g)
    resolve_split_key_name(["NORTH ZONE", "SOUTH ZONE"], _contract(), _terms(),
                           FakeSplitKeyNameProposer((
                               ScoredKeyCandidate("port", GIST_CATEGORY, 0.99, "guess"),
                           )), g)
    r = validate(g, _shapes(), _knowledge())
    assert r.conforms, r.report_text


# --- the split-key naming promotions deliberate (spec 2026-08-10 §5.3) --------------
#
# PREMISE TYPE: **FIXTURE**, not evidence. MEASURED: `resolve_split_key_name` has no
# production call site (`grep -rn resolve_split_key_name src tests scripts` names only
# tests/test_split_key_naming.py and tests/test_cbh_e2e.py), so this emitter contributes
# ZERO to the corpus and cannot move the O1/O4 oracle. Unit tests are its only disposal.
#
# `_emit_assertion` is the FIFTH producer with the defect Task 4 fixed in `ground.py`: it
# minted a dec:DecisionHolon with no dec:optionSpace and no dec:chosen, while its docstring
# claimed "the same shape ground.py's `ground_concept` uses". The oracle is
# vocab/shapes/dec-shapes.ttl, which this loop may not edit.

from pathlib import Path

from pyshacl import validate as _pyshacl_validate

DEC = Namespace("https://w3id.org/iladub/dec#")
_ONT_DIR = Path(__file__).parents[1] / "vocab" / "ontology"
_DEC_SHAPES = Path(__file__).parents[1] / "vocab" / "shapes" / "dec-shapes.ttl"


def _dec_conforms(g):
    """(conforms, text) against the SHIPPED closure — membrane._validate_pyshacl exactly."""
    from iladub.etkl import membrane
    ont = Graph()
    for f in ("dec.ttl", "iladub.ttl"):
        ont.parse(str(_ONT_DIR / f), format="turtle")
    shapes = Graph().parse(str(_DEC_SHAPES), format="turtle")
    conforms, _, text = _pyshacl_validate(membrane.subclass_closure(g, ont), shacl_graph=shapes,
                                          inference="none", advanced=True)
    return bool(conforms), text


def _assert_deliberated(g, label):
    """The assertions every promotion decision owes dec:DecisionHolonShape. Returns the
    set of dec:rejectedBecause strings on the options that lost."""
    conforms, text = _dec_conforms(g)
    assert conforms, f"[{label}] {text}"
    pds = _promotion_decisions(g)
    assert len(pds) == 1, f"[{label}] expected exactly one PromotionDecision, got {pds}"
    pd = pds[0]
    options = list(g.objects(pd, DEC.optionSpace))
    assert len(options) >= 2, f"[{label}] a real decision deliberates >= 2 options: {options}"
    chosen = list(g.objects(pd, DEC.chosen))
    assert len(chosen) == 1, f"[{label}] exactly one chosen option: {chosen}"
    assert chosen[0] in options, f"[{label}] the chosen option must be in the option space"
    rejected = set()
    for o in options:
        assert g.value(o, RDFS.label) is not None, f"[{label}] an unlabelled option: {o}"
        if o != chosen[0]:
            why = g.value(o, DEC.rejectedBecause)
            assert why is not None, f"[{label}] the rejected option {o} does not say why it lost"
            rejected.add(str(why))
    return options, chosen[0], rejected


def _arm1_explicit(g):
    return resolve_split_key_name(["Port: GERALDTON", "Port: KWINANA"], _contract(), Graph(),
                                  _RaisingProposer(), g)


def _arm2_unique(g):
    return resolve_split_key_name(WA_PORTS, _contract(), _terms(), _RaisingProposer(), g)


def _arm3_pick_among_verified(g):
    proposer = FakeSplitKeyNameProposer((
        ScoredKeyCandidate("port", GIST_CATEGORY, 0.91, "geography vocabulary"),
        ScoredKeyCandidate("commodity", GIST_CATEGORY, 0.40, "less likely"),
    ))
    return resolve_split_key_name(WA_PORTS, _contract(), _doctored_terms_two_admitting(),
                                  proposer, g)


def test_explicit_naming_promotion_deliberates():
    """Arm 1. The alternative is the branch the SAME arm takes three lines down when
    `exact_field` returns None: quarantine as `explicit-unverified`. Naming it invents
    nothing (Global Constraint 3)."""
    g = Graph()
    res = _arm1_explicit(g)
    assert res.arm == "explicit-naming", "setup: arm 1 must assert"
    _, chosen, _ = _assert_deliberated(g, "explicit-naming")
    assert "Port" in str(g.value(chosen, RDFS.label)), (
        "the chosen option must name the dimension it promoted")


def test_unique_admitting_promotion_deliberates():
    """Arm 2. The alternative is the abstention the code itself takes when `len(admitting)`
    is not 1 — it falls through to arm 3's quarantine."""
    g = Graph()
    res = _arm2_unique(g)
    assert res.arm == "unique-admitting-field", "setup: arm 2 must assert"
    _assert_deliberated(g, "unique-admitting-field")


def test_proposer_pick_among_verified_deliberates_the_fields_it_did_not_pick():
    """Arm 3. The option space is NOT invented: `admitting` is the list the code itself
    enumerates, and the proposer picks one of its members. Every OTHER admitting field is
    an option the code could have taken, so each must appear and say why it lost."""
    g = Graph()
    res = _arm3_pick_among_verified(g)
    assert res.arm == "proposer-pick-among-verified", "setup: arm 3 must assert"
    options, chosen, rejected = _assert_deliberated(g, "proposer-pick-among-verified")
    labels = {str(g.value(o, RDFS.label)) for o in options}
    assert any("commodity" in l for l in labels), (
        f"the VERIFIED field the proposer ranked lower must be a deliberated option: {labels}")
    assert any("commodity" in r for r in rejected), (
        f"the losing admitting field must say why IT lost, by name: {rejected}")


def test_the_three_arms_reject_for_three_different_reasons():
    """THE ANTI-DECORATION ORACLE (Global Constraint 4). Three arms assert through three
    different oracles — an explicit source form, whole-set scheme membership, and a NEURAL
    narrowing of an already-verified set. A single hard-coded rejection string passes every
    assertion above and fails this one."""
    reasons = []
    for label, arm in (("explicit-naming", _arm1_explicit),
                       ("unique-admitting-field", _arm2_unique),
                       ("proposer-pick-among-verified", _arm3_pick_among_verified)):
        g = Graph()
        arm(g)
        _, _, rejected = _assert_deliberated(g, label)
        reasons.append(frozenset(rejected))
    assert len(set(reasons)) == 3, (
        f"the three arms must not share a rejection reason — decoration, not deliberation: "
        f"{reasons}")
