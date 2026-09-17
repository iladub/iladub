"""Grounding oracle power — for each question the grounding proposer is asked on the corpus, how
many of the contract's fields would the oracle ADMIT if the proposer named them?

The adversarial review of `specs/2026-09-17-neural-worker-foundation-design.md` asks whether
`_grounds_to` disposes the proposer's CHOICE of field or only the VALUE's fit to whichever field is
named. `_grounds_to(is_exact=False)` admits a proposed field only through scheme membership or the
field's SHACL value constraint, and refuses outright a field with neither. So per asked cell, the
admitting set A = {f in contract.fields : _grounds_to(concept, f, ..., is_exact=False) is not None}:

  |A| = 0  -> no proposal can ever be admitted; the worker cannot change the outcome.
  |A| = 1  -> the oracle alone decides; the worker is redundant (an AXIOM could name the field).
  |A| >= 2 -> the oracle cannot discriminate the options; the model's choice goes unchecked.

Only |A| >= 2 WITH a discriminating second signal would make a worker both useful and disposed.
CONTROL: exact-label concepts are NOT asked (they never reach the proposer); as a positive
control the script also computes A for one exact-matched concept per document and requires the
exactly-matched field to be in A when that field is constrained.

Same entry and one-document-per-process discipline as `neural_seam_population.py`.

    PYTHONPATH=src .venv/bin/python scripts/grounding_oracle_power.py <out-dir>

Gate classification (CLAUDE.md §8): PROCEDURAL. It calls the shipped oracle and counts.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from reach_probe import SHORT, manifest  # noqa: E402


def run_one(entry, out_dir):
    from rdflib import Graph, URIRef
    from iladub.etkl.document import compile_document
    from iladub.feed import ground_document
    from iladub.ground import load_contract, _grounds_to, exact_field
    from iladub.propose_ground import GroundingProposal

    contract = load_contract(str(REPO / entry["contract"]))
    terms = Graph().parse(str(REPO / entry["terms"]), format="turtle")
    shapes = Graph().parse(str(REPO / entry["shapes"]), format="turtle")
    offer = URIRef("urn:iladub:oracle-power#offer")
    memo = {}

    def admitting(concept):
        out = []
        for f in contract.fields:
            k = (concept.value, f.iri)
            if k not in memo:
                memo[k] = _grounds_to(concept, f, terms, False, shapes, offer,
                                      contract.target_class)[0] is not None
            if memo[k]:
                out.append(f.fills_property.rsplit("#", 1)[-1].rsplit("/", 1)[-1])
        return tuple(sorted(out))

    per_text = defaultdict(Counter)

    class Probe:
        def propose_grounding(self, concept, fields, page_context=None):
            per_text[concept.text][admitting(concept)] += 1
            return GroundingProposal(None, "https://w3id.org/semanticarts/ns/ontology/gist/Category",
                                     0.0, "abstain", "urn:iladub:suggester/oracle-power")

    rep = compile_document(str(REPO / "corpus" / entry["file"]))
    ground_document(rep.graph, contract, Probe(), terms, shapes, Graph(), validate_shapes=False)

    # positive control: exact-matched concepts, whose field is known
    from iladub.feed import table_records
    control = []
    for rec in table_records(rep.graph):
        for c in rec.concepts:
            f = exact_field(c, contract)
            if f is not None and len(control) < 3:
                control.append({"text": c.text, "value": c.value,
                                "field": f.fills_property.rsplit("#", 1)[-1],
                                "scheme": f.scheme, "A": admitting(c)})
        if len(control) >= 3:
            break
    stem = Path(entry["file"]).stem
    out = {"short": SHORT.get(stem, stem),
           "fields": [f.fills_property.rsplit("#", 1)[-1] + (" [scheme]" if f.scheme else "")
                      for f in contract.fields],
           "per_text": {t: {"|".join(a) or "<none>": n for a, n in c.items()}
                        for t, c in per_text.items()},
           "control": control}
    (Path(out_dir) / f"{stem}.json").write_text(json.dumps(out, indent=1))
    sizes = Counter()
    for c in per_text.values():
        for a, n in c.items():
            sizes[len(a)] += n
    print(f"{out['short']:>6}: cells by |A| {dict(sorted(sizes.items()))}")


def main(argv):
    out_dir = argv[1]
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if len(argv) > 2:
        run_one(json.loads(argv[2]), out_dir)
        return
    for e in manifest():
        if e["contract"] and (REPO / "corpus" / e["file"]).is_file():
            subprocess.run([sys.executable, __file__, out_dir, json.dumps(e)], check=True)


if __name__ == "__main__":
    main(sys.argv)
