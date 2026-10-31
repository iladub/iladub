# Handoff 2026-10-31: the synthetic contract set is built; owner review, then merge

**Topic:** contract · **Date:** 2026-10-31 ·
**Serves:** maintenance — project 1 of the contract:01 rescope; no criterion yet.

Written at ~130K working tokens (over the 50K originating floor; under the 150K executing floor).
Part 5 is graded per action.

## 5. Next concrete action (written first; typed)

0. **Asserted** (mechanical): in a fresh session, run the FINAL whole-branch review (superpowers:subagent-driven-development § Final Review; most capable model) over `git merge-base main HEAD`..HEAD, with the ledger `.superpowers/sdd/2026-10-31-synthetic-contract-set/progress.md` (gitignored, kept on disk in this worktree) for its deferred minors and rulings. One fix wave, one re-review.
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

## 6. Ledger rulings and deferred minors (verbatim, for the final review and the owner)

- Ruling: Task 4 adds the truth-record shapes to examples/synthetic-contracts/shapes.ttl (and a truth negative) — it owns the Truth model; T7's conformance test needs them — cost if wrong: shapes move between files.
- Ruling: Task 7 adds "examples/synthetic-contracts/README.md" to MANUAL_ALLOWLIST in tests/docgov_extract.py (a README whose commands must run = the Manual class) — cost if wrong: one-line revert and move README prose into synthetic.ttl comments.
- Task 1: minor (deferred): load_manifest no missing-property check; unreachable return 2 in __main__; no captured red run (falsification only)
- Ruling: Task 2 runs now for the three GAFTA maps; the USDA map is a follow-up dispatch once the owner places usda-ffp-cp.pdf — the 403 is the owner's to resolve, the GAFTA maps don't depend on it — cost if wrong: one extra dispatch.
- Ruling: usda-ffp-cp.pdf obtained via owner's Chrome at owner's request (in-page fetch, sha verified d677ebc9… before saving); Task 2 scope widened back to all four maps — cost if wrong: none, sha-pinned
- Ruling: 79B has three single-page table parts (p1 clause-6, p2 clause-7, p2 clause-8), not one p1–p2 span — the page shows clause 6's table ends on p1; maps record what the source supports (CLAUDE.md §7); spec §4.1 nesting still pinned — cost if wrong: one map edit + count test. Tasks 3/6 carry three 79B grids.
- Ruling: clause-8 grid is 4×4 by ruling lines (hand-measured), not find_tables' 2×4 — cost if wrong: grid edit.
- Ruling: wrapped USDA blanks stay one Blank per run (keys .1/.2…); merging is an owner-review item, not an interface change now — cost if wrong: Blank grouping added later.
- Task 2: minor (deferred): test_blanks_inside_their_part near-vacuous (no blank-vs-table disjointness); counts pinned as totals not per page; PartMap.blanks sorted by IRI not reading order; shapes allow partId on blanks; measured constants duplicated in test
- Task 3: minor (deferred): fill .ttl blank-node value order non-deterministic across regenerations (noisy diffs); template-text test is local-only (CI can't catch a values.py regression); 'NN year form stylised
- Ruling: Task 4's Truth.to_turtle must be byte-deterministic (sorted, no blank-node order churn) — truth is generated+committed in Task 7 and diffs must mean change — cost if wrong: noisy truth diffs.
- Ruling: removing rdfs:domain from ten syn: properties is accepted — under inference="rdfs" the domains reclassified truth nodes as PartMap/Part and failed their shapes; SHACL shapes carry the constraints — cost if wrong: vocab says less, restore domains with distinct truth properties.
- Ruling: Task 7 compose prefixes part ids + parent refs per component (m3 = gafta-48-3 twice) — to_turtle refuses duplicate part ids — cost if wrong: part ids in mixed truth renamed.
- Task 4: minor (deferred): truth SHACL test on FILLS[:1] only; value oracle tolerant in y; place_values silently overflows when value wider than blank (producer guard — R89); c._pagesize private; negative test asserts components not (component,focus); out._keep monkey-attach
- Task 5: minor (deferred): 99% converse oracle per-document not per-value; height overflow not refused (ink above blank); _ink uses reportlab private TTF parser; SHACL/no-text-layer tests on 1–2 fills; test _unfilled re-derives the pipeline; full run shows 2 warnings (unidentified); truth.py:24 unused URIRef import (T4)
- Ruling: Word flavour emits no Heading blocks — choosing heading lines would be a geometric reading heuristic (CLAUDE.md §8) and maps carry no heading labels; spec §4.3 lists headings, so this is an OWNER REVIEW ITEM (fix route: hand-mapped heading boxes) — cost if wrong: Word outputs lack heading styles/bookmarks.
- Task 6: minor (deferred): word SHACL test on FILLS[0] only; carries_real_text compares vs whole doc not part boxes; grid edge inclusive both sides (word could land in two cells); bare StopIteration at wordexport.py:442; _inside_box duplicates _inside; subprocess.TimeoutExpired not wrapped + doc may stay open on AppleScript timeout; syn:converter global, not per truth
- Ruling: artifact tests read examples/synthetic-contracts/synthetic.ttl as the syn: declaring file and pinned counts are re-measured — moving syn: into vocab/internal would touch a baseline input (24-min regenerate) — cost if wrong: declaration moves to vocab/internal later.
- Ruling: mixed-truth value keys stay unprefixed (m3 same fill twice, page-scoped) — cost if wrong: prefix values later.
- Ruling: wrote the executed-handoff early (at ~130K) with a **Topic:** line, which clears the pre-existing cockpit failure — cost if wrong: none
- Task 7: minor (deferred): unfilled() truth labelled form-fill; load_mixed doesn't refuse duplicate syn:order; source PdfDocuments del'd not closed; 5047 warnings in run unattributed
