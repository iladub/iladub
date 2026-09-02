# Handoff — the body starts at the stub (spec written, no plan yet)

**Topic:** apple's double header. The predecessor (`2026-09-01-corpus-reach-measured-handoff.md`
§ 5) sent this loop to `infer_column_tree_by_proximity`; the tree was dumped and is **correct**. The
defect is the header/body split typing the years line as body. Spec:
`docs/superpowers/specs/2026-09-02-the-body-starts-at-the-stub-design.md`.

**Part 5 written first, under the floor** (working figure estimated ~55–65K at the time of
writing; `plimslop preflight` reported "unmeasured, no turn recorded", so this is an estimate and
graded as over). Per CLAUDE.md § "The handoff's next action is TYPED".

**Doc impact: increment** (carried from the spec).

---

## 5. The next concrete action — TYPED

### ASSERTED — mechanical

1. **The spec is APPROVED by the maintainer (2026-09-02, in session; recorded here only). Start a FRESH session and invoke `superpowers:writing-plans` on it** — this session stopped at ~98K working tokens, twice the originating floor, and did not write the plan. No plan exists. The spec's
   § 5 names six oracles and § 6 names the three seams the plan must measure before writing a call.
2. **Reproduce § 1.2 before building** (~1 minute): monkeypatch `matrix.header_body_split` to return
   3 on apple p0 band 2 and confirm `region_tiles` is True with a three-level tree. Every figure in
   the spec came from scratchpad scripts that no longer exist; the spec carries their outputs inline.

### PROPOSED — predictions the spec makes that the loop must RUN

- ~~**apple p1's header band asserts a CORRECT reading under the stub rule.**~~ **MEASURED after
  approval, same session — CONFIRMED** (spec § 8 carries the tree: two levels, every data-column
  header word carried, 14 entries, tiles). The accepted drop is honest; the choice stands.
- **`k` from the type split equals `k` from the moved body start on every corpus band.** Measured
  on apple only.
- **The guard (§ 3.2) fires on NO currently-asserted corpus region.** Predicted from WHO's stub
  header being in column 0; the battery (O5) is the test.

### PROPOSED — the maintainer's choice, recorded here and in the spec only

"(A) + (B) refusal, accept the drop" was chosen over settling the adoption gate (C) and over the
eight section-band tiling failures. Reversible; see spec § 4 and § 7.

---

## 1. Goal

Make apple's statement headers assert by deriving the matrix body start from the presence of a
stub cell (AXIOM), and refuse a column tree that drops header ink (producer-side guard).

## 2. Where the primaries are

| primary | what to establish there |
| --- | --- |
| `docs/superpowers/specs/2026-09-02-the-body-starts-at-the-stub-design.md` | The measurements (§ 1), the §8 argument (§ 2), design (§ 3), what is NOT done (§ 4), oracle (§ 5) |
| `src/iladub/etkl/headers.py:84` + `vocab/queries/header-body-split.rq` | The type transition that places the years line in the body. **Untouched by this loop** |
| `src/iladub/etkl/matrix.py:39` (`infer_column_tree_by_proximity`) | Where the guard goes; the tree is otherwise correct on apple p0 |
| `src/iladub/etkl/rows.py:24` (`logical_rows`) | Why the wrong split refuses: the anchor column |
| `vocab/queries/adoption-candidate.rq` | The `NOT EXISTS tab:EntryCell` gate that costs page 1 its adoption |
| `tests/corpus-manifest.ttl` (apple, `cor:rationale`) | Carries the census figures this loop supersedes — the Doc impact increment |

## 3. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The subject moved from the column tree to the matrix body start | spec § 1; this file; nowhere else yet |
| A: AXIOM derivation, matrix-scoped, `header-body-split.rq` untouched | spec § 2, § 3.1 |
| B: producer-side guard, justified by CLAUDE.md § Producer-side guards | spec § 2, § 3.2 |
| C: the score drop is accepted; the adoption gate becomes a residue | spec § 1.4, § 7 — **maintainer's choice, this session** |
| No new escalation reason, no label grouping | spec § 4 |

## 4. Unverified or assumed

- Everything in spec § 8.
- The full corpus battery has not run in seven loops; the spec's O5 is the first run.
- The `-m "not corpus"` suite was not run this session (no `src/` change yet).
- The working-token figure above is an estimate.
