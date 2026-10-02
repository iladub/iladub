# Evidence — R261 loop (b): the grand total's role question, P4 and P4b (2026-10-02)

**Serves:** prog:criterion:etkl:03 — loop (b) of the R261 totals family, run BEFORE any spec as the
table-level handoff's part 5 ordered (`2026-10-01-r261-table-level-handoff.md`, graded *proposed*).

**Doc impact: none.**

## § 1. Why a new question

P3 (`2026-10-01-r261-totals-family-evidence.md` § 6.4) refuted one wording. It did not refute the
total-of-totals level. Two defects in that wording, read off `scripts/r261_total_question_probe.py`
`PROMPT2`:

1. **It was leading.** *"several tables each have a total printed beneath them. The number {value}
   is also printed"* asserts that `{value}` is not one of those totals, which is false for every
   port total it was asked of.
2. **Nothing located the asked number.** On the page all five totals carry identical typography:
   the same Volume column, a thin rule above and a thick rule below (`pdfplumber` rects at x 797,
   width 50; e.g. 178,708's at top 664/673 and 1,951,264's at 681/689), all Calibri 6.0 in black.
   `1,951,264` differs only by position: directly beneath ESPERANCE's total, with no table between.

P3's control was the right one and stays the control here. A worker that answers "yes" to the port
totals adds nothing, and the conjunction reduces to exact sum alone.

## § 2. The probe

`scripts/r261_grand_total_role_probe.py` (its docstring carries the run command):

- **The question:** the role of one number, marked by a red box on the image, as a closed enum:
  `table_total | total_of_totals | other | cannot_tell`. There is no note field. Model: Haiku 4.5,
  the production `Claude` client.
- **The population:** the target `1,951,264`; the 4 port totals (expected `table_total`); and one
  extra control, `22,858`, ESPERANCE's last Volume cell (expected `other`).
- **Decision rule, fixed with the maintainer before either run:** the question holds iff
  `1,951,264` gets `total_of_totals` ×3 AND no null ask gets `total_of_totals`.
- **Two crops:**
  - **P4 (`CROP=strip`):** a hand-picked strip, pt (600, 60, 1000, 700). That is a tuned constant
    (CLAUDE.md § 8), so P4 is the first measurement only.
  - **P4b (`CROP=derived`):** the union of the four operand totals' D7 table-level crops (each
    total's previous band, through its own line) plus the candidate line. It derives to pt
    (46, 101, 1148, 693) and is the production analogue of `printedtotal.crop_table`.

## § 3. Recorded runs (`REPEAT=3`, 2026-10-02, serial)

| case | P4 strip | P4b derived |
|---|---|---|
| `1,951,264` (target) | total_of_totals ×3 | total_of_totals ×3 |
| `374,904` | table_total ×3 | table_total ×3 |
| `737,289` | table_total ×3 | table_total ×3 |
| `660,363` | table_total ×3 | table_total ×3 |
| `178,708` | table_total ×3 | table_total ×3 |
| `22,858` (in-table cell) | other ×3 | **table_total ×3** |

All 36 replies parsed; none was `cannot_tell`. The committed script was then re-run at `REPEAT=1`
on both crops and reproduced every answer above. P4b's first attempt died on a transient
`URLError: [Errno 65] No route to host` before any answer was recorded. It was retried unchanged;
that run is the one recorded here.

## § 4. Verdict

- **The rule HOLDS on both crops.** The target gets `total_of_totals` ×3, and no null gets
  `total_of_totals` in 30 asks.
- **The extra control FAILS on the derived crop**, which is outside the rule. The red box is on
  `22,858` and stays visible after the API's downscale (2297×1233 px → long edge 1568, factor 0.68;
  rendered and looked at). Yet the worker calls an in-table value a table total. On a near-page-wide
  image its reading is coarser than on the strip. It may be keying on *"a number at the foot of a
  column"* more than on the rules that set a total apart.
- **What the failure does not do:** it does not bind anything. The totals-level conjunction asks
  only about an arithmetic candidate (a lone number equal to the exact sum of every total bound on
  the page) and binds only on `total_of_totals`. `table_total` binds nothing.
- **What it does show:** the worker's protection beyond the arithmetic is shown at n = 1 target and
  4 nulls. The one null it misread is the one closest to the coincidence class the worker exists to
  catch: a number in the right place that is not a total. No corpus document offers that
  coincidence (right sum, wrong role). Raised as [[R287]].

## § 5. Ruling taken on this evidence

The maintainer chose (2026-10-02, in session): **spec loop (b) on the derived crop.** The `22,858`
miss is stated first in the spec as a concern and recorded as [[R287]], rather than tuning a narrower
crop now. The rejected options were a column-scoped crop measured first, and a ruling instead of a
worker (exact arithmetic alone, or leave `1,951,264` unbound).
