# Evidence — Jev on the boxhead question, before any design

**Serves:** maintenance — the accuracy proposition of `2026-09-27-jev-reading-architecture-handoff.md` § 5, run before the brainstorm designs on it

**Date:** 2026-09-27. **Tree:** branch `jev-reading-handoff`, at `0542bd0` (`src/` identical to `main` `6d6631f`).

**Doc impact: none.**

The handoff typed its next action PROPOSED: *on a real etkl question, does Jev's pick agree with
what the oracle accepts, and with the recorded Sonnet readings in `readings/boxhead/`?* It was run
first. **The proposition is refuted for the boxhead as posed, and one variant shows why the gap is
the oracle, not the worker.**

## 1. Setup

- **Population:** every recorded boxhead question, 5 of 5. That is ons p7 and p8, apple p2, and bfs p5 and p6 (`readings/boxhead/README.txt`).
- **Rebuilding each question:** each page's grid and header block were rebuilt exactly as `compile.py` rebuilds them (`derive_data_grid`, `header_block`, `listing_of`). The recording was then found by `question_key`, so the rebuilt question is byte-identical to the one Sonnet answered: 5 of 5 keys hit.
- **The call:** one Jev call per page, through Cloudflare (`typesafe/jev`, model `jev-1.13.0`), with one `choice` question per header word. That is 226 words in all.
- **The reference is Sonnet's recorded reading, not ground truth.** A disagreement is a disagreement, and it is not proof that Jev is wrong. The disagreement lists were read by eye, and in every case quoted below Sonnet's placement is the one a person would make. The rest were not checked word by word.
- **Where the raw data is:** scripts, states, questions and responses are at `internal/benchmarks/jev-2026-09-27/boxhead-spike/` (confidential, untracked). Re-run anything before relying on it. Jev's answers vary by ±0.02 from run to run.

Jev reads text only, so the geometry the image gives Sonnet was supplied as text in the state: each
column's x-interval, each header word with its x-range, and the first 3 data rows with x-ranges.

## 2. Arm 1: Jev places each word

Options: `column 0 … column n-1`, *spans several columns*, and *not a column header* (the explicit abstain).

| page | words | agree with Sonnet | Sonnet labels the oracle kept | Jev labels the oracle kept |
| --- | --- | --- | --- | --- |
| ons p7 | 52 | 34 (0.65) | 6 | 1 |
| ons p8 | 53 | 32 (0.60) | 6 | 1 |
| apple p2 | 20 | 16 (0.80) | 2 | 2 |
| bfs p5 | 52 | 28 (0.54) | 11 | 4 |
| bfs p6 | 49 | 23 (0.47) | 8 | 1 |

- **The dominant error is one column off.** On ons p8, `hotels`, `restaurants`, `communication`, `finance`, `Govern-`, `ment` and others are all placed one column to the left. That is interval arithmetic, the weakness the vendor lists itself (`model-jaggedness/jev-1.13.md`; handoff § 2a).
- **Confidence does not separate right from wrong.** Across the 226 answers:

  | confidence | answers | agreed with Sonnet |
  | --- | --- | --- |
  | < 0.3 | 39 | 0.28 |
  | 0.3–0.5 | 79 | 0.59 |
  | 0.5–0.7 | 67 | 0.70 |
  | 0.7–0.9 | 36 | 0.75 |
  | ≥ 0.9 | 5 | **0.20** |

## 3. Arm 2: Jev assigns roles only, and the host places

- **The question:** options *part of the label of ONE column*, *spans several columns*, and *not a column header*. The state carries no coordinates.
- **The placement:** the host places each leaf word by the oracle's own rule (`dispose_boxhead`: the word's centre inside the column interval). This is the same test, not a new heuristic.

| page | words agreeing on role | labels identical to Sonnet's |
| --- | --- | --- |
| ons p7 | 49 / 52 (0.94) | 5 / 6 |
| ons p8 | 50 / 53 (0.94) | 5 / 6 |
| apple p2 | 17 / 20 (0.85) | 0 / 2 |
| bfs p5 | 41 / 52 (0.79) | 5 / 11 |
| bfs p6 | 39 / 49 (0.80) | 0 / 8 |

- **Jev missed every spanning label.** On ons, `Industry sections (SIC2007)` went into a leaf. On apple, `Nine Months Ended` went into both date leaves, which is why 0 of 2 are identical. On bfs p5, `Composantes de l'évolution de la population` was split between leaves and not-header.
- **Title lines leaked into labels.** On bfs p6, `Population résidante permanente … classe d'âge et rapports de dépendance` and `canton,` were joined into column labels, so 0 of 8 are identical.
- **Footnote marks** (`1`, `2`) are misassigned both ways on bfs.

## 4. What the oracle can and cannot see

**Under arm 2, `dispose_boxhead` accepts every one of Jev's readings, including the wrong ones.**
Its three checks are address space, total accounting, and centre-in-interval placement. They catch
a *placement* error, which is arm 1's failure. They are blind to a *role* error: a title word filed
under a column's label passes all three. Spanners are checked for accounting only
(`boxhead.py`, `dispose_boxhead`: `spanning_labels` never reaches the placement loop). So arm 2's
errors are exactly the class the membrane admits.

By CLAUDE.md § 8 (*no oracle, no worker*), that makes the missing piece a **role and spanner
oracle**, not a better worker. Until one exists, giving Jev the role decision would put unrefusable
errors into the graph.

## 5. What this settles and what it does not

- **Settled:** Jev does not replace `ReadBoxhead`. It fails when asked for per-word placement from text geometry (arm 1). When asked for roles, its errors pass the current oracle unseen (arm 2).
- **Not settled:** whether Jev is accurate on the questions in its measured strong zone. Those are grounding a label to a concept or refusing, checking an extracted fact against its source sentence, and reading Turtle (handoff § 2a, a handful of calls each). The architecture brainstorm proceeds on this split: geometry is host derivation (AXIOM), reading the image stays with Sonnet, and Jev takes only questions that an oracle can refuse.
- **Not measured:** whether a role question phrased per line or per label, rather than per word, would recover the spanners. Nothing here pins a claim either way.
- **Cost, for the record:** 3.0k–11.4k input tokens per page; round trips of 0.32–0.68 s.
