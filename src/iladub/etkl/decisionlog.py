"""decisionlog — the reading, recorded as evidence (spec 2026-08-07).

iladub records the LAST step of its reasoning (iladub:PromotionDecision) and discards the
rest: the reading that precedes it returns a kind and a reason string, the alternatives are
never named, and the moment a branch is taken the others cease to exist. This module gives
that reading a record, using only the OWNED dec: vocabulary — whose differential half
(dec:optionSpace / dec:chosen / dec:rejectedBecause) had no producer before this loop.

Gate classification (CLAUDE.md §8): PROCEDURAL engine glue. It makes no domain decision — it
records ones already made at the call site, and no judgement function is modified.

MEMBRANE HAZARD (spec §3.1): a recorder must be given the DOCUMENT graph, never a region's
scratch graph. Decisions in a graph that region_tiles validates is the R19 hazard again — a
shape firing on something that is not what it thinks it is.
"""
from __future__ import annotations

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS, PROV

DEC = Namespace("https://w3id.org/iladub/dec#")

# Module-level default agent: the iladub reading compiler.
_READER_AGENT = URIRef("https://w3id.org/iladub/etkl#reader")


class BandRecorder:
    """Records the judgement sequence for one band. `dec:order` counts within the band."""

    def __init__(self, graph: Graph, band_node: URIRef, region_uri: URIRef, prefix: str,
                 agent: URIRef):
        self._g = graph
        self._band = band_node
        self._regarding = region_uri
        self._prefix = prefix
        self._agent = agent
        self._n = 0

    def record(self, judgement: str, options, chosen, rationale: str,
               rejected: dict | None = None, evidence=None) -> URIRef:
        """One judgement. `options` are candidate names; `chosen` is one of them.
        `rejected` maps a candidate name to the observation that refuted it."""
        if len(options) < 2:
            raise ValueError(f"A real decision needs at least 2 options; got {len(options)}")
        if chosen not in options:
            raise ValueError(f"chosen '{chosen}' is not in options {options}")

        g = self._g
        d = URIRef(f"{self._prefix}-d{self._n}")
        g.add((d, RDF.type, DEC.DecisionHolon))
        g.add((d, RDFS.label, Literal(judgement)))
        g.add((d, DEC.regarding, self._regarding))
        g.add((d, DEC.withinProcess, self._band))
        g.add((d, DEC.decidedBy, self._agent))
        g.add((d, DEC.order, Literal(self._n, datatype=XSD.integer)))
        g.add((d, DEC.rationale, Literal(rationale)))
        rejected = rejected or {}
        for name in options:
            o = URIRef(f"{d}-opt-{_slug(name)}")
            g.add((o, RDF.type, DEC.Option))
            g.add((o, RDFS.label, Literal(str(name))))
            g.add((d, DEC.optionSpace, o))
            if str(name) == str(chosen):
                g.add((d, DEC.chosen, o))
            elif str(name) in rejected:
                g.add((o, DEC.rejectedBecause, Literal(rejected[str(name)])))
        for e in (evidence or ()):
            g.add((d, DEC.consideredEvidence, e))
        self._n += 1
        return d


class ReadingRecorder:
    """One per page compile. Mints the page process under the document, and a band process
    under the page, so dcterms:isPartOf carries document -> page -> band -> judgement."""

    def __init__(self, graph: Graph, doc_uri: URIRef, page: int,
                 agent: URIRef | None = None):
        self._g = graph
        self._doc = doc_uri
        self._page = page
        self._agent = agent or _READER_AGENT
        self._page_node = URIRef(f"{doc_uri}#p{page}-reading")

        # Emit agent once per recorder.
        graph.add((self._agent, RDF.type, PROV.SoftwareAgent))
        if agent is None:
            # Only label the default agent; caller agents are expected to be pre-labelled.
            graph.add((self._agent, RDFS.label, Literal("iladub reading compiler", lang="en")))

        # Page is a dec:Process, not a decision. NO dec:regarding here (final-review I5):
        # dec:regarding's rdfs:domain is dec:DecisionHolon (widened on this branch only to
        # unionOf(dec:DecisionHolon, dec:ExpansionRequest)), and a dec:Process is neither —
        # emitting it on a container asserted a term outside its own declared domain. The
        # structure the containers carry is dcterms:isPartOf; the JUDGEMENTS keep their own
        # dec:regarding, which is the only thing the committed queries read (all three bind
        # `?d a dec:DecisionHolon`, so a container never matched them anyway).
        graph.add((self._page_node, RDF.type, DEC.Process))
        graph.add((self._page_node, RDFS.label, Literal(f"reading page {page}")))
        graph.add((self._page_node, DCTERMS.isPartOf, doc_uri))

    def band(self, idx: int) -> BandRecorder:
        prefix = f"{self._doc}#region{idx}"
        band_node = URIRef(f"{prefix}-reading")
        # Band is a dec:Process, not a decision — see the page node above for why it carries
        # no dec:regarding.
        self._g.add((band_node, RDF.type, DEC.Process))
        self._g.add((band_node, RDFS.label, Literal(f"reading band {idx}")))
        self._g.add((band_node, DCTERMS.isPartOf, self._page_node))
        return BandRecorder(self._g, band_node, URIRef(prefix), prefix, self._agent)


def _slug(name) -> str:
    return "".join(c if c.isalnum() else "_" for c in str(name))
