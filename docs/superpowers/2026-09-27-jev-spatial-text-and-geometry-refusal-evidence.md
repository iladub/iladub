# Evidence — spatial text for Jev, and whether geometry can refuse Jev's role errors

**Serves:** maintenance — two probes run inside the Jev deep brainstorm (`2026-09-27-jev-deep-brainstorm-handoff.md`), before any design is built on them

**Date:** 2026-09-27. **Tree:** branch `jev-reading-handoff` at `71ad28d` (`src/` identical to `main` `6d6631f`).

**Doc impact: none.**

The population, the rebuilt questions and the reference are exactly those of
`2026-09-27-jev-boxhead-spike-evidence.md` § 1. That means 5 recorded boxhead pages (ons p7/p8, apple p2,
bfs p5/p6) and Sonnet's recorded readings as the reference, **not ground truth**. Scripts, states,
responses and printed outputs are kept at `internal/benchmarks/jev-2026-09-27/boxhead-spike/`
(untracked): `jev_spatial_spike.py` → `run3-spatial/`, and `geometry_refusal_probe.py` (+ `_noR3`) →
`run4-refusal/`. It is one run per condition, and Jev varies by ±0.02 from run to run.

## 1. Probe A: does spatial text help Jev? (maintainer's question, in session)

**The state.** Header lines plus the first 5 data rows, drawn monospaced. The cell pitch is **derived** (the median
glyph advance of the rendered words), and words are never overwritten. The PDF's vector edges are
drawn as `─ │ ┼`, and a host-derived ruler `c0 c1 …` marks the column centres. The existing
`roundtrip.render_ascii` was not reused: it hard-codes `width=80` and overwrites colliding words.

**The control.** The same rows with every whitespace run collapsed to one space. That destroys the
alignment and keeps the content and line order. Questions are unchanged from arm 1 (placement) and
arm 2 (role).

| arm 2 (role): words agreeing · labels identical to Sonnet | numeric x-ranges (earlier run2) | spatial | control |
| --- | --- | --- | --- |
| ons p7 | 0.94 · 5/6 | 0.92 · 6/6 | 0.94 · 5/6 |
| ons p8 | 0.94 · 5/6 | 0.96 · 6/6 | 0.94 · 5/6 |
| apple p2 | 0.85 · 0/2 | 0.85 · 0/2 | 0.95 · 1/2 |
| bfs p5 | 0.79 · 5/11 | 0.90 · 7/11 | 0.90 · 7/11 |
| bfs p6 | 0.80 · 0/8 | 0.86 · 7/8 | 1.00 · 7/8 |
| labels identical, total | 15/33 | 26/33 | 25/33 |

- **Arm 1 (placement)** scores 0.50–0.80 for spatial and 0.52–0.85 for the control, the same level as the numeric run. Labels identical to Sonnet stay near 0 everywhere. **Jev still cannot place words.**
- **Alignment is not what helps.** The control matches or beats spatial on every page. The gain over the numeric run comes from what both share: whole lines in reading order, and no coordinates.
- **Alignment misleads in two cases.** On bfs p6 the spatial state makes the wide title a spanner (7 errors, against 0 for the control). On apple, spatial loses `Nine Months Ended` (3 errors, against 1 for the control).
- **Some disagreements are probably Sonnet's.** On bfs p5, Jev files the footnote marks `1` as not-a-header, where Sonnet put them in a label.

## 2. Probe B: can geometry refuse role errors, with no tuned constant?

The probe uses exact interval tests over host evidence, with no tolerance. **Spanning labels** are maximal runs of
consecutive "spans" answers on one line.

- **R1:** a spanner overlaps at least 2 column intervals.
- **R2:** a spanner overlaps no stub column, where the stub means `not GridColumn.is_measure`.
- **R3:** a leaf word overlaps exactly 1 column interval.

**The null control** passes Sonnet's reading through the same rules; any refusal there is false.

**Results as errors / caught / false refusals** (`run4-refusal/*.txt`):

| rules | Sonnet (null) | numeric | spatial | control |
| --- | --- | --- | --- | --- |
| R1 + R2 + R3 | 0 / 0 / **8** | 30 / 10 / 8 | 21 / 12 / 14 | 12 / 7 / 15 |
| R1 + R2 | 0 / 0 / 0 | 30 / 0 / 0 | 21 / 11 / 6 | 12 / 7 / 7 |

- **R3 is refuted.** It refuses 8 of Sonnet's correct leaf words, among them `communication`, `Accroissement` and `80 ans ou plus`. The reason is that header words legitimately overhang the extent of their data column. Rescuing R3 needs a tolerance, which is forbidden (CLAUDE.md § 8). The oracle's existing centre-in-interval rule stays the only placement test.
- **R1 costs nothing** on the null control. It catches spanners over a single column, such as `Section` and `État de la`. Its one false refusal (apple control, `Nine`) is a run left alone because its neighbour `Months` was misread. That makes it a correct refusal of a partly wrong label, charged to one correct word.
- **R2 catches title-as-spanner** (bfs p6 spatial) but **rests on a wrong derivation.** On bfs p5, `is_measure` makes the year column c0 a `Quantity` and c8 (`- 3 933`) a `Text`. The stub is therefore c8, and R2 refuses Sonnet's correct `Composantes de l'évolution…` spanner: 6 false refusals in both spatial and control. The axiom may still stand. The stub derivation it depends on does not hold here.
- **Omissions are invisible to geometry.** `(SIC2007)` answered not-a-header, and the footnote marks, are not claims. No placement test can refuse them.

## 3. What this settles and what it does not

- **Settled on this population.**
  - Jev's evidence should be reading-order lines without coordinates.
  - Spatial layout adds nothing measurable for Jev and can mislead it.
  - Geometry can refuse one class of role error, spanner commissions (R1), at zero false refusals.
- **Not settled.**
  - A geometric oracle for leaf/title confusion and for omissions. R3 needs a tolerance, R2 needs a correct stub, and omissions need a non-placement oracle.
  - Whether R2 holds once the stub is derived correctly (the stub derivation is its own defect).
  - Anything at n > 5 pages.
