# Handoff — the WHO subject relocated a third time, and the spec is written

**Topic:** `R45`. The predecessor's § 5 directed a re-argument of `CLAUDE.md` §8 against
`infer_column_tree_by_proximity`'s Voronoi span assignment. That framing was **refuted by
measurement**: the assignment is correct and unchanged in the spike that makes WHO tile. The subject
is `_level_tops` (`matrix.py:34-36`). A spec is written, reviewed against its own falsification, and
open as **PR #145** (branch `r45-a-header-level-is-a-band-line`, commits `1d56133` + `e95ae7b`).
**No `src/` or `tests/` file was changed by this session**; every spike was a scratchpad
monkeypatch and `git status` was clean throughout.

**This handoff was authored at ~90k working tokens — 1.8× the originating floor.** Part 5 is graded
per action per `CLAUDE.md` § "The handoff's next action is TYPED". Parts 1-4 are pointers and do not
degrade.

Part 5 is written first.

## 5. The next concrete action — TYPED

### ASSERTED — execute the spec; the outcome is known and doing it IS the work

**`docs/superpowers/specs/2026-08-31-a-header-level-is-a-band-line-design.md`.** It is a contract:
interfaces and invariants in §5, oracles in §7, scope-out in §8, unverified in §9. Nothing in it
needs re-deriving. Two reasons this is asserted rather than proposed: the change was **measured
end-to-end before the spec was written** (WHO `0.559748427672956 → 0.909596662030598`, 3 → 0
escalations), and the `-m "not corpus"` baseline is **green** (`1379 passed, 7 skipped, 46
deselected, 1 xfailed in 1314.82s`).

Do it in this order, because the third step fails if the first two are skipped:

1. **Re-point `test_corpus_census_every_live_escalating_decision_is_furnished` FIRST**
   (`tests/etkl/test_escalation_furnish.py:222-243`). It selects WHO *because it escalates with
   nothing withdrawn* and asserts `len(escalating) > 0`. **It fails by design when this loop
   succeeds.** Spec §6.1 names the seam and explicitly does **not** name the answer: measure B, C
   and superseded per candidate with `_census` itself — the region-level counters in §3.4 are the
   wrong coordinate system for that decision.
2. **Write the fixture and show it RED at HEAD** (spec §7.1). `crosstab_table_pdf`
   (`fixtures.py:347`) is the template; three leaf labels at `top - 13.0`, three at `top - 13.9`.
   Per plan-rule 1 this is a **plan-supplied test and therefore a proposition** — if it cannot be
   made red at HEAD, that is a spec defect to report, not an assertion to weaken.
3. **Then delete `_level_tops`** and make the level the band line (spec §5).
4. **Then the consumer surface** — spec §6.2 (the HOLD adjudication in
   `tests/corpus-manifest.ttl:118-129`), §6.3 (five arc-manifest sites), §6.4 (three comment pins).

**§6 is the loop's real cost, not §5.** The code change is a few lines; the enumeration is the work.

### ASSERTED — what is measured and what it does NOT license

- **`apple` is unchanged** — its 2 `MATRIX_AMBIGUOUS` survive byte-identically. `R62` stays open and
  `prog:criterion:tab:05` stays `prog:met false`. **This loop closes `R45`, not the criterion.**
- **The corpus battery is LOW POWER and the spec says so in §3.4.1.** Reach probe, calls to
  `infer_column_tree_by_proximity`: `graincorp-stem 0 · graincorp-capacity 0 · bfs 0 · ons 0 ·
  cbh 0 · apple 2 · who 3`. **Five of six "PASS" rows are vacuous** — `graincorp-stem`'s 0.95 floor
  is protected by **non-reach, not robustness**. The entire negative evidence in the corpus is
  `apple`, reached twice, tree identical both times. **Do not cite "six documents unchanged" as
  safety evidence**; that claim was made in this session's first report and corrected in `e95ae7b`.
- **`R154` is irrelevant to `R45`, now confirmed a second independent way.** The tree that *passes*
  still carries all seven chopped fragments. Broken labels, correct structure, document tiles.

### PROPOSED — `R154` next, and the reason is a consequence this loop creates

After this ships, WHO asserts a table whose top-level header nodes read `'Z-s'`, `'res (weight'`,
`'kg)'` — structurally correct, textually wrong. **That is a known-bad text payload shipping as an
assertion**, which is the strongest argument yet for prioritising `R154`. Graded proposed because
nothing was measured about `R154`'s fix cost this session, and its own row warns the discriminator
must be tolerance-free (the census refutes any cluster-grouping constant — clustering is a
per-document property).

