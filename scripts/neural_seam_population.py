"""NEURAL seam population — how often each shipped proposer seam is REACHED on the corpus.

The NEURAL worker foundation (handoff `2026-09-17-neural-workers-handoff.md` § 5a) proposes an
eval harness scored by the oracle's acceptance rate "over recorded contexts". That presumes the
corpus produces contexts. No production entry point constructs a live proposer (every
`compile_document` call in `src/` and `scripts/` passes none), so nothing has ever counted how
often a seam would be asked. This script counts it.

Method: inject an ABSTAINING, COUNTING proposer into each seam the document path exposes —
`compile_document(span_proposer=, row_role_proposer=)` always, and `ground_document(proposer=)`
where the corpus manifest names a contract. Abstention returns `None` (span/row-role) or a
`field_iri=None` proposal (grounding), which is the branch each seam already takes when no live
proposer exists, so the reading is unchanged. Each call's context is kept, so the population's
SHAPE (not only its size) is on the record.

CONTROL: the row-role seam is also counted against the escalations it replaces. Every compile
branch that reaches it without resolving books `MERGE_AMBIGUOUS` (`compile.py`, the `else:` under
`not merge_tiling_ok`), so calls == MERGE_AMBIGUOUS regions must hold, per document. A counting
proposer that was never wired would report 0 calls AND could not satisfy that identity on a
document that escalates MERGE_AMBIGUOUS — the identity is what makes a 0 mean "unreached".

Seams NOT reachable from the document path, and therefore not counted here (measured by grep,
2026-09-17): `certify_with_proposals` (ProposeDimensionName) and `resolve_split_key_name`
(ProposeSplitKeyName) are called from tests only.

ONE DOCUMENT PER PROCESS, for the reason `reach_probe.py` records (memoised membranes) and
because corpus compiles are memory-heavy — never run two of these at once.

    PYTHONPATH=src .venv/bin/python scripts/neural_seam_population.py run  <out-dir>
    PYTHONPATH=src .venv/bin/python scripts/neural_seam_population.py report <out-dir>

Gate classification (CLAUDE.md §8): PROCEDURAL. It counts calls and writes them down; it decides
nothing about any document and carries no tolerance.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from reach_probe import SHORT, manifest  # noqa: E402  (the corpus register, read once)


class _Counting:
    def __init__(self):
        self.span, self.rowrole, self.grounding = [], [], []

    # SpanProposer / RowRoleProposer protocol — abstain
    def propose_header_span(self, context):
        self.span.append({k: repr(v) for k, v in context.items()})
        return None

    def propose_header_row_roles(self, context):
        self.rowrole.append({k: repr(v) for k, v in context.items()})
        return None

    # GroundingProposer protocol — abstain (field_iri=None -> quarantine, as with no proposer)
    def propose_grounding(self, concept, fields, page_context=None):
        from iladub.propose_ground import GroundingProposal
        self.grounding.append({"text": concept.text, "value": concept.value,
                               "n_fields": len(fields),
                               "has_page_context": page_context is not None})
        return GroundingProposal(None, "https://w3id.org/semanticarts/ns/ontology/gist/Category",
                                 0.0, "abstain", "urn:iladub:suggester/seam-census")


def run_one(entry, out_dir):
    from rdflib import Graph
    from iladub.etkl.document import compile_document

    pdf = REPO / "corpus" / entry["file"]
    stem = Path(entry["file"]).stem
    c = _Counting()
    rep = compile_document(str(pdf), span_proposer=c, row_role_proposer=c)
    reasons = {}
    for page in rep.pages:
        for r in page.regions:
            key = f"{r.verdict}:{r.reason}"
            reasons[key] = reasons.get(key, 0) + 1
    if entry["contract"]:
        from iladub.feed import ground_document
        from iladub.ground import load_contract
        ground_document(rep.graph, load_contract(str(REPO / entry["contract"])), c,
                        Graph().parse(str(REPO / entry["terms"]), format="turtle"),
                        Graph().parse(str(REPO / entry["shapes"]), format="turtle"),
                        Graph(), validate_shapes=False)
    out = {"file": entry["file"], "short": SHORT.get(stem, stem), "score": rep.score,
           "contract": bool(entry["contract"]), "reasons": reasons,
           "span": c.span, "rowrole": c.rowrole, "grounding": c.grounding}
    (Path(out_dir) / f"{stem}.json").write_text(json.dumps(out, indent=1))
    print(f"{out['short']:>6}: span={len(c.span)} rowrole={len(c.rowrole)} "
          f"grounding={len(c.grounding)}")


def report(out_dir):
    rows = [json.loads(f.read_text()) for f in sorted(Path(out_dir).glob("*.json"))]
    print(f"{'doc':>6} {'score':>7} {'span':>5} {'rowrole':>7} {'MERGE_AMB':>9} "
          f"{'identity':>8} {'grounding':>9} {'ctx':>4}")
    tot = {"span": 0, "rowrole": 0, "grounding": 0}
    for j in rows:
        merge = sum(v for k, v in j["reasons"].items() if k.endswith(":MERGE_AMBIGUOUS"))
        ident = "ok" if len(j["rowrole"]) == merge else "BROKEN"
        ctx = sum(1 for x in j["grounding"] if x["has_page_context"])
        print(f"{j['short']:>6} {j['score']:>7.4f} {len(j['span']):>5} {len(j['rowrole']):>7} "
              f"{merge:>9} {ident:>8} {len(j['grounding']) if j['contract'] else '-':>9} {ctx:>4}")
        for k in tot:
            tot[k] += len(j[k])
    print(f"{'total':>6} {'':>7} {tot['span']:>5} {tot['rowrole']:>7} {'':>9} {'':>8} "
          f"{tot['grounding']:>9}")
    blank = sum(1 for j in rows for x in j["grounding"] if x["text"] == "")
    distinct = len({(x["text"]) for j in rows for x in j["grounding"]})
    print(f"grounding calls with empty surface text: {blank}; distinct surface texts: {distinct}")


def main(argv):
    cmd, out_dir = argv[1], argv[2]
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if cmd == "run":
        for e in manifest():
            if not (REPO / "corpus" / e["file"]).is_file():
                print(f"SKIP (not populated): {e['file']}")
                continue
            subprocess.run([sys.executable, __file__, "one", out_dir, json.dumps(e)], check=True)
    elif cmd == "one":
        run_one(json.loads(argv[3]), out_dir)
    elif cmd == "report":
        report(out_dir)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
