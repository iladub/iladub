# Handoff — `R45` is closed: a header level is a band line

**Topic:** `R45` **and, unplanned, `R98`** — executed from `docs/superpowers/specs/2026-08-31-a-header-level-is-a-band-line-design.md`
exactly as its predecessor's part 5 asserted. `matrix._level_tops` is deleted; a header level is now
`band.lines[:split]`. WHO `0.5597 → 0.9095966620305981`, 3 `MATRIX_AMBIGUOUS` escalations → 0, and
its corpus adjudication moves from a recorded HOLD to an acceptance with `cor:scoreFloor 0.90`.
**`R98` closed as a side effect, and the register's own rot-guard found it, not a person**: WHO's
continuation-licence refusal on pair `(1, 2)` was always recorded on the report, but the
`tab:licenceRefused` graph fact is written only when both refused regions asserted a table — which
is now true. `tab:LicenceRefusalShape` went LIVE and `test_no_registered_shape_has_gone_live` went
RED before anything was edited. Branch `r45-a-header-level-is-a-band-line`, PR #145.

Part 5 is written first, per `CLAUDE.md` § "The handoff's next action is TYPED".

## 5. The next concrete action — TYPED

### PROPOSED — `R154`, and this loop is what makes it urgent

`R154`'s row (`docs/superpowers/residues-open.md`) is the primary; **open it, do not plan against
this paragraph.** The argument this loop adds is a *consequence it created*: WHO now **asserts** a
`tab:HierarchicalTable` whose top-level header nodes read `'Z-s'`, `'res (weight'`, `'kg)'`.
Structurally correct, textually wrong — a known-bad text payload that has crossed the membrane as an
assertion rather than sitting in an escalation. Before this loop it was quarantined by an escalation;
now it is carried. That is a real change in what the corpus asserts and it is recorded in WHO's
acceptance rationale (`tests/corpus-manifest.ttl`) rather than left implicit.

**Graded PROPOSED, and the prediction that must be run first:** `R154`'s own row states the
discriminator must be tolerance-free and that a prior loop's word-atomicity spike made things
*worse* (`0.5597 → 0.5514`), collapsing `header_body_split` from ≥2 to 1. **Nothing about `R154`'s
fix cost was measured this session.** A session that treats "fix R154 next" as a plan rather than a
hypothesis will spend a day discovering what that row already says.

### ASSERTED — what is measured, and the three things it does NOT license

- **WHO** `0.9095966620305981` (= 654/719), tokens `445/350 → 654/65`, verdicts `escalated 3 → 0`
  (10 asserted, 8 ignored). **The spec §3.3 figure `0.909596662030598` is one digit short** of the
  value `repr()` gives; same float family, transcription slip, corrected here and in the manifest.
- **The other six documents are byte-identical** on score, every verdict counter, every escalation
  reason, `tokens_asserted`, `tokens_escalated`, `adopted` and `repaired_bands` — including
  **apple's `MATRIX_AMBIGUOUS x2`, which survives**. `R62` is untouched.
- **Do NOT cite "six documents unchanged" as safety evidence.** Spec §3.4.1's reach probe:
  `graincorp-stem 0 · graincorp-capacity 0 · bfs 0 · ons 0 · cbh 0 · apple 2 · who 3` calls to
  `infer_column_tree_by_proximity`. Five of six PASS rows are **vacuous**. The whole negative
  evidence is `apple`, reached twice, tree identical both times, plus the new fixture.
- **`prog:criterion:tab:05` stays `prog:met false`**, now on `R62` alone; **`tab:10` stays
  `prog:met false`**, now on `R97`/`R99`/`R100`. The rung moved `etkl 1/7 → 2/7`; the `tab` rung did
  not move.
- **`R98` is closed on the FIRST of the two outcomes its own row named** — a specimen, not a proof
  that the state is unreachable. Measured: `refused_licences == ((1, 2),)` **unchanged**, and one
  `tab:licenceRefused` edge, `p2#mtable1 -> p1#mtable2`. Nothing was written unconditionally and no
  fixture was authored; an unrelated reading fix changed which state the corpus reaches. That is
  worth carrying forward as a pattern: **a vacuity registration can be discharged by a loop that was
  not about it**, so the rot-guard is the instrument that matters, not the row's own prediction.
- **The `0.6 × median glyph height` tolerance is consolidated, not eliminated.** `text_lines` and
  `rule_aware_lines` still own it. Three places deciding what a line is became two, not zero.

### PROPOSED — blocked on rulings, unchanged and NOT re-derived

