# Handoff: R318 closed; loop (b), the band-role reading, is next (2026-10-15)

**Serves:** prog:criterion:tab:07 — loop (b) of `2026-10-15-r44-subject-chosen-handoff.md` § 5.2.
Verify `prog:met false` on tab:07 before starting.

**Topic:** compile · **Date:** 2026-10-15

**Doc impact: none.** A handoff.

Part 5 was written first, at about 95K working tokens. That is over the 50K originating floor, so it
names a subject and an oracle question and stops there. It contains no design.

## 5. The next concrete action, typed

1. **ASSERTED:** start loop (b) in a fresh session. The design is the R44 handoff's § 5.2 (b), which
   still stands. Escalated regions now carry their exact `band_text`, which is the input (b)'s
   oracle was waiting on.
2. **PROPOSED, may fail in minutes:** that a role oracle can be named before a worker exists ("no
   oracle, no worker", CLAUDE.md § 8). The R44 handoff warns that a context-carrier role fits the
   7-document corpus but not held-out fed-h41, where three `REGION_TILING_FAILED` firings are table
   body rows. The spec's first measurement is whether any oracle separates those three from bfs/ons
   captions and footnotes **without a tuned constant**. If none does, the spec is about the oracle,
   not the worker.

## 1. Goal

Done this loop: every `escalate_region` site carries `bands.band_text` (R318). Spec:
`docs/superpowers/specs/2026-10-15-escalation-carries-exact-text-design.md`.

## 2. Where the primaries are

- Code: `src/iladub/etkl/compile.py` (`surface_text`), `holon.py` (`escalate_region`,
  `assert_hier_region`), `ruleguard.py`. `RegionReport.ascii` is now `RegionReport.text`.
- Oracle: `tests/etkl/test_r318_exact_surface_text.py`.
- Register: `~~R318~~` in `residues-closed.md`, with the falsification and corpus evidence.
- Adjudications: the end of `tests/corpus-manifest.ttl` (bfs, ons).

## 3. What was decided, and where it is recorded

- The seam: `compile_tables` accepts only a PDF, so the oracle compiles reportlab fixtures. One
  fixture per reason, measured over every `*_pdf` builder. ROW_GROUP_AMBIGUOUS and ROUND_TRIP_FAIL
  are reached by a forced oracle refusal, the precedent being `test_tiling_gate`. Recorded in the
  test's docstring.
- Spec § 4.3's prediction held exactly: `graph_sha256` moved on arxiv, bfs, fed-h41, ons and
  who-covid, and nothing else moved. The separate `-rt` pre-count was skipped, because an
  unexpected `-rt` candidate on apple or caltrain would itself have moved their sha.

## 4. Unverified or assumed

- R319 (token unit) and R320 (extractor segmentation) stay open. Both are now structural park
  candidates (`residue_graph.py --candidates`). Parking them is the maintainer's call, not a loop's.
- The misleading comment near `compile.py:1864` ("ROUND_TRIP_FAIL never reaches escalate_region")
  is still uncorrected. Spec § 6 left it, by plan rule 7.
