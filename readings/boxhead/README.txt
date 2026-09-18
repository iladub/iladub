# Recorded boxhead readings

One JSON file per **question** put to the NEURAL boxhead reader (`src/iladub/etkl/boxhead.py`,
`baml_src/boxhead.baml`): *which header words head which column of this data grid?*

- **The filename is the question**: `sha256(column count + the numbered header listing)`, both
  derived from the PDF's text layer. It misses exactly when the document's header text or the
  grid's column count changes — and then it should, because the recording answers a question
  nobody is asking any more.
- **The content is the PROPOSAL, never the answer**: word addresses only. `dispose_boxhead` runs
  against it on every compile (address space, total accounting of every listed word, per-label
  placement inside the grid's own column intervals). The oracle never trusts the file.
- **Why they are committed**: a live reading costs money and varies run to run. A compile must be
  reproducible offline or no score it produces can be pinned as a `cor:scoreFloor`.

To record: `BAML_LIVE=1 ILADUB_RECORD_READINGS=1` and compile the document. With no recording and
no live reader the boxhead path is the identity.

| recorded | document | page | result |
| --- | --- | --- | --- |
| 2026-09-18 | gov-stats/ons-index-of-services-2026-02.pdf | 7, 8 | 6 of 6 columns labelled on each; 0.7712 → 0.8452535760728218 |
| 2026-09-18 | financial/apple-fy2026q3-statements.pdf | 2 | `June 27, 2026`, `June 28, 2025`; 0.9302 → 0.9418604651162791 |
