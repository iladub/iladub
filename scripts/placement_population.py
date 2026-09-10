"""The cells a model-backed GroundingProposer could ever touch, per contracted corpus document.

WHY THIS EXISTS. A proposer sits behind `exact_field` (`src/iladub/ground.py`, `ground_concept`):
it is asked only about a cell whose column label matches no contract field, and whatever it
proposes is admitted only by an oracle — a field's `etkl:admissibleScheme` or a SHACL value
constraint (`_grounds_to`). So before pricing any model in that seam, count two populations:
the RAW one (cells the proposer is asked about) and the CEILING (raw cells whose value some
oracle-bearing field would admit). Cheap times zero is zero. Written for the GLiNER2 handoff
`docs/superpowers/2026-09-10-gliner2-population-count-handoff.md` § 5a; the figures it produced
are in `docs/superpowers/2026-09-10-gliner2-the-count-handoff.md`.

WHAT IT MEASURES. For every `SurfaceConcept` of every record `table_records` yields, the branch
`ground_concept` would take, replayed without a proposer and without emitting a graph:
  exact-grounded  exact_field hit, the field's oracle admitted the value
  exact-refused   exact_field hit, the oracle refused (quarantine)
  novel           exact_field None -> the proposer would be asked (the RAW population)
and for the novel cells, whether ANY oracle-bearing field admits the value as it stands
(the CEILING — what a perfect proposer could add; a proposer only ever names contract fields).

WHAT IT DOES NOT MEASURE. Whether a ceiling cell SHOULD ground there: a section marker whose
text is a port's prefLabel is counted as admissible on the port field, which is a claim about
the oracle, not about the page. Read the ceiling's label breakdown before believing the number.

RUN. From the repo root, with the corpus populated (`scripts/fetch_corpus.py`):
    PYTHONPATH=. .venv/bin/python scripts/placement_population.py
Only the manifest documents carrying a `cor:contract` are measured; the others have no
grounding leg (`tests/corpus-manifest.ttl`). Each document compiles from scratch, so expect
minutes, not seconds.
"""
import collections
import sys
from pathlib import Path

from rdflib import BNode, Graph, URIRef

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from iladub.etkl.document import compile_document  # noqa: E402
from iladub.feed import table_records  # noqa: E402
from iladub.ground import (  # noqa: E402
    _grounds_to, _has_value_constraint, _property_shape, _value_conforms,
    exact_field, load_contract, scheme_member,
)

# (corpus file, examples/shipping/<stem>-{contract,terms,shapes}.ttl) — the two contracted
# manifest entries. Read the manifest, not this table, for the authoritative binding.
DOCS = (("ag-trade/graincorp-stem-2026-07-31.pdf", "stem"),
        ("ag-trade/cbh-stem-2026-08-03.pdf", "cbh"))


def _short(iri):
    return iri.split("#")[-1].split("/")[-1]


def measure(pdf, ex):
    contract = load_contract(str(REPO / f"examples/shipping/{ex}-contract.ttl"))
    terms = Graph().parse(str(REPO / f"examples/shipping/{ex}-terms.ttl"), format="turtle")
    shapes = Graph().parse(str(REPO / f"examples/shipping/{ex}-shapes.ttl"), format="turtle")
    oracle_fields = []
    for f in contract.fields:
        ps = _property_shape(shapes, f.fills_property)
        if f.scheme:
            oracle_fields.append((f, "scheme"))
        elif ps is not None and _has_value_constraint(shapes, ps):
            oracle_fields.append((f, "value-constraint"))

    rep = compile_document(str(REPO / "corpus" / pdf))
    recs = table_records(rep.graph)
    tally = collections.Counter()
    novel, refused = [], []
    for rec in recs:
        subj = URIRef("urn:iladub:probe:" + rec.row_id.replace(" ", "_"))
        for c in rec.concepts:
            f = exact_field(c, contract)
            if f is None:
                tally["novel"] += 1
                novel.append(c)
                continue
            target, _ = _grounds_to(c, f, terms, True, shapes, subj, contract.target_class)
            if target is None:
                tally["exact-refused"] += 1
                refused.append(c)
            else:
                tally["exact-grounded"] += 1

    ceiling = []
    for c in novel:
        for f, kind in oracle_fields:
            admits = (scheme_member(c.value, f.scheme, terms) is not None if kind == "scheme"
                      else _value_conforms(BNode(), contract.target_class, f.fills_property,
                                           c.value, shapes))
            if admits:
                ceiling.append((c, f))
                break

    print(f"\n=== {pdf}  score={rep.score:.4f} records={len(recs)} cells={sum(tally.values())}")
    print("  fields:", [(_short(f.fills_property), f.scheme is not None) for f in contract.fields])
    print("  oracle-bearing:", [(_short(f.fills_property), k) for f, k in oracle_fields])
    print("  tally:", dict(tally))
    print(f"  RAW (novel): {len(novel)} cells, {len({c.text for c in novel})} distinct labels, "
          f"{len({c.value for c in novel})} distinct values, "
          f"{len({(c.text, c.value) for c in novel})} distinct (label, value), "
          f"{sum(c.is_section_marker for c in novel)} section markers")
    print("  novel labels:", collections.Counter(c.text for c in novel).most_common())
    print(f"  CEILING (novel values some oracle admits): {len(ceiling)}",
          collections.Counter((c.text, _short(f.fills_property)) for c, f in ceiling).most_common())
    print(f"  exact-refused: {len(refused)}",
          collections.Counter((c.text, c.value) for c in refused).most_common(20))


if __name__ == "__main__":
    for pdf, ex in DOCS:
        if not (REPO / "corpus" / pdf).is_file():
            print(f"SKIP (not populated): {pdf}")
            continue
        measure(pdf, ex)
