# Handoff — etkl:02: graincorp-capacity, the corpus document nearest to acceptable

**Topic:** etkl-02-graincorp-capacity
**Serves:** prog:criterion:etkl:02 — chosen by the maintainer 2026-09-11 from the strip's `ready 9`.
**Date:** 2026-09-11. **Loop shape:** selection only; no spec, no code. This session stopped at
~54K working tokens, past the 50K originating floor, so the spec is a fresh session's. The
maintainer chose that over an override. **Doc impact: none**.

Part 5 written first. It is graded per action, because the session was past the floor when it
wrote it.

## 5. The next concrete action

### 5a. ASSERTED: write the etkl:02 spec in a fresh session, from the hold's own three steps

The route is already on record, written by the 2026-08-20 hold on
`<urn:iladub:corpus:graincorp-capacity-2026-08-04>` (`tests/corpus-manifest.ttl`, the node after
graincorp-stem's). It does not need re-deriving. Its three steps:

1. author a `cor:contract` / `cor:terms` / `cor:shapes` triple for the document (it has none, so
   `tests/test_corpus.py::test_grounding_where_contracted` never parametrizes it);
2. that test passing: every grounded node sits behind exactly one accountable promotion, and
   `grounded` is non-empty;
3. **the maintainer**, not the loop, reads the carried grid against the source page and records
   that read in a dated `cor:adjudication`.

The spec's job is to state (1) and (2) as a contract and to make (3) cheap for the maintainer.
Step (3) could be a side-by-side of the carried grid and the rendered page. **The loop cannot
flip `prog:met`**: that needs step 3's human note, then `cor:expectedVerdict cor:CompilesAbove`
plus a `cor:scoreFloor`. `tests/test_arc_manifest.py::test_etkl_criteria_agree_with_the_corpus_manifest`
recomputes all seven etkl criteria from the corpus manifest, so the two files must flip together.

### 5b. PROPOSED: the score is still 1.0000 when the fresh session starts

Re-measured this session (below, § 2). Four of seven corpus scores moved inside three days
earlier this month ([[figure-carries-its-date]]), so re-run the one command in § 2 before citing
the figure. **Refuted in 20 seconds.** If it moved, the spec starts from the new figure and asks
what moved it.

### 5c. PROPOSED: the RECORD_TABLE is groundable by a small contract (`grounded > 0`)

Only one region asserts: a single `RECORD_TABLE`, next to four ignored `NON_TABLE` bands. The
prediction: its columns name concepts a terms file can carry, as cbh and stem do (their contract,
shapes and terms files are 13 to 23 lines each). **Refuted in minutes** by dumping the carried
records and opening the PDF page. If the columns are not concepts (a capacity table may be sites
× figures with no stable vocabulary), then step 1 is a design question and the spec says so.

**The trap that 5c must not fall into** ([[no-overfitting-general-fixes]]): author the terms
from the PDF page, as a human reads it. **Never from the compile's output.** A contract fitted to
what the compiler carried makes step 2 circular. The grounding would then confirm the reading
instead of testing it, and step 3's read is the only thing that would catch it.

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the criterion | `tests/arc-manifest.ttl`, `prog:criterion:etkl:02` block | `prog:source "tests/corpus-manifest.ttl:46"`, `met false`, no blocker, no dependency read |
| the hold | `tests/corpus-manifest.ttl`, `<urn:iladub:corpus:graincorp-capacity-2026-08-04>` | the three-step route quoted in 5a; `cor:expectedVerdict cor:Unadjudicated` |
| the pattern | `examples/shipping/{cbh,stem}-{contract,terms,shapes}.ttl` | size and shape of a per-series contract triple |
| the grounding oracle | `tests/test_corpus.py:146` `test_grounding_where_contracted` | `validate_shapes=True` is the promotion-invariant gate; `grounded` non-empty is the non-vacuity claim |
| the source | `corpus/ag-trade/graincorp-capacity-2026-08-04.pdf` (gitignored; `scripts/fetch_corpus.py`) | 1 page; `cor:sha256 ac66b478…` |

## 2. What was measured this session (on `512f82e`)

- Strip: `etkl 2/7  dec 17/17  holon 5/6  tab 1/10  substrate 0/3  frontier 13  ready 9  serves 1/3/34`.
  The 9 ready: etkl:02–06, holon:06, substrate:01–03.
- **Two different "ready" counts; do not conflate them.** The strip's `ready` counts unmet
  criteria that name no `prog:blockedBy` (`scripts/cockpit.py:292`) → 9. The landscape cache's
  §1 `ready` counts unmet criteria whose direct `prog:dependsOn` are met
  (`vocab/queries/arc-ready.rq`) → 15. The tab criteria are in the second and not the first.
  The cache was not stale: regenerated to scratch, `diff -q` was silent.
- The score re-measured at HEAD:

  ```
  $ ./.venv/bin/python -m pytest "tests/test_corpus.py::test_expected_verdict[ag-trade/graincorp-capacity-2026-08-04.pdf]" -q -s -m corpus
    ag-trade/graincorp-capacity-2026-08-04.pdf: score=1.0000 pages=1 chains=[1] wall=16s
    UNADJUDICATED — regions: [('NON_TABLE', 'ignored', 'fewer than 2 lines'), ('NON_TABLE', 'ignored', 'fewer than 2 columns'), ('NON_TABLE', 'ignored', 'fewer than 2 lines'), ('RECORD_TABLE', 'asserted', None), ('NON_TABLE', 'ignored', 'fewer than 2 lines')]
    1 passed in 18.52s
  ```

## 3. What was decided, and where that decision is recorded

- **Subject etkl:02 over holon:06 and substrate.** The maintainer chose it (2026-09-11, in
  session); this file is the only record. holon:06 stays ready: it is fully closable without a
  human read but does not move the product rung. substrate:01–03 is a multi-loop build with zero
  code (the manifest's substrate comment measures the zero).
- **Fresh session rather than an override of the floor.** The maintainer chose this in session.

## 4. Unverified or assumed

- Nobody opened the PDF page this session. 5c's "columns are concepts" is a guess from the
  document's name.
- Whether a `cor:contract` requires `examples/<family>/` placement or can live anywhere was not
  checked. cbh and stem use `examples/shipping/`.
- No suite run; nothing in the tree changed but this file.
