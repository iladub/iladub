# Handoff 2026-10-31: the synthetic contract set is built; owner review, then merge

**Topic:** contract · **Date:** 2026-10-31 ·
**Serves:** maintenance — project 1 of the contract:01 rescope; no criterion yet.

Written at ~130K working tokens (over the 50K originating floor; under the 150K executing floor).
Part 5 is graded per action.

## 5. Next concrete action (written first; typed)

1. **Asserted** (mechanical): the owner reviews PR #386's owner items (§ 3 below): the four part maps
   (flip `syn:review "draft"` → `"owner-reviewed"`), the Word converter, the no-headings ruling, the
   wrapped-USDA-blanks ruling. Then take #386 out of draft; merge when `test` is green.
2. **Proposed** (may fail, found in minutes): CI `test` goes green on #386. The one pre-existing red
   (`test_cockpit.py::test_the_live_newest_handoff_declares_a_topic`, red on 2eff2f0 because the newest
   handoff lacked `**Topic:**`) is fixed by this handoff's Topic line — 32 passed locally.
3. **Proposed**: brainstorm project 2 (document router) in a fresh session, consuming
   `synthetic/out/*.pdf` + `examples/synthetic-contracts/truth/`.

## 1. Goal

39 fake filled-contract PDFs (12 fills × form-fill / handwriting-scan / word-export + 3 mixed) and
39 generator-written truth records from four local templates — done, subagent-driven, 7 tasks.

## 2. Where the primaries are

- Plan: `docs/superpowers/plans/2026-10-31-synthetic-contract-set.md`; spec
  `docs/superpowers/specs/2026-10-31-synthetic-contract-set-design.md`.
- Code `scripts/synthetic_contracts/`; data `examples/synthetic-contracts/`; README there.
- Commits 38bfc52..9b2509d on branch `contract-rung-spec` (PR #386).
- Rebuild: `python -m scripts.synthetic_contracts fetch` then `build` (README). The USDA template
  403s for scripts on omb.report; it was fetched through the owner's browser and sha-verified.

## 3. What was decided, and where (controller rulings — owner to confirm)

All in the PR body; each with what it costs if wrong.
- 79B: three single-page tables (the page shows clause 6's table ends on p1), not one p1–p2 span.
- Wrapped USDA blanks: one Blank per dot-leader run (`.1`/`.2` keys), independent values.
- Word flavour emits **no headings** (choosing heading lines would be a geometric reading heuristic);
  spec § 4.3 lists headings — owner item.
- Converter: Microsoft Word 16.114.3 via osascript, saving inside Word's container (no dialog).
- `rdfs:domain` removed from ten `syn:` properties (RDFS retyped truth nodes as maps).
- `syn:` declared in `examples/synthetic-contracts/synthetic.ttl` (not `vocab/` — a baseline input);
  artifact/query declaration tests read it; pins re-measured 189 → 253.
- README in `MANUAL_ALLOWLIST` (`tests/docgov_extract.py`).

## 4. Unverified

- The full suite after fix round 1 was not re-run end to end (targeted 251 passed).
- Handwriting and Word flavours are local-only (macOS fonts, cv2, Word); CI skips them.
- Deferred minors from every task review are in the PR body for triage.
