# Handoff: R301's guard runs before adoption, and p5 stops contradicting its graph (2026-10-08)

**Serves:** maintenance. This is [[R301]], continuing `2026-10-08-r301-guard-prototype-handoff.md`
(PR #320), whose § 5.1 asked this session to run one PROPOSED prediction before anything was
written on it.

**Topic:** compile · **Date:** 2026-10-08

**Doc impact: none.** This adds one probe script and this handoff. No vocabulary, shape or compile
path changed. The compile hook the probe needs was applied locally, run, and reverted. Its diff is
in § 2.

## 5. Next concrete action (written first, at about 45K working tokens, under the 50K floor)

1. **ASSERTED: write R301's spec in a fresh session.** The predecessor's § 5.2 lists four rulings.
   Their inputs are now all measured, and § 1 of this file adds a fifth:
   - **(a) Position: settled by measurement (G1).** Run differencing, then carry, then the guard,
     then adoption, then the existing carry, score and validate. On fed-h41 the existing post-carry
     position never sees a refused cell (G2). The spec should keep the membrane as the backstop
     there, not add a second guard.
   - **(b) Extent:** a closure over blank nodes only, as in the predecessor's F4.
   - **(c) Refusal decision:** one `dec:DecisionHolon` per withdrawn table, chained through
     `_effective_verdict` (F5). Whether `{t}-admission` stays is decided by the 2026-09-29 "the log
     is a boundary" ruling.
   - **(d) Escalation text of an appended region** (F7).
   - **(e) The ledger's appended-region term (G3).** Either rule that a guard-escalated appended
     region is excluded from `build_ledger`'s booked set, or rule that the double count stays
     because it refuses re-adoption by construction. In either case the spec must say which one,
     because the guard creates the first escalated appended region.
   *Confidence: high that these five are the open rulings. None is made here.* The spec should
   pin p5 = 187/64 (0.7450), p7 = 0/137 and the document = 2739/663 (0.8051) as its corpus oracle
   on fed-h41. G1 measured these with a guard that still deletes the admission root and escalates
   p7 with placeholder text, so (c) and (d) may move the figures for the graph but not for the
   ledger.

## 1. What was measured

The run was `scripts/r301_guard_position_probe.py pre` at `69eb44b` plus the § 2 hook, with
`validate_shapes=True`. It took 215 s. The baseline was `scripts/r301_guard_prototype.py base` at
the same commit, with no hook and `validate_shapes=False`. It took 196 s.

- **G1. CONFIRMED: the predecessor's § 5.1 prediction holds.** With the guard placed before the
  adoption branch, p5's `/adopt` re-compile withdraws `p5/adopt#htable3` (113 triples) before it
  adopts. Region 3 of the installed report reads `escalated RULE_SEPARATED_INK 26`, and the document
  graph's only region-3 node is the pass-1 candidate `p5#region3`. **The graph and the report now
  agree** where the after-adoption position left them contradicting each other (the predecessor's
  F2). The document compiles under validation, and refused cells in the document graph go from 13
  to 0. The per-region ledgers hold on all 11 pages (asserted in the probe).

  | page | baseline A/E (score) | guard before adoption A/E (score) |
  |---|---|---|
  | p5 | 213/38 (0.8486) | 187/64 (0.7450) |
  | p7 | 137/0 (1.0000) | 0/137 (0.0000) |
  | document | 2902/500 (0.8530) | 2739/663 (0.8051) |

  **No other page moves.** p0–p4, p6 and p8–p10 are identical, region by region, to the baseline,
  and so is the adopted set (2, 3, 5, 8, 10). This answers the predecessor's § 4 "does an
  escalation added before adoption change any other page's adoption outcome" for fed-h41: it does
  not. The R300 dangling list loses p5 (its region 3 no longer names a table). p3 `adopt#htable7`
  and p10 `adopt#htable3` stay on it, unchanged, because they belong to R300 and not to R301. One
  note is added: `page 7: adoption refused — no data grid region on the re-compile`.
- **G2. The post-carry position finds nothing once the guard runs first.** The hook also ran after
  the existing `carry_from_pdf` in count-only mode. It logged **no** refused cell on any compile:
  not on any pass-1 page, any pass-2 page, or either `/adopt` re-compile. So a guard at both
  positions would have produced the same run, and the `both` mode was not run for that reason.
- **G3. p7's grid cannot be re-adopted, but only because the ledger double-counts.** In p7's
  `/adopt` re-compile the guard escalates the fallback grid (region 3, appended after 3 bands).
  The adoption gate then opens (`escalated_total = 137 > 0`) and derives the same grid, and the
  ledger reads **asserted 137, escalated 137, touched {1}**. That is 274 tokens on a 137-token
  page. The strict-less gate refuses on the tie. Measured by tracing `build_ledger` in
  `compile_tables(fed-h41, 7, datagrid_adopt=True)`. The mechanism is in `adoption.py`'s
  `build_ledger`: `booked_bands` enumerates **`reports`**, which includes the appended region at
  index 3, while `touched` ranges over **`range(len(bands))`** only. So the appended region is
  never touched, and its 137 escalated tokens enter the untouched term even though the grid admits
  the same lines. Because that term always contains the appended region's own escalation, the
  ledger's escalated count is always ≥ `escalated_total` on such a page, and **re-adoption is
  refused by construction**. The construction is an accounting artefact, though, not knowledge
  that the grid was refused. Before the guard this was unreachable, because an appended region was
  always asserted.
- **G4. The second carry costs nothing observable.** `carry_rule_ink` mints deterministic IRIs
  (`{doc}#rule-p{page}-{k}`, plus literals on existing cells), so running it twice is idempotent.
  The guarded document run took 215 s, against 227 s for the predecessor's after-adoption guard
  and 196 s for the unguarded baseline. That is a single run each, so it shows no measurable cost
  and does not establish a bound. One side effect for the spec: when a withdrawal removes every
  cell on a page, that page's `tab:RuleSpan` nodes remain without cells (p7). They are harmless to
  the shape, which joins on a cell.

## 2. Where the primaries are

- The probe: `scripts/r301_guard_position_probe.py` (modes `pre` and `both`). It reads its query
  from `scripts/r301_guard_prototype.py`. Its output is not committed. Re-run it with the hook
  below applied.
- The hook, which was applied for the run and reverted, and is **never to be committed**:

  ```diff
  +_R301_HOOK = None
  +
   def compile_tables(pdf_path: str, page_number: int = 0,
  ...
  +    if _R301_HOOK is not None:   # THROWAWAY probe hook (r301 position), never committed
  +        from .ruleink import carry_from_pdf as _cfp
  +        _cfp(graph, str(doc), pdf_path)
  +        graph, reports, asserted_total, escalated_total = _R301_HOOK(
  +            'pre', graph, reports, asserted_total, escalated_total, doc, page_number, pdf_path)
       if datagrid_adopt and escalated_total > 0:
  ...
       from .ruleink import carry_from_pdf
       carry_from_pdf(graph, str(doc), pdf_path)
  +    if _R301_HOOK is not None:   # THROWAWAY probe hook
  +        graph, reports, asserted_total, escalated_total = _R301_HOOK(
  +            'post', graph, reports, asserted_total, escalated_total, doc, page_number, pdf_path)
  +        denom = asserted_total + escalated_total
  +        if denom: score = asserted_total / denom
  ```

- The ledger: `src/iladub/etkl/adoption.py`, `build_ledger` (`booked_bands` against `touched`).
- Everything else is as in the predecessor's § 2.

## 3. What was decided

Nothing. G1 settles ruling (a) as a measurement. The spec still has to rule it.

## 4. Unverified

- The `both` mode was not run (G2 says it would equal `pre` on fed-h41).
- Whether the guard is the identity on the other 10 corpus documents. Loop 3's census found the
  predicate firing on 0 of their cells, so this is inferred and was not re-run with the guard.
- Rulings (c) and (d) change the graph a withdrawal leaves (the admission root, and the
  appended region's text), but not the ledger. This is reasoned, not run.
