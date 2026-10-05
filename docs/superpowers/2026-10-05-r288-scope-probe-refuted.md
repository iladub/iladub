# Evidence: R288 scope probe — REFUTED, and the worker is the half that fails (2026-10-05)

**Topic:** r288-scope-probe-live · **Date:** 2026-10-05

**Serves:** prog:criterion:etkl:03 — R288: the `live` run the 2026-10-05 scope-probe handoff's part 5 prescribed.

**Doc impact: none.**

Written under the 50K originating floor (about 35K working tokens, estimated, not read off a meter). Part 5 was written first.

## 5. Next action (written first)

- **Proposed. This is a maintainer ruling, not a loop.** The probe asked one worker two questions:
  *whether* the red text is a note, and *which* tables it qualifies. The reading-order oracle
  disposes only *which*. § 2 shows the worker answers *whether* with "yes" for 37 of the 40
  non-notes it parsed, so nothing disposed *whether*, and the composite admitted titles, footers,
  a page number and data rows. Under the 2026-09-17 ruling (*no oracle, no worker*), the next
  subject is **an oracle for *whether***, and none exists. The two ways to close R288 are now:
  (a) find a disposer for *whether*, and that starts as a design session, not a run; or
  (b) take R288's close arm (b), a recorded ruling that ignoring cbh's Note is acceptable for
  `etkl:03`, at +0.0883. **Recommendation: (b) now, and (a) parked until a second document style
  needs it.** Re-prompting and re-running against the same 8-note truth set would fit the prompt
  to the truth set (see [[no-overfitting-general-fixes]]), and this note does not propose it.

## 1. What was run

Branch `r288-scope-probe-live` from `303a8a5`. `scripts/r288_scope_probe.py` and `src/` are
byte-identical to `f10dcfe`, where the prompt was approved (`git diff --stat f10dcfe HEAD --
scripts/r288_scope_probe.py src` printed nothing).

- `census`, re-run: `candidates=53 nulls=32 skipped=[]`, and every candidate is `join=ok`. All 8
  approved truth bands are present at the indices § 3 of the handoff names, with the expected text,
  so nothing was re-mapped.
- `truth.json` is exactly the handoff's 8 bands.
- `live`, Haiku 4.5, 3 repeats, 255 calls, no HTTP errors:

```
admitted=[('bfs-population-bilan-2023', 6, 12), ('graincorp-capacity-2026-08-04', 0, 4),
          ('graincorp-stem-2026-07-31', 0, 3), ('graincorp-stem-2026-07-31', 1, 2),
          ('graincorp-stem-2026-07-31', 2, 2), ('ons-index-of-services-2026-02', 4, 4),
          ('ons-index-of-services-2026-02', 7, 6), ('ons-index-of-services-2026-02', 8, 6),
          ('who-wfa-boys-zscore-0-5', 1, 6)]
missed notes=[('bfs-population-bilan-2023', 5, 6), ('cbh-stem-2026-08-03', 0, 9),
              ('ons-index-of-services-2026-02', 7, 16), ('ons-index-of-services-2026-02', 8, 8)]
admitted non-notes=[('bfs-population-bilan-2023', 6, 12), ('ons-index-of-services-2026-02', 4, 4),
                    ('ons-index-of-services-2026-02', 7, 6), ('ons-index-of-services-2026-02', 8, 6),
                    ('who-wfa-boys-zscore-0-5', 1, 6)]
null admits=3
VERDICT: REFUTED
```

4 of 8 notes admitted (the graincorp four), 5 non-notes admitted, 3 nulls admitted. The verdict
rule was fixed before any call, and it says REFUTED on every one of its three clauses.

## 2. Why: four separable failures

**F1, the worker does not discriminate.** This is the decisive failure. The tally is the
2-of-3 majority over the 53 ignored bands:

| | majority non-empty ("a note") | majority empty | UNPARSED |
|---|---|---|---|
| truth = note (8) | 7 | 0 | 1 |
| truth = not a note (45) | **37** | 3 | 5 |

Titles (`Apple Inc.`, `ELEVATION CAPACITY TABLE`), the publisher line, `Page 5 of 7`, a footer
(`WHO Child Growth Standards`, the OFS address) and stray data rows all drew `{A}` or every label.
The worker read the question as *"is this text related to a table"*. On a page with one table,
its answer is a constant. The oracle refused most of these only because they **precede** the table
(`ro={}`), so position, not the worker, did the refusing. Everything that **follows** a table
satisfies reading-order equality by construction, and the worker let it through: ons p4 b4
`Page 5 of 7`, ons p7 b6 (a data row), ons p8 b6, bfs p6 b12 (a footer), and who p1 b6 (a
footer).

**F2, the oracle's ordering key is wrong on cbh.** The worker answered `{A..F}` ×3 for the Note.
The oracle wanted `{A..D}`, because tables E (stock) and F (shutdown dates) have band indices 10
and 11, after the Note's 9. On the rendered page, E and F sit **above** the Note, side by side
(viewed, `cbh-stem-2026-08-03_p0_b9.png`). Band 9's position is its pre-carve band's (it held
`1,951,264`, which sits above E), not its Note lines'. The worker was right and the oracle was
wrong. Band index is not reading position after a carve.

**F3, the oracle's floor cascades a false admit into a miss.** On ons p7 and p8, the grid is
table A at band 3 / 2. The worker's false `{A}` on a data row (p7 b6) and on p8 b6 admitted them,
which moved the floor to 6, so the true note below (p7 b16, p8 b8) got `ro={}` and was refused,
even though the worker said `{A}` ×3. With no floor, both would be admitted. The floor converts
one F1 error into two errors.

**F4, the closed contract refused the author's labels.** On bfs p5 every answer is UNPARSED
(18 of 18). One diagnostic call on b6, made after the verdict, returned
`{"tables": ["T1", "T2"]}`. The page prints its own `T1`/`T2`, and the worker named those, not
the overlay's `A`. The neutral-letter ruling avoided the collision of labels, not the worker's
preference for the printed ones. The contract did its job: it refused rather than guessed.

## 3. What this does and does not say

- **It refutes the composite as designed**, under the rule fixed before the run. It does not
  refute "a VLM can recognise a table note". The worker named the right tables for 7 of 8 notes
  (F2's cbh answer included), and that is the *which* half.
- **Repairing the oracle does not rescue it.** F2 and F3 are oracle defects, and both can be fixed
  without a constant: key on the candidate lines' own top, and drop the floor. But F1 alone still
  admits every trailing title, footer and page number. Reading-order equality has **no power over
  *whether***, and the probe gave *whether* to the worker with no disposer behind it.
- **Not a post-hoc re-scoring.** No truth label, prompt or rule was changed after the run. The
  single diagnostic call in F4 was made after the verdict, and it explains an UNPARSED without
  feeding any score.

## 4. Unverified

1. F1's reading of the worker's intent ("related to" rather than "a note on") is an
   interpretation of its answers. It was not asked.
2. F2 is measured on cbh only. Whether other carves misplace a band's position is not surveyed.
3. The bfs p6 page has 9 asserted tables (one per canton row band). The null rows there are the
   R238/R239 row-as-table family, and they were not examined further.
4. The census and live outputs lived in a session scratchpad and are gone. The lines quoted above
   are the record.
