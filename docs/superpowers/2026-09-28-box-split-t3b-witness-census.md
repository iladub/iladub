# T3b measurement M4 — a fusion witness, measured against the count guard (MEASUREMENT ONLY)

**Serves:** prog:criterion:etkl:03 — measurement for Task 3b of the box-split loop.
**Doc impact: none.** Follows `2026-09-28-box-split-t3b-measurements.md` (M1–M3). No source,
test or spec was changed. The instrument is in the SDD workspace, which is gitignored and therefore NOT
durable: `.superpowers/sdd/2026-09-28-box-split/w1.py` (runner `w1.sh`, raw output `w1.jsonl`).
The witness definition below is complete enough to rebuild it.

## The question

The shipped guard (`compile._build_ruled_band`, `_under_resolved`) refuses a re-bucket when
`len(xs) - 1 < _word_column_count(sub)`. Its own comment says why: re-bucketing on rules that
under-resolve "can only FUSE". M1 showed the count reads 9 on cbh T1 though no line of T1 has two
words that the extra gutters separate. So the question measured here is whether the property the
comment names, fusion, can be tested directly and exactly, with no tolerance.

**Fusion witness (exact, no constant).** For a band `sub` (the peeled band the guard already
measures) and rule xs: a witness is a pair of adjacent words `a`, `b` on ONE line, whose centres
fall in the SAME rule interval (inside the outer pair), such that some point of the open x-range
`(a.x1, b.x0)` is covered by no word of ANY line of the band. The pair is two pieces of ink the
band's own layout separates all the way down, and a re-bucket on `xs` would join them into one cell.

## Command

```
bash .superpowers/sdd/2026-09-28-box-split/w1.sh     # serial, one process per corpus PDF, page_bands on every page
```

Branch `box-split` at `9d38182`. All 7 PDFs exited 0 and the instrument fired **100** times,
matching M2's 100 `_build_ruled_band` calls, so it covers the same population.

## Result

```
(count_refuses, witness_exists) : {(True, True): 35, (True, False): 1, (False, True): 52, (False, False): 12}

count refuses, NO witness:
  cbh-stem-2026-08-03.pdf p0 box  rule_cols 7  word_cols 9  lines 5 | PORT WHEAT MAIN WHEAT GRADES BARLEY CANOLA OTHER TOTAL
```

**Fact 1. As a REPLACEMENT for the count, the witness is refuted.** It fires on 52 bands the count
accepts, and every sampled witness there is an inter-word space inside one cell: `DUE|TO` (cbh),
`Time|Nominated` (cbh), `of|Ship` (graincorp-stem), `income|taxes` (apple), `-3|SD` (who). A space
between two words of one phrase is also a band-wide zero-ink gap. So the exact witness cannot tell
a word space from a column gutter. Telling them apart is a reading judgement, and it is not
answerable at this grain.

**Fact 2. Its ABSENCE is a proof, and it is absent on exactly one refused band: cbh T1.** If no
witness exists, every pair of words that a re-bucket joins was already bridged by some other line's
ink, so the re-bucket joins nothing that the band's layout separates. On T1 the pairs a re-bucket
joins are `MAIN|WHEAT|GRADES`, bridged by the body word `APW1/ASW9/AWW1` [155.78, 206.82]. The two
EXTRA gutters from M1 (x 101.38, 377.88) separate words on DIFFERENT lines only, so they produce
no witness.

**Fact 3. As a CONJUNCTION (refuse iff count refuses AND a witness exists), exactly one of 100
calls changes: cbh T1, from refuse to accept.** The other 35 refusals, including all 8 bfs p6
bands with T1's shape (6 rule cols vs 9) and all 27 outer-box (`rule_cols == 1`) bands, keep a
witness and keep refusing. The 64 accepts are untouched by construction, because the conjunction
can only relax a refusal.

**Fact 4. The post-refinement application (`len(col_xs) - 1 < _word_cols`) is not exercised by the
relaxation.** Of 18 calls that return non-empty `column_xs`, that check passed on all 18 (it
refuses nothing in this census), so a conjunction there changes nothing measured. Recorded for
completeness: 17 of the 18 carry a witness even on the refined `column_xs`, again word spaces
(`G|and`, `1|736`, `of|Ship`), and ons p7 `2024 Dec …` carries none.

## Not measured

- The full classify → compile → membrane path for T1 with the relaxed guard. M3's guard-off
  control shows only that T1's header re-buckets to the 7 correct cells.
- `test_o3_no_page_loses_asserted_ink_to_a_merge` and the full suite with the relaxation.
- Section-repair rebuilds (`section_repair=True`), as in M2's scope caveat.