`R132`, `R127`, `R131`(b). Open `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5.

## 1. Goal

Execute the R45 spec end to end: re-point the census test, ship the falsifying fixture, delete
`_level_tops`, and carry the whole consumer surface (§6) that WHO's escalation was feeding.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `src/iladub/etkl/matrix.py` (`infer_column_tree_by_proximity`) | **THE CHANGE.** `_level_tops` gone; `levels = band.lines[:split]`; module + function docstrings say why |
| `tests/etkl/fixtures.py::crosstab_drifting_leafrow_pdf` | The falsifying fixture: `crosstab_table_pdf` with Q2's three leaf labels drawn 0.9pt below Q1's |
| `tests/etkl/test_matrix.py::test_sub_point_leaf_drift_is_one_header_level` | Tree-level oracle: the drifted tree must equal the undrifted one node for node |
| `tests/etkl/test_closing_slice.py::test_crosstab_with_sub_point_leaf_drift_compiles` | End-to-end oracle: `score == 1.0`, a typed `tab:HierarchicalTable` |
| `tests/etkl/test_escalation_furnish.py` (`BFS`, the census test) | Re-pointed off WHO. Its docstring carries the measured B/C/superseded for bfs **and** why apple was rejected |
| `tests/corpus-manifest.ttl`, the `who-wfa` node | `cor:CompilesAbove` + `cor:scoreFloor 0.90` + an **appended** 2026-08-31 adjudication. The 2026-08-20 HOLD is kept, not repaired |
| `tests/arc-manifest.ttl` | `etkl:07` met (+`metOn`), `tab:05` loses its `R45` edge, the `etkl:07 → tab:05` proposed edge **deleted with its reason recorded**, three census comments annotated not rewritten |
| `docs/superpowers/residues-closed.md`, `~~R45~~` | The closure row and, at its end, the five things this closure does **not** license |
| `docs/superpowers/residues-closed.md`, `~~R98~~` | The unplanned closure: what made the shape live, and that it was NOT the route the row prescribed |
| `tests/etkl/test_vacuity_registry.py` | Where the `TAB.LicenceRefusalShape` row was, now a comment carrying its measurement |
| `docs/superpowers/specs/2026-08-31-a-header-level-is-a-band-line-design.md` | The contract this executed. §3.4.1 and §9 are the parts still live |

## 3. What was decided, and where that decision is recorded

- **`bfs-population` replaces `who-wfa` as the escalation-census document.** Measured with `_census`
  itself, not inferred from region counters as the spec warned: `bfs B=10 C=10 superseded=0 live=10
  requests=10`; `apple B=15 C=15 superseded=5` — rejected because 5 of its 15 are withdrawn, so it
  lacks the "none withdrawn" property the test's choice rests on, and `cbh-stem` already covers the
  wholly-superseded case. Recorded **in the test's docstring**; reversible.
- **WHO accepted at `cor:scoreFloor 0.90`** — at-or-below the measured score per the manifest
  header's own rule, never the measured value. Recorded in `tests/corpus-manifest.ttl`; reversible.
- **The `etkl:07 → tab:05` proposed edge is DELETED, on the measurement not the argument.** Its
  rationale said who-wfa fires `MATRIX_AMBIGUOUS` and nothing else; it now fires nothing, and with
  `etkl:07` met the edge would also trip `arc-shapes` M15. A comment records that it existed and why
  it stopped being true.
- **`test_arc_manifest.py`'s pinned acceptance count moved 1 → 2 by hand**, which is what that test
  is designed to force. Its docstring's `etkl 1/7` is annotated rather than silently corrected.
- **The AXIOM classification is the spec's argument (§4), still NOT ratified by the maintainer.**
  Recorded in the spec and the closure row; nowhere else; reversible.

## 4. Unverified or assumed

- ~~The `-m "not corpus"` unit suite has NOT been observed green on this tree.~~ **RESOLVED:**
  `./.venv/bin/python -m pytest -m "not corpus" -q` on the committed tree →
  **`1381 passed, 7 skipped, 46 deselected, 1 xfailed in 1302.05s (21m42s)`**. An earlier run of the
  same command, taken mid-loop, failed on `test_residue_register_integrity.py` alone — a **register
  format error, not a code one**: the index row for a closed residue keeps its plain id
  (`| R45 | closed | …`); only the DETAIL row is struck (`| ~~R45~~ |`). `_INDEX_ROW`
  (`tests/test_residue_register_integrity.py`) does not match a struck index id, so striking one
  orphans the detail row. Worth knowing before closing the next residue — `CLAUDE.md`'s "strike the
  row" is about the detail file.
- **The `-m corpus` battery ran: `1 failed, 45 passed, 1389 deselected in 1282.70s`.** The single
  failure was the predicted one — `test_no_registered_shape_has_gone_live` on
  `tab:LicenceRefusalShape` — and it is fixed by deleting that registry row (see part 3). The
  battery has **not been re-run end to end since that deletion**; only
  `tests/etkl/test_vacuity_registry.py -m corpus` was (**5 passed, 4 deselected in 336.77s**). CI on
  PR #145 is the end-to-end check.
- **`tests/etkl/test_vacuity_registry.py`'s `iladub:CandidateConcept` on 3 of 7** (apple, bfs,
  who-wfa) was not re-measured directly, but the row's test passed in the battery above.
- **`prog:source "tests/corpus-manifest.ttl:118"`** on `etkl:07` is a line pointer into a file this
  loop grew by 2 lines above that point. `test_etkl_criterion_sources_point_at_the_document_they_name`
  passes, so it still resolves — but the class of hazard is `R139`'s and it was not re-derived.
- **Fidelity is unchecked.** The tiling oracle certifies consistency. Nobody has read WHO's carried
  table against the published PDF, and `R154` guarantees its top-level labels are wrong.
- **No `plimslop` working-token figure exists for this session** — `preflight` reported "unmeasured,
  no turn recorded for this project" on its only call. The shape was logged as *executing*.
