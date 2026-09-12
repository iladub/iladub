# Handoff — R212's carrier: the plan is written, execute it

**Topic:** the-carrier-plan
**Serves:** prog:criterion:etkl:02 — R212 is a prerequisite of that criterion's measures, not a
criterion of its own.
**Date:** 2026-09-12. **Branch:** `r212-carry-the-ignored-band`, cut from `main` at `353eadc`.
**Plan:** `docs/superpowers/plans/2026-09-12-the-ignored-band-carries-its-text.md`.
**Spec:** `docs/superpowers/specs/2026-09-12-the-ignored-band-carries-its-text-design.md`.

**Doc impact: none.** This loop ships a plan and no code. Nothing queues for a release, nothing
blocks one. (The plan it ships *declares* `Doc impact: increment` for the loop that executes it.)

This loop wrote the plan the previous handoff's § 5a ordered, took the four corrections from the
evidence rather than the spec, and took the two decisions the evidence left open. **Part 5 was
written first.**

## 5. The next concrete action

### 5a. ASSERTED: execute the plan, task by task. Do not re-plan.

The design is settled (spec), the claim it rested on is measured (evidence § 1), the four seams are
measured (evidence § 2–5), and the five decisions a plan had to take are taken in the plan's
§ *The five decisions*. A fresh session opens the plan and starts at Task 1.

**What is NOT open, and must not be re-litigated:** the vocabulary choice (three candidates refused
with measured reasons, spec § 3); the two 2026-09-12 rulings (**all** ignored bands are carried; the
term lives in **`etkl:`**); and the membrane home (plan DECISION D, with the measurement that decides
it — see § 2 below).

This is asserted, not proposed: every step is mechanical, and where a step could still surprise the
implementer the plan names the measurement to take first rather than the answer to assume
(DECISION B's reason-totality, DECISION D's focus-node census, Task 2's fixture banding).

### 5b. PROPOSED: a compiled PAGE graph carries no `etkl:` triple today, so the carrier's node will be the first

Plan DECISION D validates a real compiled page graph against the whole of `etkl-shapes.ttl` and
requires that `etkl:IgnoredBandShape` be the only shape with focus nodes. **Prediction: it is** —
`compile.py` never mentions the `etkl` namespace at all (the `ETKL = Namespace(...)` binding lives in
`document.py:119`, `federate.py:19` and `bridge.py:12`, not in `compile.py`), so no
`etkl:DocumentProjection` and no `etkl:CompiledDocumentHolon` can exist in a page graph for
`DocumentProjectionShape` or `MembraneHealthShape` to target.

**Reasoned from a grep, not from running pySHACL over a compiled graph.** The prediction is scoped to
**page** graphs: at *document* scope the same check would be different, because `document.py` does
emit `etkl:` terms (`:1277` mints an `etkl:MembraneValidation`; `:1323` manages
`etkl:membraneHealth` on `_DOC`) — so a later loop that validates a *document* graph against this
file should expect `MembraneHealthShape` to fire too, and that is not a defect.

If 5b is wrong, the plan gains one measured line in Task 3's report and nothing in its design moves.
Cheap to refute: compile the Task 2 fixture and count focus nodes per shape.

### 5c. What this loop deliberately leaves exposed

[[R218]] and [[R219]], untouched. No new residue raised: this loop shipped no code and measured
nothing that deferred. The plan's Task 5 Step 2 names the two rows the *executing* loop may need to
raise, conditional on what it finds.

## 1. Where the primaries are

- **The plan** — `docs/superpowers/plans/2026-09-12-the-ignored-band-carries-its-text.md`. Read
  § *Global Constraints*, then § *The invariant, stated ONCE*, then § *The five decisions*, before
  any task. The tasks cite those sections rather than re-deriving them (plan rule 6).
- **The evidence it rests on** — `docs/superpowers/2026-09-12-r212-invariant-arm-evidence.md`
  (§ 1 the invariant, § 2 the refuted producer, § 3 the constructible oracle arm, § 4 the import
  cycle, § 5 the membrane).
- **The spec** — unchanged; § 3 the reading and the three refusals, § 4 what the loop does NOT do.
- **The criterion** — `tests/arc-manifest.ttl:210-219`; hold note `tests/corpus-manifest.ttl:56-57`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The term is `etkl:IgnoredBand` + `etkl:bandText` + `etkl:bandIndex` | plan DECISION A |
| The classifier's reason is carried **iff measured total** — the plan names the enumeration, not the answer | plan DECISION B |
| The subject is `{doc}#ignored{idx}`, **distinct** from the `{doc}#region{idx}` the branch already mints for unit markers (`compile.py:819-820`) | plan DECISION C |
| **The shape is NOT wired into the compile membrane** — measured: `_validate` runs only when the page graph already holds a `tab:RecordTable`/`tab:HierarchicalTable` (`compile.py:1441-1445`), so a page of pure furniture never reaches a shape at all. Wiring would look total and be silently absent exactly where the carrier matters most | plan DECISION D |
| Consequently handoff-before-last's § 5b ("a wired carrier shape costs zero vacuity-registry rows") is **left untested by design**, not confirmed | plan DECISION D, Task 3 |
| `_band_text` moves to `bands.py` and becomes public; **four** references follow it, not two (`:476, :480` are prose, `:594, :598` are calls) | plan DECISION E, Task 2 |

## 3. Unverified or assumed

- **5b is unrun** (above) — the one prediction this handoff makes.
- **The reportlab fixture's coordinates are not written.** Evidence § 3 measured the *banding* that
  page produces; the plan deliberately supplies no fixture body (plan rule 1), so the first
  implementer runs it and may find the geometry needs adjusting. The plan says: adjust the fixture,
  never the assertion.
- **DECISION B is open by construction** — whether `classify` always sets a reason on `NON_TABLE` is
  the plan's first measurement, not a claim it makes.
- **No task has been executed.** Every number in the plan is quoted from the spec or the evidence
  doc, both of which were measured at `ec1dc4e` / `a3ff34b`, not re-measured here.

## 4. What this loop did not touch

No `src/`, no `vocab/`, no tests, no register row. [[R166]], [[R211]], [[R212]], [[R218]], [[R219]]
and etkl:02 are where PR #212 left them. R212 closes in the loop that executes this plan, on the
corpus arm's output (plan Task 4 Step 3) — not before.
