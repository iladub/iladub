"""Furniture field names ([[R250]]) — does any contract field's name occur in a document's carried
furniture (`feed._page_context`), and which asks reach the grounding proposer with a non-empty
admitting set A?

Per contracted corpus document: the furniture text, and for each contract field whether its
property local name occurs in it (normalised substring, all camelCase parts as words, and which
parts). Then every ask the proposer receives, keyed by the concept's text and A, with its values
counted as `zero` (the literal `0`, [[R213]]'s invisible glyphs on gcap), `num`, or `other`.

Same one-document-per-process discipline as `grounding_oracle_power.py`; corpus runs are serial.

    PYTHONPATH=src .venv/bin/python scripts/furniture_field_names.py > out.json

Gate classification (CLAUDE.md §8): PROCEDURAL. It calls the shipped feed and oracle and counts;
it decides nothing.
"""
import json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from reach_probe import SHORT, manifest

def words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower())}

def split_camel(n):
    return [p.lower() for p in re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", n)]

def run_one(e):
    from rdflib import Graph, URIRef
    from iladub.etkl.document import compile_document
    from iladub.feed import ground_document, _page_context
    from iladub.ground import load_contract, _grounds_to, _norm
    from iladub.propose_ground import GroundingProposal
    contract = load_contract(str(REPO / e["contract"]))
    terms = Graph().parse(str(REPO / e["terms"]), format="turtle")
    shapes = Graph().parse(str(REPO / e["shapes"]), format="turtle")
    offer = URIRef("urn:r250#offer")
    rep = compile_document(str(REPO / "corpus" / e["file"]))
    ctx = _page_context(rep.graph) or ""
    W = words(ctx); N = _norm(ctx)
    fields = {}
    for f in contract.fields:
        name = f.fills_property.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
        parts = split_camel(name)
        fields[name] = {"norm_substring": _norm(name) in N,
                        "all_words": all(p in W for p in parts),
                        "any_word": [p for p in parts if p in W],
                        "scheme": bool(f.scheme)}
    asks = defaultdict(Counter)
    memo = {}
    class Probe:
        def propose_grounding(self, c, flds, page_context=None):
            A = []
            for f in contract.fields:
                k = (c.value, f.iri)
                if k not in memo:
                    memo[k] = _grounds_to(c, f, terms, False, shapes, offer, contract.target_class)[0] is not None
                if memo[k]:
                    A.append(f.fills_property.rsplit("#", 1)[-1])
            vk = "zero" if c.value.strip() == "0" else ("num" if re.fullmatch(r"[\d,]+", c.value.strip()) else "other")
            asks[(c.text, "|".join(A) or "-")][vk] += 1
            return GroundingProposal(None, "https://w3id.org/semanticarts/ns/ontology/gist/Category", 0.0, "abstain", "urn:r250")
    ground_document(rep.graph, contract, Probe(), terms, shapes, Graph(), validate_shapes=False)
    stem = Path(e["file"]).stem
    print(json.dumps({"doc": SHORT.get(stem, stem), "context": ctx, "fields": fields,
                      "asks_with_nonempty_A": {f"{t!r} A={a}": dict(v) for (t, a), v in asks.items() if a != "-"},
                      "asked_texts_total": len(asks)}, indent=1))

if len(sys.argv) > 1:
    run_one(json.loads(sys.argv[1]))
else:
    for e in manifest():
        if e["contract"] and (REPO / "corpus" / e["file"]).is_file():
            subprocess.run([sys.executable, __file__, json.dumps(e)], check=True)
