# Handoff: R288 scope probe — census done, truth set and prompt await the maintainer (2026-10-05)

**Topic:** r288-scope-probe · **Date:** 2026-10-05

**Serves:** prog:criterion:etkl:03 — R288: the scope probe from the 2026-10-04 handoff, part 5.

**Doc impact: none.**

Written at ~51K working tokens, just past the 50K originating floor. Part 5 was written first.

## 5. Next action (written first)

- **Proposed. Run it, and it may refute.** With the maintainer, settle the three open decisions in
  § 4 (labels, ons p4, the truth list). Write `truth.json` in the census output directory as a JSON
  list of `[doc_stem, page, band]`. Then run `scripts/r288_scope_probe.py live`. It prints `VERDICT:
  HOLDS | REFUTED` under the rule fixed in § 3, before any call. The prediction is that the
  composite admits exactly the notes whose qualified tables are asserted. § 4 items 1 and 2 were
  ruled after this part was written; see § 3.

## 1. Goal

Find out whether a NEURAL "which enumerated tables does this text qualify?" worker, disposed by
reading-order equality, admits exactly the table notes. Then R288 gets a reader with an oracle.

## 2. Where the primaries are

- **`scripts/r288_scope_probe.py`**, committed on this branch. `census` (offline, ~10 min,
  serial) writes `cases.json` plus one rendered page per candidate. `live` asks Haiku 4.5 three
  times per band and applies the oracle and the verdict rule. Re-run `census`: its output directory
  was a scratchpad and is gone.
- **The census result at `bf2cd42` + this branch:** 53 candidate ignored bands on table-bearing
  pages, 32 null controls (the last line of each band-asserted table). All 53 joined to the
  compile's carried `#ignored{i}` text, and none were skipped. Re-run it rather than trusting this
  line.
- **The previous handoff:** `docs/superpowers/2026-10-04-r288-table-notes-approaches-handoff.md`.
- **ons p4's misreading:** R230's full row in `docs/superpowers/residues-open.md`.

## 3. Decided, and where recorded

- **Path: spike.** The output is a verdict, and no reader ships. Maintainer nod in session; recorded
  only here.
- **Stray data rows that landed in `IgnoredBand` go in the NULL set** (ons p7 b6–b12, bfs p5 b9).
  Admitting one refutes the probe. Maintainer's choice of option (a), in session; recorded only
  here.
- **The oracle and the verdict rule** are in the script's `reading_order` / `majority` / `live`, and
  they were written before any call. A band is admitted iff the 2-of-3 majority answer is non-empty
  and equals the asserted tables preceding it on its page, back to the previous admitted note. The
  probe HOLDS iff the admitted set equals `truth.json` and no null is admitted. Approved in outline
  in session; the code is the record.
- **Two census defects fixed before any judgement** (both in the script). (1) On grid-adopted
  pages, regions outnumber bands by the appended grid and residue (`compile.py`, the R73 adoption
  branch). The grid's box is now the union of its superseded bands. Before the fix, all four
  note-bearing pages (bfs p5, ons p7, ons p8, apple p2) were silently skipped. (2) R261's carve
  leaves cbh band 9's carried text without `1,951,264`, so the candidate is now the band's lines
  that the carried text holds.

- **Overlay labels are neutral letters (`A`, `B`, …), not `T1`…**, because bfs prints its own
  `T1`/`T2`. Maintainer, in session after this handoff was first written; the script carries it.
- **ons p4 b1/b2 go in the must-refuse set**, consistent with option (a): a note whose referent
  table is unasserted (R230) cannot be bound. Maintainer, in session; recorded only here.

## 4. Unverified or assumed

1. ~~**Label collision, undecided.**~~ Ruled, see § 3. bfs p5 has the author's own `T1`/`T2`, and the probe draws
   `T1`… too. Options: neutral letters (`A`, `B`, …), or keep `T` and accept the confound. Not
   measured.
2. **ons p4 cannot be scored as the old truth list assumed.** Seen on the rendered page: the
   page's only asserted table is the numbered Notes list, and the real Table 1 (band 0, 241 words)
   is ignored. That is R230. The "Source:" line's referent is unasserted, so the oracle refuses it
   by construction. Ruled, see § 3.
3. **Truth list not re-judged.** Only ons p4 was viewed. From text heads, the candidates are cbh p0
   b9, graincorp-capacity p0 b4, graincorp-stem p0 b3 / p1 b2 / p2 b2, bfs p5 b6, ons p7 b16, and
   ons p8 b8. Every one needs its rendered page looked at before it enters `truth.json`.
4. **Grid boxes and label placement on grid pages were never viewed.** bfs p5, ons p7, ons p8 and
   apple p2 are the pages that matter most.
5. **Grids get no null control** (their last line is not one band's). The null set covers band
   tables only.
6. **The prompt is a draft.** It is the `PROMPT` constant in the script, and the maintainer has not
   seen it.
