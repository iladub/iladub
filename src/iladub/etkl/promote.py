"""promote — emit the accountable provenance for a GenAI-proposed dimension name (Loop A2).

The proposed name is a PROPOSITION: an iladub:CandidateConcept reviewed by an
iladub:PromotionDecision (a dec:DecisionHolon). The reshape structure is oracle-certified;
the NAME is not — dec:rationale records that split.
"""
from __future__ import annotations

import re
from decimal import Decimal

from rdflib import RDF, RDFS, BNode, Literal, Namespace, URIRef

TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
GIST = Namespace("https://w3id.org/semanticarts/ns/ontology/gist/")


def _slug(s):
    """IRI-safe slug — a proposed name may be a multi-word phrase (e.g. 'Fiscal Quarter'),
    which would make an unencoded IRI invalid Turtle. The human-readable name is preserved
    verbatim on the CandidateConcept's rdfs:label; this only sanitizes the promotion IRI."""
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-") or "dim"


def _suggester(g, proposal):
    from .membrane import suggester_agent           # R129: refuse a non-IRI suggester HERE
    agent = suggester_agent(proposal.suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    return agent


def _deliberate(g, pd, chosen, alternatives):
    """Record the option space of a promotion: `chosen` plus every `alternatives` entry
    (name -> why it lost). Emits `dec:optionSpace` per option, `dec:chosen` on one, and
    `dec:rejectedBecause` on the rest, satisfying `dec:DecisionHolonShape`.

    §8: PROCEDURAL — it records a decision the caller has ALREADY made; it decides nothing,
    ranks nothing and carries no constant. The OPTIONS ARE NOT INVENTED (Global Constraint 3):
    each caller passes the legal set its own code enumerates — `("absorb", "standalone")` at
    `span.py:90`, `rowrole.ROLES` at `rowrole.py:36`, and reshape's escalate-unnamed branch at
    `reshape.py:206,219`. A name not in one of those sets is a branch the code could not have
    taken, and must not appear here.

    Option nodes are URIRefs derived from `pd`, following `decisionlog.BandRecorder.record`
    (`{d}-opt-{slug}`). This is the same convention `ground._emit_grounded` follows with
    BNodes: the option's identity matches the identity of the decision it hangs off — `pd` is
    a URIRef here and a BNode there, so the nodes differ while the convention does not.
    """
    for name, why in [(chosen, None)] + list(alternatives):
        o = URIRef("%s-opt-%s" % (pd, _slug(str(name))))
        g.add((o, RDF.type, DEC.Option))
        g.add((o, RDFS.label, Literal(str(name))))
        g.add((pd, DEC.optionSpace, o))
        if why is None:
            g.add((pd, DEC.chosen, o))
        else:
            g.add((o, DEC.rejectedBecause, Literal(why)))


def emit_promotion(g, t, normalized_base, dimension_name, values, proposal):
    """Write the CandidateConcept + PromotionDecision for a promoted name; link the recipe's
    UnpivotOp via tab:namePromotedBy. Returns the PromotionDecision uri."""
    agent = _suggester(g, proposal)
    _confidence = Literal(Decimal(str(round(proposal.confidence, 6))))

    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal(dimension_name)))
    g.add((cand, ILADUB.surfaceText, Literal(" | ".join(values))))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.suggestedAnchor, GIST.Category))
    g.add((cand, ILADUB.fromRegion, t))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    g.add((cand, ILADUB.confidence, _confidence))

    pd = URIRef("%s-promotion-%s" % (t, _slug(dimension_name)))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, t))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, _confidence))
    g.add((pd, DEC.rationale, Literal(
        "Reshape round-trips exactly with dimension=%s; the name is a model proposition, "
        "not oracle-verified. Rationale: %s" % (dimension_name, proposal.rationale))))
    g.add((pd, DEC.produced, normalized_base))
    # The alternative is the branch `certify_with_proposals` ACTUALLY takes when the proposer
    # declines or the round-trip oracle refuses (reshape.py:206 and :219, both
    # `return ProposalOutcome(None, ...)` — escalate with nothing asserted). It lost here
    # because the oracle DID certify the reshape; what it does not certify is the name.
    _deliberate(g, pd, "name the pivot dimension '%s'" % dimension_name, [
        ("escalate the nameless pivot unread",
         "round_trip certified the reshape as invertible with dimension='%s', so refusing "
         "would discard a reading the oracle admits; only the NAME is unverified"
         % dimension_name)])

    # link the UnpivotOp carrying this dimension name to its promotion
    for op in g.subjects(RDF.type, TAB.UnpivotOp):
        if str(g.value(op, TAB.opDimension)) == dimension_name:
            g.add((op, TAB.namePromotedBy, pd))
    return pd


