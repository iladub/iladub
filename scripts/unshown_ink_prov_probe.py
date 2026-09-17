"""unshown_ink_prov_probe — does a grounded node's provenance chain reach the tab:EntryCell?

The one PROPOSED item of `docs/superpowers/2026-09-17-unshown-ink-respec-handoff.md` § 5c, and the
seam spec § 8.5 tells the implementer to MEASURE before writing clause 2 of the membrane. Clause 2
says *no asserted contract value may be sourced from a cell whose ink the page does not show*. It
can only be a SHACL shape if the graph actually joins a grounded node back to the cell.

Measurement only: compiles one document, grounds it against a real contract, and reports the join.
Writes nothing, decides nothing.

  ./.venv/bin/python scripts/unshown_ink_prov_probe.py            # graincorp-capacity
  ./.venv/bin/python scripts/unshown_ink_prov_probe.py <pdf> <page>

What it prints, and why each line is there:

  1. the EntryCell -> prov:wasDerivedFrom object census: is that object UNIQUE per cell, or do
     several cells share one? A shared object cannot discriminate one cell from its neighbour, so
     clause 2 could not name the unshown cell even if the chain reached the object.
  2. the grounded chain: GroundedNode -> iladub:wasPromotedBy -> dec:consideredEvidence ->
     iladub:fromRegion -> urn:iladub:region:<fragment>.
  3. whether <fragment> is the fragment of some cell's prov object (outcome 3, a string rewrite),
     of the cell IRI itself (outcome 1), or of neither (outcome 2).
"""
from __future__ import annotations

import os
import sys
from collections import Counter

from rdflib import Graph, Namespace, RDF, URIRef

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = Namespace("https://w3id.org/iladub/tab#")
ILADUB = Namespace("https://w3id.org/iladub#")
DEC = Namespace("https://w3id.org/iladub/dec#")
PROV = Namespace("http://www.w3.org/ns/prov#")
SHIP = Namespace("https://example.org/shipping#")

GCAP = os.path.join(REPO, "corpus", "ag-trade", "graincorp-capacity-2026-08-04.pdf")


def _frag(iri: str) -> str:
    return str(iri).split("#")[-1]


def main(pdf: str, page: int) -> None:
    from iladub.etkl import compile_tables
    from iladub.feed import ground_document
    from iladub.ground import Contract, ContractField
    from iladub.propose_ground import FakeGroundingProposer, GroundingProposal

    rep = compile_tables(pdf, page_number=page)
    dg = rep.graph
    print(f"== {os.path.basename(pdf)} p{page}: {len(dg)} triples compiled\n")

    # 1. the cell -> prov object census
    cells = sorted(dg.subjects(RDF.type, TAB.EntryCell), key=str)
    provs = {}
    for c in cells:
        p = dg.value(c, PROV.wasDerivedFrom)
        provs[c] = p
    have = [c for c in cells if provs[c] is not None]
    shared = Counter(str(provs[c]) for c in have)
    multi = {k: v for k, v in shared.items() if v > 1}
    print(f"   tab:EntryCell: {len(cells)}   carrying prov:wasDerivedFrom: {len(have)}")
    print(f"   distinct prov objects: {len(shared)}   objects shared by >1 cell: {len(multi)}")
    if multi:
        worst = sorted(multi.items(), key=lambda kv: -kv[1])[:3]
        for k, v in worst:
            print(f"       shared by {v} cells: {_frag(k)}")
    if have:
        print(f"   example: {_frag(have[0])}  ->  {_frag(provs[have[0]])}")

    # 2. ground it against the real capacity contract
    contract = Contract(str(SHIP.ElevationCapacity),
                        (ContractField(str(SHIP.fCap), str(SHIP.capacity), None),))
    terms = Graph()
    shapes = Graph().parse(os.path.join(REPO, "examples", "shipping", "capacity-shapes.ttl"),
                           format="turtle")
    abstain = FakeGroundingProposer(GroundingProposal(
        None, str(SHIP) + "x", 0.1, "n/a", "urn:iladub:suggester/fake"))
    g = Graph()
    result = ground_document(dg, contract, abstain, terms, shapes, g)
    grounded = sorted(g.subjects(RDF.type, ILADUB.GroundedNode), key=str)
    cands = sorted(g.subjects(RDF.type, ILADUB.CandidateConcept), key=str)
    print(f"\n   records={result.records} grounded={len(grounded)} "
          f"still-quarantined={result.proposed} candidate-pool={len(cands)}")

    # 3. the join, from BOTH ends: what a grounded node can reach, and what a candidate can.
    cell_frags = {_frag(c) for c in cells}
    prov_frags = {_frag(provs[c]) for c in have}

    def regions_of(node, via_pd: bool):
        out = set()
        if via_pd:
            for pd in g.objects(node, ILADUB.wasPromotedBy):
                for ev in g.objects(pd, DEC.consideredEvidence):
                    out |= set(g.objects(ev, ILADUB.fromRegion))
                for ev in g.objects(pd, ILADUB.reviews):
                    out |= set(g.objects(ev, ILADUB.fromRegion))
        else:
            out |= set(g.objects(node, ILADUB.fromRegion))
        return out

    for label, nodes, via in (("GroundedNode", grounded, True),
                              ("CandidateConcept", cands, False)):
        regs = set()
        reach_none = 0
        for n in nodes:
            r = regions_of(n, via)
            if not r:
                reach_none += 1
            regs |= r
        rf = {str(r).rsplit(":", 1)[-1] for r in regs}
        print(f"\n   {label}: {len(nodes)} nodes, {len(regs)} distinct regions reached, "
              f"{reach_none} reaching NO region")
        if rf:
            ex = sorted(rf)[:3]
            print(f"       region fragments, e.g.: {ex}")
            print(f"       fragment IS a cell IRI fragment (outcome 1): "
                  f"{len(rf & cell_frags)}/{len(rf)}")
            print(f"       fragment IS a prov-object fragment (outcome 3): "
                  f"{len(rf & prov_frags)}/{len(rf)}")
            print(f"       fragment is NEITHER (outcome 2): "
                  f"{len(rf - cell_frags - prov_frags)}/{len(rf)}")

    # 4. if the join is the prov object, is it INJECTIVE back onto one cell?
    print("\n   -- can a region fragment name ONE cell? --")
    per = Counter(_frag(provs[c]) for c in have)
    print(f"      prov fragments naming exactly 1 cell: {sum(1 for v in per.values() if v == 1)}"
          f" / {len(per)}")
    print(f"      max cells behind one prov fragment: {max(per.values()) if per else 0}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:]]
    pdf = args[0] if args else GCAP
    page = int(args[1]) if len(args) > 1 else 0
    main(pdf, page)
