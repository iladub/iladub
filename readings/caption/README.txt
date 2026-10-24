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