### PROPOSED — blocked on rulings, unchanged and NOT re-derived

`R132`, `R127`, `R131`(b). Open `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5.

## 1. Goal

Discharge the predecessor's § 5 by running its falsifications before building on them, relocate the
WHO subject to wherever the measurement puts it, and write the spec.

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-08-31-a-header-level-is-a-band-line-design.md` | **THE contract.** §3.4.1 (why the oracle is weak), §6 (the consumer surface), §7 (falsification), §9 (unverified) |
| `src/iladub/etkl/matrix.py:34-36` (`_level_tops`) + `:57` | **THE SUBJECT.** The `round(w.top,1)` level derivation and the `< 0.5` label filter. Two references only, both in this file |
| `src/iladub/etkl/headers.py:386` (`header_rows_of`), `:406-408` | The prior art: the primary header path derives levels as **rows of the band**. The §8 AXIOM argument leans on this |
| `src/iladub/etkl/geometry.py:459` (`text_lines`), `:263` (`rule_aware_lines`) | Both group rows on `0.6 × median glyph height`. The tolerance this loop consolidates *toward*, and does not remove |
| `vocab/shapes/tab-shapes.ttl:127` (`tab:UnambiguousAccessShape`) | The refusing shape. **It is correct and is NOT modified** — only the tree fed to it was wrong |
| `tests/etkl/test_escalation_furnish.py:222-243` | The test that fails by design when this loop succeeds. Read its docstring before touching it |
| `tests/corpus-manifest.ttl:118-129` | WHO's HOLD adjudication — *"Held until that header block is read."* That condition is now discharged |
| `docs/superpowers/residues-open.md`, `R45` / `R154` / `R62` | `R45` closes here; `R154` and `R62` do not |
| PR #145 | The two commits and their messages; `e95ae7b` is the correction of a claim `1d56133` got wrong |

## 3. What was decided, and where that decision is recorded

- **The subject moved from `infer_column_tree_by_proximity`'s span assignment to `_level_tops`'
  level derivation**, refuting the predecessor's § 5 framing. Recorded in the spec §2 and PR #145;
  **nowhere else; reversible.**
- **Classified AXIOM on a FRESH argument** — spec §4, four numbered grounds. The maintainer's
  earlier AXIOM ruling was made about the refuted subject (word-atomicity) and was **deliberately
  not inherited**, as the predecessor's handoff instructed. **Not ratified by the maintainer this
  session** — recorded in the spec only, and reversible.
- **The `band.lines` vs `group_wrapped` fork settled as `band.lines`**, on the measurement that
  `header_rows_of` dereferences the same index as `band.lines[body_line].top` (`headers.py:407`).
  Spec §5; reversible.
- **The corpus oracle re-graded to low power** after the reach probe. Spec §3.4.1, commit `e95ae7b`.
- **No code was written, deliberately.** The session's mandate was part 5 of the predecessor
  handoff, which ended at a spec.

## 4. Unverified or assumed

- **The AXIOM classification has NOT been ratified by the maintainer.** It is the spec's argument,
  not a ruling. §8 routes *"which columns does X span"* to NEURAL by wording, and the case that this
  subject is a different question is made in spec §4 — it should be read adversarially before code
  is written.
- **Only TWO corpus documents exercise the cross-tab path at all** (`apple`, `who`). Any claim about
  this change across header geometries rests on those two plus the §7.1 fixture. See §3.4.1.
- **Whether other corpus documents contain sub-point header drift is UNKNOWN** — five never reach
  the function, so the corpus cannot answer it for them either way.
- **The WHO tree under the fix was checked structurally against `extract_words` output, not against
  the published WHO table by a human.** The tiling oracle certifies consistency, not fidelity.
- **The `-m "not corpus"` suite was measured green at `22263a2`'s CODE, on branch HEAD `1d56133`**
  (`git diff --stat 22263a2 1d56133` = 1 file, docs only). It has **not** been run since `e95ae7b`,
  which is also docs-only.
- **`--timeout=0` is unusable in this tree** — `pytest-timeout` is not installed; pytest exits with
  `unrecognized arguments`. Two sessions have now paid for this.
- **The apple tree was dumped only as a diff-vs-baseline** (identical, twice). Whether its 2
  `MATRIX_AMBIGUOUS` share WHO's mechanism is **still unknown, seven loops on.**
- **The ~90k working-token figure is from the harness context line**, not a `plimslop` measurement;
  `preflight` reported "unmeasured, no turn recorded for this project" on the first call this
  session.
