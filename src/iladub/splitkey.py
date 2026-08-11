"""splitkey — the denormalized split-key naming cascade (Loop Q Task 6, spec
2026-08-04 §4.3).

Recovers the NAME of a denormalized dimension whose values are carried positionally by
section markers (loop Q §4.2's key-value attribution already mints the row identity —
"GERALDTON > r3" — before any name is known; "attribution never waits for naming").
Three arms, gate-shaped: each fires only when the previous one abstains.

  1. AXIOM — explicit naming in the source (no LLM): a "Key: Value" marker form, the SAME
     key shared by every marker, recovers the dimension name directly from raw document
     structure ("Port: GERALDTON"). CBH fails this arm — its markers are bare
     ("GERALDTON") — and abstains to step 2. The recovered key is real §0 evidence, but it
     still needs an oracle to ASSERT (§3: assert only what you can ground): when it
     matches a contract field exactly, it asserts against that field; when it matches NO
     field ("Berth: 12A" against a contract with no `berth` field), it is NOT asserted —
     minting a synthetic groundsTo IRI and asserting on presence alone would fabricate a
     target the membrane cannot actually verify. It quarantines instead, as an
     `iladub:CandidateConcept` (arm `explicit-unverified`) — the same disposal shape as
     arm 3's zero-admitting outcome.
  2. AXIOM — unique admitting contract field: ground the marker VALUES against the
     destination contract's SKOS schemes (the shipped `ground.scheme_member` oracle). A
     field ADMITS the set iff its scheme contains a matching label for EVERY marker
     (whole-set membership — strict, decidable); the ambiguity score is the COUNT of
     admitting fields. Exactly one admitting field -> the name is *derived from the
     contract*, asserted through an `iladub:PromotionDecision` recording the membership
     evidence. No LLM. Partial membership (a field admits a strict subset) never asserts
     here — it abstains to step 3.
  3. NEURAL — BAML scored proposal (fires only on 0 or >=2 admitting fields): the
     proposer guesses ranked name candidates from the markers + a context sketch, UNAWARE
     of which contract fields admit — soundness was already decided in step 2, so the
     NEURAL step only ever NARROWS an already-verified set, never invents membership:
       - >=2 admitting: the proposer's ranked candidates are matched against the VERIFIED
         admitting-field names; the highest-scoring MATCH asserts (the "winner").
       - 0 admitting (or, in the >=2 case, no candidate names a verified field): the
         top-scored proposal stays a quarantined `iladub:CandidateConcept` (suggested
         anchor + suggester + score). Confidence NEVER promotes, however high the score
         (§3; the B1.2 confidence≠validity lesson) — a 0.99-scored zero-admitting guess
         quarantines exactly like a 0.1-scored one.

Boundary (read before wiring this into feed.py / ground_document): this module resolves
the dimension's NAME only. Per-VALUE grounding of each individual marker — a marker
outside its field's scheme quarantines as a *value* regardless of how the name resolves
(§7) — is the shipped `ground_concept` / `ground_document` path; Task 5's
`feed._inject_section_captions` already routes every caption through it as an
undiscriminated candidate. This function does not touch or duplicate that.

A second, out-of-scope boundary (a residue, not solved here): `markers` must already be
the clean set of KEY marker texts for one dimension. Discriminating a genuine key
("GERALDTON") from stray notice text among a table's captions ("BERTH MAY BE UNAVAILABLE
...") — both arrive as `is_section_marker=True` candidates from Task 5's feed — is not
this function's job either; the caller must present a clean set (or accept that notice
pollution defeats whole-set membership and drives the resolution to step 3).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from rdflib import RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef

from .ground import Contract, ContractField, SurfaceConcept, exact_field, scheme_member

ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")

_GIST_CATEGORY = "https://w3id.org/semanticarts/ns/ontology/gist/Category"
_EXPLICIT_RULE = "urn:iladub:suggester/explicit-marker-naming-rule"
_MEMBERSHIP_RULE = "urn:iladub:suggester/unique-admitting-field-rule"

# "Port: GERALDTON" -> ("Port", "GERALDTON"). Requires a non-blank value after the colon
# so a bare trailing ":" doesn't count as an explicit form.
_EXPLICIT_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 _/-]*?)\s*:\s*\S.*$")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


@dataclass(frozen=True)
class KeyNameResolution:
    """The cascade's verdict. `outcome` is "asserted" or "quarantined" (never anything
    else — there is no third epistemic state). `node` is the minted GroundedNode (asserted)
    or CandidateConcept (quarantined) identifier in `graph`, or None only when the
    proposer returned no candidates at all to quarantine."""
    outcome: str
    name: str | None
    arm: str
    ambiguity_score: int | None
    field: ContractField | None = None
    node: object = None


def _field_local_name(field: ContractField) -> str:
    return field.fills_property.split("#")[-1].split("/")[-1]


def _explicit_name(markers: list[str]) -> str | None:
    """Step 1's oracle: the form itself IS the evidence (§0 recovery — raw extraction of
    an explicit marker, not a judgment call). Every marker must share the SAME key; one
    non-conforming marker (a bare value) abstains the whole arm."""
    names = set()
    for m in markers:
        match = _EXPLICIT_RE.match(m)
        if not match:
            return None
        names.add(match.group(1).strip())
    return names.pop() if len(names) == 1 else None


def _admitting_fields(markers: list[str], contract: Contract, terms: Graph) -> list[ContractField]:
    """Step 2's oracle: whole-set scheme membership. A field ADMITS the marker set iff its
    scheme carries a matching skos:prefLabel for EVERY marker (strict, decidable — partial
    membership never admits)."""
    admitting = []
    for f in contract.fields:
        if f.scheme is None:
            continue
        if all(scheme_member(m, f.scheme, terms) is not None for m in markers):
            admitting.append(f)
    return admitting


def _emit_candidate(g, name, markers, anchor_iri, suggester_iri, confidence):
    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal(name)))
    g.add((cand, ILADUB.surfaceText, Literal(", ".join(markers))))
    g.add((cand, ILADUB.suggestedAnchor, URIRef(anchor_iri)))
    agent = URIRef(suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.confidence, Literal(Decimal(str(round(confidence, 6))))))
    region = URIRef("urn:iladub:region:split-key-naming")
    g.add((region, RDF.type, ILADUB.SourceRegion))
    g.add((cand, ILADUB.fromRegion, region))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    return cand, agent


def _deliberate(g, pd, chosen_label, alternatives):
    """Record the option space of a naming promotion: `chosen_label`, plus every
    `alternatives` entry (label -> why it lost). Emits `dec:optionSpace` per option,
    `dec:chosen` on one and `dec:rejectedBecause` on the rest, satisfying
    `dec:DecisionHolonShape` (spec 2026-08-10 §5.3).

    §8: PROCEDURAL — it records a decision `resolve_split_key_name` has ALREADY made; it
    decides nothing, ranks nothing and carries no constant. THE OPTIONS ARE NOT INVENTED
    (Global Constraint 3): each arm passes the branches its OWN code enumerates — arm 1's
    quarantine-as-`explicit-unverified` (the `if field is not None` it just took), arm 2's
    abstention to arm 3 when `len(admitting) != 1`, and arm 3's `admitting` list itself,
    which the NEURAL step only narrows.

    Option nodes are BNodes, following `ground._emit_grounded` rather than
    `promote._deliberate`: `pd`, `cand` and `gn` are all BNodes here, so a URIRef option
    would be the only named node in an otherwise anonymous record, with no stable identity
    to mint it from. The convention travels; the node type follows its decision.
    """
    chosen = BNode()
    g.add((chosen, RDF.type, DEC.Option))
    g.add((chosen, RDFS.label, Literal(chosen_label)))
    g.add((pd, DEC.optionSpace, chosen))
    g.add((pd, DEC.chosen, chosen))
    for label, why in alternatives:
        o = BNode()
        g.add((o, RDF.type, DEC.Option))
        g.add((o, RDFS.label, Literal(label)))
        g.add((o, DEC.rejectedBecause, Literal(why)))
        g.add((pd, DEC.optionSpace, o))


def _emit_assertion(g, name, markers, grounds_to, suggester_iri, confidence, rationale,
                    anchor_iri, chosen_label, alternatives):
    """Mints exactly one CandidateConcept + one PromotionDecision + one GroundedNode —
    the same shape ground.py's `ground_concept` uses for a value, applied here to a
    dimension NAME. Every call site is an assertion; the invariant "every grounded node
    has exactly one wasPromotedBy" holds by construction (one pd, one gn, always paired).

    `chosen_label` + `alternatives` are the DELIBERATION the arm performed: a promotion
    that cannot name what it weighed is not an accountable decision, and
    `dec:DecisionHolonShape` refuses it."""
    cand, agent = _emit_candidate(g, name, markers, anchor_iri, suggester_iri, confidence)
    pd = BNode()
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, Literal(Decimal(str(round(confidence, 6))))))
    g.add((pd, DEC.rationale, Literal(rationale)))
    _deliberate(g, pd, chosen_label, alternatives)
    gn = BNode()
    g.add((gn, RDF.type, ILADUB.GroundedNode))
    g.add((gn, ILADUB.wasPromotedBy, pd))
    g.add((gn, ILADUB.groundsTo, URIRef(grounds_to)))
    g.add((gn, ILADUB.status, ILADUB.asserted))
    g.add((pd, DEC.produced, gn))
    return gn


def resolve_split_key_name(markers, contract: Contract, terms: Graph, proposer, graph: Graph,
                           context: str = "") -> KeyNameResolution:
    """Implements spec §4.3's three-arm naming cascade (see module docstring for full
    disposal semantics and the per-value / clean-marker-set boundaries)."""
    markers = list(markers)

    # --- Arm 1: AXIOM, explicit naming (no contract, no terms, no LLM needed) ---
    explicit = _explicit_name(markers)
    if explicit is not None:
        field = exact_field(SurfaceConcept(explicit, "", "na"), contract)
        if field is not None:
            gn = _emit_assertion(
                graph, explicit, markers, field.fills_property, _EXPLICIT_RULE, 1.0,
                "Explicit '%s: <value>' marker form, shared by every marker, recovers the "
                "dimension name directly from the source document AND matches contract "
                "field '%s' (no scheme lookup needed)." % (explicit, _field_local_name(field)),
                _GIST_CATEGORY,
                "name the split key '%s', grounded to contract field '%s'"
                % (explicit, _field_local_name(field)),
                [("quarantine '%s' as an unverified proposition" % explicit,
                  "the explicit marker form is real source evidence AND `exact_field` matched "
                  "contract field '%s'; quarantine is the branch this same arm takes when the "
                  "recovered key matches NO contract field, since asserting it would fabricate "
                  "a groundsTo target the membrane cannot verify"
                  % _field_local_name(field))])
            return KeyNameResolution("asserted", explicit, "explicit-naming", None, field, gn)
        # §3: the explicit form IS real §0 evidence (recovered exactly from the source),
        # but it names NO contract field — nothing to ground it against. Assert only what
        # you can ground; propose everything else. Never mint a synthetic groundsTo IRI
        # and assert on presence alone (that both fabricates a target and defeats the
        # membrane's only real check on groundsTo, which is minCount, not resolution).
        cc, _ = _emit_candidate(
            graph, explicit, markers, _GIST_CATEGORY, _EXPLICIT_RULE, 1.0)
        return KeyNameResolution("quarantined", None, "explicit-unverified", None, None, cc)

    # --- Arm 2: AXIOM, unique admitting contract field ---
    admitting = _admitting_fields(markers, contract, terms)
    if len(admitting) == 1:
        field = admitting[0]
        name = _field_local_name(field)
        gn = _emit_assertion(
            graph, name, markers, field.fills_property, _MEMBERSHIP_RULE, 1.0,
            "Contract field '%s' is the UNIQUE field whose scheme (%s) admits every "
            "marker %r (whole-set membership; ambiguity score = 1)."
            % (name, field.scheme, markers),
            _GIST_CATEGORY,
            "name the split key '%s', the unique admitting contract field" % name,
            [("abstain to the NEURAL arm and quarantine the top proposal",
              "exactly ONE contract field's scheme admits every marker (ambiguity score 1), so "
              "membership decides the name outright; abstention is the branch this arm takes "
              "when `admitting` holds 0 or >= 2 fields and nothing but a proposer can narrow it")])
        return KeyNameResolution("asserted", name, "unique-admitting-field", 1, field, gn)

    # --- Arm 3: NEURAL, BAML scored proposal (0 or >=2 admitting) ---
    score = len(admitting)
    ranked = sorted(proposer.propose_split_key_name(markers, context), key=lambda c: c.score,
                    reverse=True)

    if admitting:                                          # >=2 admitting: pick among VERIFIED
        by_norm_name = {_norm(_field_local_name(f)): f for f in admitting}
        for cand in ranked:
            field = by_norm_name.get(_norm(cand.name))
            if field is not None:
                name = _field_local_name(field)
                gn = _emit_assertion(
                    graph, name, markers, field.fills_property, cand.suggester_iri, cand.score,
                    "NEURAL proposal picked '%s' among %d VERIFIED admitting fields "
                    "(ambiguity score = %d; membership was decided BEFORE the proposer "
                    "spoke — the NEURAL step only narrows): %s"
                    % (name, len(admitting), score, cand.rationale),
                    cand.anchor_iri,
                    "name the split key '%s', the verified admitting field the proposer "
                    "ranked highest (score %s)" % (name, cand.score),
                    # THE OPTION SPACE IS `admitting` ITSELF (Global Constraint 3): every
                    # field in it passed the whole-set membership oracle, so each is a name
                    # this arm could have asserted. They lost to the NEURAL narrowing, not
                    # to the membership oracle — and each says so BY NAME, so a reader can
                    # see which verified reading was set aside.
                    [("name the split key '%s'" % _field_local_name(other),
                      "'%s' is a VERIFIED admitting field — its scheme (%s) admits every "
                      "marker exactly as the chosen one does — but the proposer's ranked "
                      "candidates named '%s' at score %s and nothing above it named '%s'; "
                      "membership could not discriminate the two, so only the NEURAL step "
                      "could"
                      % (_field_local_name(other), other.scheme, name, cand.score,
                         _field_local_name(other)))
                     for other in admitting if other is not field]
                    + [("quarantine the top proposal, naming nothing",
                        "a ranked proposal DID name a verified admitting field, so refusing "
                        "to name would discard a reading both the membership oracle and the "
                        "proposer admit; quarantine is the branch taken when no candidate "
                        "names any verified field")])
                return KeyNameResolution("asserted", name, "proposer-pick-among-verified",
                                         score, field, gn)
        # no proposed candidate names any verified field -> honest refusal (never fabricate
        # a pick); falls through to the same quarantine-the-top-proposal path as 0-admitting.

    if ranked:
        top = ranked[0]
        cc, _ = _emit_candidate(graph, top.name, markers, top.anchor_iri, top.suggester_iri,
                                top.score)
        arm = "proposer-quarantine" if score == 0 else "proposer-no-verified-match"
        return KeyNameResolution("quarantined", None, arm, score, None, cc)

    return KeyNameResolution("quarantined", None, "proposer-empty", score, None, None)
