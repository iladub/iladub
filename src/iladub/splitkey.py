"""splitkey — the denormalized split-key naming cascade (Loop Q Task 6, spec
2026-08-04 §4.3).

Recovers the NAME of a denormalized dimension whose values are carried positionally by
section markers (loop Q §4.2's key-value attribution already mints the row identity —
"GERALDTON > r3" — before any name is known; "attribution never waits for naming").
Three arms, gate-shaped: each fires only when the previous one abstains.

  1. AXIOM — explicit naming in the source (no oracle, no LLM): a "Key: Value" marker
     form, the SAME key shared by every marker, names the dimension directly from raw
     document structure ("Port: GERALDTON"). CBH fails this arm — its markers are bare
     ("GERALDTON") — and abstains to step 2.
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


def _emit_assertion(g, name, markers, grounds_to, suggester_iri, confidence, rationale, anchor_iri):
    """Mints exactly one CandidateConcept + one PromotionDecision + one GroundedNode —
    the same shape ground.py's `ground_concept` uses for a value, applied here to a
    dimension NAME. Every call site is an assertion; the invariant "every grounded node
    has exactly one wasPromotedBy" holds by construction (one pd, one gn, always paired)."""
    cand, agent = _emit_candidate(g, name, markers, anchor_iri, suggester_iri, confidence)
    pd = BNode()
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, Literal(Decimal(str(round(confidence, 6))))))
    g.add((pd, DEC.rationale, Literal(rationale)))
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
        grounds_to = (field.fills_property if field is not None
                     else "urn:iladub:dimension-name/" + _norm(explicit))
        gn = _emit_assertion(
            graph, explicit, markers, grounds_to, _EXPLICIT_RULE, 1.0,
            "Explicit '%s: <value>' marker form, shared by every marker, recovers the "
            "dimension name directly from the source document (no scheme lookup needed)."
            % explicit,
            _GIST_CATEGORY)
        return KeyNameResolution("asserted", explicit, "explicit-naming", None, field, gn)

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
            _GIST_CATEGORY)
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
                    cand.anchor_iri)
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