def emit_span_promotion(g, region_uri, node_text, flank, choice, proposal):
    """Write the CandidateConcept + PromotionDecision for a NEURAL narrow-flank merge reading
    (loop B1.3). The reading is a PROPOSITION: region_tiles has confirmed it is structurally
    LEGAL, but geometry could not decide it uniquely — so it is admitted accountably, never
    asserted as grounded truth (§3). Returns the PromotionDecision uri."""
    from .membrane import suggester_agent           # R129: refuse a non-IRI suggester HERE
    agent = suggester_agent(proposal.suggester_iri)
    g.add((agent, RDF.type, ILADUB.Suggester))
    confidence = Literal(Decimal(str(round(proposal.confidence, 6))))

    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal("%s span reading: %s (flank col %d)" % (node_text, choice, flank))))
    g.add((cand, ILADUB.surfaceText, Literal(node_text)))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.suggestedAnchor, GIST.Category))
    g.add((cand, ILADUB.fromRegion, region_uri))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    g.add((cand, ILADUB.confidence, confidence))

    pd = URIRef("%s-span-promotion-%s-c%d" % (region_uri, _slug(choice), flank))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, region_uri))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, confidence))
    g.add((pd, DEC.rationale, Literal(
        "Geometry tied at narrow flank col %d; model proposed '%s'; region_tiles confirms the "
        "reading is structurally legal but NOT oracle-verified as unique — admitted as a "
        "proposition. Rationale: %s" % (flank, choice, proposal.rationale))))
    g.add((pd, DEC.produced, region_uri))
    # The tie IS the option space, and the code enumerates it: `resolve_ambiguous_merge`
    # refuses any `proposal.choice not in ("absorb", "standalone")` (span.py:90), so both were
    # live at this point and neither was ranked by an oracle — region_tiles certifies the
    # reading it was given is LEGAL, not that it is unique.
    _deliberate(g, pd, choice, [
        (other, "region_tiles confirms the '%s' reading is structurally legal but cannot rank "
                "it against '%s' at narrow flank col %d — geometry tied, so the model's "
                "proposal selected between them, not an oracle" % (choice, other, flank))
        for other in ("absorb", "standalone") if other != choice])
    return pd


def emit_row_role_promotion(g, region_uri, row_index, role, texts, proposal):
    """Write the CandidateConcept + PromotionDecision for a NEURAL header-region row-role reading
    (loop C). The reading is a PROPOSITION: region_tiles (tiling + content conservation) has
    confirmed it is structurally LEGAL and LOSSLESS, but no oracle can rank two legal readings —
    'furniture' and 'continuation' both tile and both conserve — so it is admitted accountably,
    never asserted as grounded truth (§3). Returns the PromotionDecision uri."""
    agent = _suggester(g, proposal)
    confidence = Literal(Decimal(str(round(proposal.confidence, 6))))
    surface = " ".join(texts)

    cand = BNode()
    g.add((cand, RDF.type, ILADUB.CandidateConcept))
    g.add((cand, RDFS.label, Literal("header row %d read as %s" % (row_index, role))))
    g.add((cand, ILADUB.surfaceText, Literal(surface)))
    g.add((cand, ILADUB.suggestedBy, agent))
    g.add((cand, ILADUB.suggestedAnchor, GIST.Category))
    g.add((cand, ILADUB.fromRegion, region_uri))
    g.add((cand, ILADUB.status, ILADUB.proposed))
    g.add((cand, ILADUB.confidence, confidence))

    pd = URIRef("%s-rowrole-promotion-r%d-%s" % (region_uri, row_index, _slug(role)))
    g.add((pd, RDF.type, ILADUB.PromotionDecision))
    g.add((pd, ILADUB.reviews, cand))
    g.add((pd, DEC.decidedBy, agent))
    g.add((pd, DEC.consideredEvidence, region_uri))
    g.add((pd, DEC.consideredEvidence, cand))
    g.add((pd, DEC.confidence, confidence))
    g.add((pd, DEC.rationale, Literal(
        "Header-region row %d ('%s') read as '%s'. Geometry cannot decide this (a caption and an "
        "off-center merge are structurally identical, and the wrap-pitch threshold cannot fire "
        "when header leading equals body leading); region_tiles confirms the reading is "
        "structurally legal and loses no source text, but NOT that it is unique — admitted as a "
        "proposition. Rationale: %s" % (row_index, surface, role, proposal.rationale))))
    g.add((pd, DEC.produced, region_uri))
    # The option space is `rowrole.ROLES` — the code's OWN enumeration of the legal readings
    # (rowrole.py:36), imported rather than restated so the two cannot drift. Every member is a
    # reading `build_row_reading` accepts, so each is a branch this row could have taken.
    #
    # The two rejection reasons are not one string, because the epistemic situations differ and
    # the module measured the difference (rowrole.py:16-17): tiling CANNOT discriminate
    # 'furniture' from 'continuation' — both tile and both conserve — whereas any other role
    # simply was not the reading proposed for this row.
    from .rowrole import ROLES
    _INDISCRIMINABLE = ("furniture", "continuation")
    _deliberate(g, pd, role, [
        (other,
         ("tiling cannot discriminate '%s' from '%s' — both tile and both conserve (furniture "
          "text is carried as a tab:RegionCaption), so no oracle ranked them for header row "
          "%d; the model's proposal selected between them" % (role, other, row_index))
         if role in _INDISCRIMINABLE and other in _INDISCRIMINABLE else
         ("'%s' was not the reading proposed for header row %d; region_tiles admitted the "
          "proposed '%s' reading and ranked nothing against it" % (other, row_index, role)))
        for other in ROLES if other != role])
    return pd
