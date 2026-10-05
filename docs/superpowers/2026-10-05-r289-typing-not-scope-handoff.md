# Evidence + handoff: R289 — the Text scope is a no-op; the bfs regressions are typing defects (2026-10-05)

**Serves:** prog:criterion:etkl:03 — R289 is the named blocker on lifting cbh's hold.

**Topic:** r289-typing-not-scope · **Date:** 2026-10-05

**Doc impact: none.**

This note ran part 5 action 1 of `2026-10-05-r289-scoping-handoff.md`. Its prediction is **REFUTED**,
but in a way that removes the need to scope the rule at all (§ 2). Part 5 was written at about 69K
working tokens, which is over the 50K originating floor, so each action in it is graded.

## 5. Next concrete action (written first)

1. **PROPOSED: write the R289 spec with the candidate rule *unscoped*, sequenced after R265's typing
   remedy.** "Unscoped" means § 2.4 of `2026-10-05-r289-split-on-a-line-with-no-data.md`: the smallest
   candidate row with no off-type, non-abstaining cell in any data column.
   - **Evidence for the sequencing (§ 2.2–2.3):** under an R265 counterfactual the rule moves cbh 8,
     ons 4 and bfs 3 bands, and 2 of bfs's 4 regressions vanish. The same counterfactual moves the
     shipped split on **0** bands corpus-wide, so R265 can land first without moving any split.
   - **What may be wrong:** the counterfactual is a regex text normalisation, not R265's real
     remedy (§ 4). If R265's remedy types more or less than the regex does, re-run
     `analyse_r265.py` after it lands, before the spec relies on these counts. That run takes about
     12 minutes.
2. **PROPOSED, and the maintainer's call:** decide whether the R289 spec waits for R242 too. The one
   remaining regression is the bfs fragment headed `2010 2` / `2011 3` (two band keys, pages `[0]`
   and `[5]`, identical text). Today's split already puts that fragment's first data row in the
   header ([[R166]]). The rule makes it two data rows. Its dirty cells are R242's fused footnote
   markers. **Predicted, not measured:** stripping the marker gives NEW == OLD.
3. **ASSERTED:** do not narrow "dirty" to `tab:Text` (§ 2.1). The narrowing is a no-op, and a spec
   clause that does nothing must not ship as a scope.

## 1. Goal

Scope the R289 candidate rule so that it fixes cbh's four rosters without regressing anywhere else.

## 2. Findings

All runs are on `r289-text-scope` at `6b68938` plus the harness changes in this PR. Each document was
compiled in its own process, one document at a time. The harness returns OLD, so every score equals
§ 2.4's: cbh 1.0, gstem 0.99955, gcap 1.0, ons 0.86849, bfs 0.90214, apple 0.94186, who 0.99628.

### 2.1 Narrowing "dirty" to Text is a no-op (the handoff's prediction is REFUTED)

With `R289_DIRTY=text`, the changed bands per document are cbh 8, ons 4 and bfs 5. These are exactly
§ 2.4's counts. On bfs, the `text` and `any` runs give the same 5 bands with the same OLD/NEW values.
**Every dirty cell on every changed band is already `tab:Text`**, so the narrowing removes nothing.
The handoff's guess that the bfs rows were dirty on "numeric fragments" was wrong in kind: the
fragments *are* numbers, but they are typed Text.

### 2.2 Why the 4 bfs fragments are dirty (measured, cell text recorded)

| band (key) | dirty cells (row, col, text) | cause |
|---|---|---|
| `64b8fa43fc82` p5 (`Berne …`) | `3 465`, `- 939`, `- 3 178`, `- 70` | [[R265]]: space-grouped thousands and a sign set apart from its digits, typed Text |
| `d2bb9cd33d92` p5 (`Bâle-Ville …`) | `2 491`, `1 855`, `2 345`, `2 547`, `1 999`, `2 748`, `- 1 651` | [[R265]] |
| `bc099aefff2a` p0 and `eb6668518cbf` p5 (`2011 3 7 870 134 …`) | `2010 2`, `2011 3` | [[R242]]: a footnote marker fused into the row label |

Probe at `6b68938`: `_cell_datatype` gives `'3 465'` → Text, `'- 939'` → Text, `'−939'` (U+2212) →
Text, `'-939'` → Numeric. The two keys `bc099…` and `eb666…` carry identical lines and differ only in
`pages` (`[0]` vs `[5]`). This is the `Word.page` 0 oddity that the scoping handoff's part 4 already
flagged.

### 2.3 R265 counterfactual: the rule after the typing remedy

`harness.py` now also builds the evidence graph a second time, from cell text passed through `r265()`.
That function closes up a sign set apart from its digits, reads U+2212 as `-`, and removes a space,
NBSP or narrow NBSP between 3-digit groups. Unit-checked on 13 strings, including `2010 2` and
`en %`, which it leaves alone. On the second graph it computes OLD′ (the shipped `.rq`) and NEW′ (the
candidate rule). `analyse_r265.py` over all 7 documents:

| doc | AXIOM bands | OLD′ ≠ OLD | NEW ≠ OLD | NEW′ ≠ OLD′ |
|---|---|---|---|---|
| cbh | 9 | 0 | 8 | 8 |
| ons | 14 | 0 | 4 | 4 |
| bfs | 23 | 0 | 5 | 3 |
| gstem, gcap, apple, who | 7, 2, 18, 10 | 0 | 0 | 0 |

- The two R265 bands go to NEW′ = OLD′ = 1, and no cell is dirty after the retyping.
- The three bfs bands left are:
  - `ee5a083ef386`: `au 1er janvier …` moves into the header, header ink ✔ (§ 2.4);
  - the `2010 2` fragment's two keys: ✘, R242.
- **The R265 retyping moves the shipped split on no band in the corpus.**

## 3. Decided, and where

- **Narrowing to Text does not ship.** This is an agent conclusion from § 2.1, recorded here only.
- **The candidate rule's bfs regressions are typing defects (R265, R242), not a scope defect.** This
  is an agent conclusion from § 2.2–2.3, recorded here and in R289's register row.
- Sequencing R289 after R265, and whether to wait for R242, are **not decided**. They are part 5
  proposals, for the maintainer.

## 4. Unverified or assumed

- `r265()` is a regex approximation of R265's remedy, not the remedy itself. In particular, it does
  not cover a decimal comma inside a space-grouped number beyond `[.,]\d+`, or an apostrophe as the
  separator (`1'234`, Swiss).
- "Footnote marker" is read from the line text (`2010 2` beside `2011 3`). It was never checked
  against glyph size or the rendered page.
- The verdicts from § 2.4 that are reused here (header ink vs data row) are still text readings and
  were never rendered.
- The score effect of the rule, with or without R265, is unmeasured. The harness always returns OLD.

## 2b. Where the primaries are

- `scripts/r289_split_blast/harness.py`: `R289_DIRTY={any,text}`, `dirty_cells` with their text,
  and the `old_r265`/`new_r265` counterfactual.
- `scripts/r289_split_blast/analyse_r265.py`: the § 2.3 table and per-band detail.
- Run outputs in a session scratchpad (not kept). Reproduce with
  `R289_DIRTY=text .venv/bin/python scripts/r289_split_blast/harness.py <pdf> <out.jsonl>`, one
  document per process and serially, then `analyse_r265.py <out.jsonl>…`.
- R289, R265 and R242 full rows: `docs/superpowers/residues-open.md`.
