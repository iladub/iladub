# Handoff — the membrane returns a verdict, it does not crash

**Pointers, plus one block of evidence that has no other home (§3).** Nothing here is settled because
it appears here.

Authored at **60,985 working tokens — 1.22× the 50,000 originating floor**, `handoff` logged. Part 5
was written **first**, per the rule this session added to CLAUDE.md § Loop & context hygiene
(`bb5abc4`) — this handoff is the first test of that rule, by its own author, and that is the point.

## 5. The next concrete action — TYPED

**One loop: four register rows whose closure is a repair. `R129`, `R133`, `R131`(a), `R128`.**
Branch off `main` once **PR #134** is merged (it was pending at authoring time).

### ASSERTED — the outcome is known; doing it *is* the work

Each was **driven, not read**, at `5bc6b00` (§3), and each has a named falsifying oracle.

| row | the change | oracle that must go RED first |
|---|---|---|
| `R133` | `_validate` answers explicitly on `legs=()` instead of `IndexError`. The row says **prefer refuse** — a validation that checked nothing and returned `True` is failing upward, which § Core design principles 7 forbids | `_validate(Graph(), legs=())` returns a refusal verdict rather than raising `IndexError` |
| `R128` | a shape targets the subjects of `dec:supersedes` — `sh:nodeKind`/`sh:class` on the object, cardinality on the arc | conforming example passes; negative example must fail. Per CLAUDE.md § Serialization |
| `R129` | one guard, called from the **5** unguarded mint sites, refuses a non-IRI suggester **as a verdict** carrying the offending value | a non-IRI `suggester_iri` yields `MembraneRefusal`/`AssertionError`, not a bare `Exception` |
| `R131`(a) | `compile.py:1173` raises `MembraneRefusal` rather than a bare `AssertionError`, so one `except` clause sees both scopes | a page-scope refusal is catchable as a membrane verdict |

**The seam `R131` hides, which the implementer must MEASURE before writing its test** (plan rule 3):
the reproduction that established `R131` **injected** the refusal by patching `_validate`. Nobody has
constructed real input whose page graph genuinely violates a `tab` shape. So: *can a tracked corpus
document produce a page-scope refusal at all, or must the oracle inject one?* Answer that before
authoring the test — an injected-only oracle is a weaker claim and must say so.

**`R131`(b) — minting page-scope health — is NOT in this loop.** It is the modelling half, and the
row itself says the two are separable. Closing (a) alone **must not strike the row**; record the half.

### PROPOSED — rests on a decision that could change the loop; NOT in scope

- **`R127`** (uncapped `dec:rationale`) is AXIOM and small, but its own "what would close it" requires
  **four shipped oracles in `tests/etkl/test_membrane_health.py` (`:182`, `:362`, `:422`, `:552`) to
  be re-homed IN THE SAME ACT**, and forbids deleting them. That is a second decision wearing a
  one-line fix's clothes.
- **`R132`** (one `_DOC` for every document) is identity plumbing over 10 occurrence sites and 4
  dependents, but the row is explicit that the hard part is an **identity/merge ruling**, not the edit.

Both reproduce at HEAD. Neither should be bundled in without being ruled first.

## 1. Goal

Close four rows by repair. The defect rate is flat; the **3.93 : 1 raise:close ratio** is what is
degrading — see `docs/superpowers/2026-08-29-defect-rate-measurement.md`.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/residues-open.md` rows `R127`–`R133` | The full rows. **An index line is a pointer, not the residue** — open the row |
| `docs/superpowers/residues.md` | The index and the conventions. A closure **strikes** the row and records evidence in place; it does **not** delete it |
| `CLAUDE.md` § Core design principles 8 | The neurosymbolic gate. `R129` and `R133` are **PROCEDURAL and must justify irreducibility in the code**; `R128` is AXIOM |
| `CLAUDE.md` § Producer-side guards vs the membrane | Directly on point for `R129`: a producer-side guard is not a duplicate of the membrane |
| PR #134 / `R151` | The corrected row, and the arc work this loop deliberately does not touch |

## 3. What was decided, and where that decision is recorded

- **`R151`'s remedy is refuted and corrected in place** — PR #134, `a8dcee9`. Recorded in the row.
- **The handoff's part 5 is typed** — PR #134, `bb5abc4`, CLAUDE.md § Loop & context hygiene.
- **`R127` and `R132` are excluded from this loop.** Recorded **here and nowhere else** — reversible.
- **The four asserted rows were verified reproducing at `5bc6b00` with ZERO line drift.** This has no
  other home, so it is recorded here rather than pointed at:

  ```
  R127  vocab/shapes/dec-shapes.ttl:60-63 ✓   escalation-furnish.rq:70/79 ✓   driven end-to-end
  R128  git grep supersedes -- vocab/shapes/ → exit 1 ✓        declared dec.ttl:173-175, no SHACL
  R129  membrane.py:318 / :347-348 ✓          driven through the PUBLIC _validate seam
  R131  compile.py:1173 ✓                     driven — but by INJECTION (see the seam above)
  R132  compile.py:22 ✓  document.py:1335 ✓   driven, two documents, identical health subject
  R133  compile.py:504-525, :523 ✓            driven
  ```

## 4. Unverified or assumed

- **`R131`'s "a real document does this" half is NOT established** — see the seam in part 5.
- **`R133`'s deferral rationale is unverified**: the row says it is "unreachable today" because one
  total function supplies every `legs` tuple. `_legs_for_document`'s returns were **not** re-enumerated.
- **`R132`'s blast radius has drifted**: the non-docs figure of 6 still reproduces exactly, but its
  parenthetical "14 including `docs/`" is now **15**.
- **The register index has degraded 3.08× since it was split** — 11,275 bytes at `db5e5b5`
  (2026-08-12), 34,710 now; `residues-open.md` is ~50k tokens and `residues-closed.md` ~30k. The
  cause is visible in the rows: closure evidence is being written into the **index** line as well as
  the detail file. The split existed because the register had stopped being readable at ~36.7k.
  **Raised as an observation, not a row** — the standing goal is closing rows, not opening them, and
  nobody has ruled whether this is a defect or the convention working as intended.
- **Branch protection is still NOT applied** — `gh api repos/iladub/iladub/branches/main -q .protected`
  → `false`, `allow_auto_merge` → `false`, re-measured this session. `--auto` remains a no-op.
- The 150K executing floor is still labelled `NO SOURCE` in `tiers.py`.
