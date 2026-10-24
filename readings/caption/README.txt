# Recorded caption readings

One JSON file per **question** put to the NEURAL caption reader (`src/iladub/etkl/caption.py`,
`baml_src/caption.baml`): *which of these candidate lines are this table's own caption — its
title, its unit line?* (R336, spec 2026-10-24 § 3.3).

- **The filename is the question**: `sha256("caption\n" + column count + "\n" + the numbered
  candidate listing)`, all derived from the PDF's text layer and the disposed boxhead. The spec
  writes the key as `"caption\n" + ncols + listing`; the second `"\n"` is a deliberate choice that
  mirrors `boxhead.question_key`'s separator between the count and the listing. The `caption\n` prefix keeps a caption key from colliding with a
  boxhead key over the same listing. It misses exactly when the candidate lines' text or the grid's
  column count changes — and then it should.
- **The content is the PROPOSAL, never the answer**: candidate indices only (`caption_lines`,
  `refuses`, `note`). `dispose_captions` runs against it on every compile (every index a candidate,
  non-empty, contiguous in page order, ending directly above the topmost surviving label). The
  oracle never trusts the file.
- **Why they are committed**: a live reading costs money and varies run to run. A compile must be
  reproducible offline or no score it produces can be pinned as a `cor:scoreFloor`.

To record: `BAML_LIVE=1 ILADUB_RECORD_READINGS=1` and compile the document. With no recording and
no live reader the caption path is the identity.

| recorded | document | page | result |
| --- | --- | --- | --- |
| 2026-10-24 | apple-fy2026q3-statements | p2 | disposed: 3 lines (0, 1, 2) |
| 2026-10-24 | bfs-population-bilan-2023 | p5 (2 grids), p6 | disposed: 1, 1, 2 lines |
| 2026-10-24 | ons-index-of-services-2026-02 | p7 / p8 | disposed 2 lines / NO CLAIM (answer {0,1}; which disposal check refused it is not measured) |
| 2026-10-24 | arxiv-1706.03762v7 | p9 | disposed: 2 lines |
| 2026-10-24 | caltrain-weekend-timetable | p0-p3 | NO CLAIM on all four (which disposal check refused each is not measured) |
| 2026-10-24 | fed-h41-2025-01-02 | p0 | **NO CLAIM**: answer {C1 `H.4.1`, C5 title, C6 `Millions of dollars`}, not contiguous. Spec §7's last bullet asked for {L6}, {L5, L6} or wider: the model returned none of these. |
| 2026-10-24 | fed-h41-2025-01-02 | p1, p2, p3, p7, p8, p10 | disposed: 2 lines each (1, 2) |
| 2026-10-24 | who-covid-sitrep-41 | p2 / p3 | disposed: 2 lines / 2 lines |

Recorded with only the caption reader live (`BamlCaptionReader` patched in, `BAML_LIVE` unset, so
every other worker replays offline), one ask per question, 20 questions across `corpus/` and
`held-out/`. A first sweep wrote nothing: `baml_client` (repo root) was not on `sys.path`, and the
reader's `ModuleNotFoundError` was swallowed at the perceptual edge as NO CLAIM. Record with
`PYTHONPATH=src:.`.
