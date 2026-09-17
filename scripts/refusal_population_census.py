"""Where does iladub still REFUSE, at HEAD? The population any comparison must be drawn from.

Written 2026-09-17 for the docling-graph benchmark, and committed rather than left in a
scratchpad because [[R245]] was raised the same morning for exactly that defect: a
measurement whose instrument nobody can re-run is not a measurement.

WHY IT EXISTS. Two inherited figures were both stale, and the benchmark's document choice
depended on them:

    apple p1   2026-08-15: score 0.117, 151/171 escalated  ->  2026-09-17: 1.0000, 0 escalated
    cbh   p0   2026-08-15: score 0.0603, 842 escalated      ->  2026-09-17: 0.9095, 80 escalated

A refusal benchmark aimed at a population nobody re-measured is the R234 failure (0/191
bands). This prints the population instead of assuming it.

WHAT IT REPORTS. Per page: score, asserted/escalated tokens, and every region carrying
escalated ink, with its reason -- so the escalated set can be read by CAUSE
(DATAGRID_RESIDUE, KIND_NOT_SUPPORTED, REGION_TILING_FAILED, ROUND_TRIP_FAIL) and not
merely by size. A JSON dump beside the text output feeds downstream harnesses.

CAUTION, measured on this machine: a full pass is ~430 s and corpus compiles must run
SERIALLY -- five memory kills are on record. Never run two at once.

Gate classification (CLAUDE.md s8): PROCEDURAL. Raw extraction plus counting over an
existing accounting; it makes no reading decision and carries no tolerance.
"""
import json
import pathlib
import sys
import time

sys.path.insert(0, "src")
from iladub.etkl.document import compile_document

OUT_JSON = "refusal_population.json"


def main() -> None:
    out, t_all = [], time.time()
    for pdf in sorted(pathlib.Path("corpus").rglob("*.pdf")):
        t0 = time.time()
        try:
            rep = compile_document(str(pdf), validate_shapes=False)
        except Exception as exc:                       # noqa: BLE001 - census must not abort
            print(f"[{pdf.stem[:30]:<31}] FAILED {type(exc).__name__}: {exc}", flush=True)
            continue
        for page, prep in enumerate(rep.pages):
            regions = [{"i": i, "verdict": str(r.verdict),
                        "kind": str(getattr(r, "kind", "")),
                        "anchor": str(getattr(r, "anchor", "")).split("#")[-1],
                        "asserted": r.tokens_asserted, "escalated": r.tokens_escalated,
                        "reason": str(getattr(r, "reason", ""))[:60]}
                       for i, r in enumerate(prep.regions)]
            out.append({"doc": pdf.stem, "page": page, "score": prep.score,
                        "asserted": prep.asserted, "escalated": prep.escalated,
                        "adopted": page in rep.adopted, "regions": regions})
        print(f"[{pdf.stem[:30]:<31}] {len(rep.pages):>2}p  {time.time() - t0:5.1f}s", flush=True)

    print(f"\nTOTAL {time.time() - t_all:.0f}s over {len(out)} pages\n")
    print(f"{'document':<30}{'pg':>3}{'score':>9}{'asrt':>7}{'esc':>7}  regions escalated")
    tot_a = tot_e = 0
    for row in sorted(out, key=lambda r: r["score"]):
        esc = [r for r in row["regions"] if r["escalated"] > 0]
        tot_a += row["asserted"]
        tot_e += row["escalated"]
        print(f"{row['doc'][:29]:<30}{row['page']:>3}{row['score']:>9.4f}"
              f"{row['asserted']:>7}{row['escalated']:>7}  "
              + ",".join(f"{r['i']}:{r['escalated']}({r['anchor'][:12]})" for r in esc))

    denom = tot_a + tot_e
    print(f"\nCORPUS TOTAL asserted={tot_a} escalated={tot_e} "
          f"ratio={tot_a / denom:.4f}" if denom else "\nCORPUS TOTAL empty")
    print(f"PAGES WITH ANY ESCALATION: {sum(1 for r in out if r['escalated'] > 0)} of {len(out)}")

    print("\n=== THE POPULATION (escalated regions, descending) ===")
    allesc = [(r["escalated"], row["doc"], row["page"], r["i"], r["anchor"], r["kind"], r["reason"])
              for row in out for r in row["regions"] if r["escalated"] > 0]
    for e, d, p, i, anc, kind, why in sorted(allesc, reverse=True):
        print(f"  {e:>5} tok  {d[:26]:<27} p{p} r{i:<3} {anc[:22]:<23} "
              f"{kind[:18]:<19} {why[:34]}")

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print(f"\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
