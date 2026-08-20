# The arc has a denominator — implementation plan (strategy instrument, slice 1)

> **For agentic workers:** REQUIRED SUB-SKILL: `superpowers:subagent-driven-development` (recommended)
> or `superpowers:executing-plans`. Steps use checkbox (`- [ ]`) syntax.

**Goal:** give each of the arc's five named rungs a countable, membrane-checked denominator and a
dependency edge to the residue register, so the cockpit stops printing `stage ?/5` and starts
printing five fractions it can defend.

**Architecture:** ASSERT + MEMBRANE, in two layers, following the `cor:` precedent exactly. A
hand-authored Turtle manifest (`tests/arc-manifest.ttl`) asserts the position; a SHACL shapes file
(`tests/arc-shapes.ttl`) refuses graph-internal dishonesty; a pytest oracle
(`tests/test_arc_manifest.py`) refuses the dishonesty SHACL cannot see (does the artifact exist? does
the oracle test collect? was this validated under the right interpreter? is that residue row real?).
Four SPARQL derivations read the manifest for selection. `scripts/cockpit.py` reads the manifest with
a regex — never rdflib — and an agreement test pins its reading equal to rdflib's.

**Tech Stack:** RDF Turtle, pySHACL (`inference="rdfs"`, `advanced=True`), rdflib 7.6.0, pytest,
Python 3.12. Runner is **`./.venv/bin/python`** — never `python3`.

**Spec:** `docs/superpowers/specs/2026-08-20-the-arc-has-a-denominator-design.md` (584 lines).
Executors read it in full before Task 1; this plan argues from it and does not restate it.

**Evidence this plan cites and does not re-measure:**
- `docs/superpowers/2026-08-20-escalation-reason-census.md` — the 315.3 s corpus run. **Do not re-run it.**
- `docs/superpowers/2026-08-20-census-done-plan-next-handoff.md` — what that run left open.

**Doc impact: none.** Every file this plan touches is Evidence class (`docs/superpowers/**`), Manual
class (none touched), or untracked-by-governance code/tests. `docs/narrative/scope-evolution.md`'s
Assertion-class increment already shipped at `3b36609`. No `mkdocs.yml` nav change, no wiki page.

---

## Global Constraints

Every task's requirements implicitly include this section.

1. **Runner:** `./.venv/bin/python -m pytest`. **Never `python3`** — it carries rdflib 7.1.4, lacks
   `pyrudof`, and reports false reds on every corpus test (spec §7.2.2; the spec's own author wrote a
   defect report for a nonexistent defect before catching it).
2. **Neurosymbolic gate (CLAUDE.md §8), classified per artifact:**
   - `tests/arc-shapes.ttl` → **AXIOM / constraint**, closed world. The membrane. It never derives.
   - `vocab/queries/arc-*.rq` → **AXIOM / derivation**, open world, evidence-positive. `NOT EXISTS` is
     permitted only query-locally (holon-scoped closure).
   - `tests/test_arc_manifest.py` → **PROCEDURAL**, and it must say why in its module docstring:
     the three checks it owns (filesystem existence, pytest collectability, interpreter identity)
     are facts about the *environment*, not about the graph, and no SHACL engine can see them.
     Precedent: `tests/test_corpus.py`.
   - `scripts/cockpit.py` → **PROCEDURAL** reporting harness, already justified in its own docstring.
   - **No NEURAL work in this loop.**
3. **No tuned constants.** A threshold that decides anything is a review failure. Colour thresholds
   that colour a number the reader still reads are permitted (existing precedent, `cockpit.py`).
4. **No auto-writing of the manifest.** Code validates the hand-authored graph and never writes it
   (spec §9; `cor:` precedent, `docs/wiki/concepts/corpus-harness.md:89-93`). A test that expects a
   criterion to flip itself to met asserts behaviour the spec forbids.
5. **`prog:` is repo-internal and unpublished**, exactly as `dg:` and `cor:` are. It never appears in
   `vocab/ontology/`, is never w3id-registered, and no HGA term appears anywhere in it.
6. **A criterion may not be authored without its met-value measured.** Authoring a row from prose
   alone puts a fabricated numerator on the strip.
7. **Never lower a bar to meet it.** Do not pin a `cor:scoreFloor` at a document's currently-measured
   score to move a fraction (spec §7.1, §8; `[[no-overfitting-general-fixes]]`).
8. **FALSIFICATION IS MANDATORY, per task** (CLAUDE.md § Plan authoring rule 4). Every task report
   carries a `## FALSIFICATION` block: remove or invert the thing the new test pins, show the test
   **failing**, restore, show the suite green. No falsification evidence ⇒ the task review fails.
9. **No test bodies are supplied in this plan** (CLAUDE.md § Plan authoring rule 1). Each step states
   the test's *name*, the assertion it must make, and what must falsify it. Writing the body — and
   falsifying it — is the implementer's work, and is the whole reason a plan defect is catchable.
   **If a stated assertion cannot be written against the code as it stands, that is a plan defect:
   say so in the task report and substitute the satisfiable form carrying the same force. Never
   weaken the assertion to make a broken contract go green.**

---

## Decisions this plan makes, and where they are recorded

**These four are recorded NOWHERE but this file — they are reversible, not settled.** The spec left
each of them to the plan; each is answered here with its reason, so the maintainer can overturn any
of them without reopening the spec.

### D1 — a corpus-dead escalation reason is NOT met by being dead

This is the handoff's *"plan's first decision"* and it sets the `tab` denominator and every row under
it.

The census measured four of nine reasons firing **nowhere** on the corpus (`MERGE_AMBIGUOUS`,
`MULTI_TABLE_AMBIGUOUS`, `ROW_GROUP_AMBIGUOUS`, `TRANSPOSED`). Spec §7.4's two-armed wording
(*"does not fire, **or** every occurrence adjudicated"*) would read all four as **met** — putting 4 of
10 `tab` criteria in the numerator for a reason that measures **the corpus, not the reading**. That is
a §8-class gameability defect of the same family as the `etkl` floor defect fixed at `820ab24`.

**Decided: both arms require a disposition, and silence alone is never one.** The criterion becomes:

> **For each escalation reason, the reason is *disposed*:**
> **(a) it fires on the corpus** ⇒ every firing document carries a dated `cor:adjudication` naming
> that reason and disposing of it; **or**
> **(b) it fires nowhere on the corpus** ⇒ it names a **collectable `prog:oracleTest`** that
> exercises the path, plus a recorded reason distinguishing **corpus gap** from **dead path**.

Arm (b) is the `VACUITY_REGISTRY` form, which is the precedent already in this repo
(`tests/etkl/test_vacuity_registry.py:87`: *a shape idle by either criterion must appear here with a
measured reason*). It is falsifiable rather than prose: **a reason with no fixture that exercises it
is dead code, and its criterion is unmet with a residue** — which is a finding worth having.

**And M8 is the structural guard that stops either arm being bought with a paragraph.** A criterion
carrying `prog:blockedBy` on an **open** residue cannot be `prog:met true`. Every firing reason is
blocked by an open row today (spec §7.4's table: R43/R44/R45/R62/R71/R74/R77/R79/R80/R83/R84), so
writing six adjudications in Task 5 **cannot** flip five reason criteria to met. **Expect `tab` to
land at 1/10 or 2/10, and that is the honest number.** If it lands higher, a reviewer must ask which
open row went missing.

### D2 — the manifest counts the **graph side** (24), and says so

The census found graph-side 24 vs report-side 29, reconciling exactly on apple page 1's five
escalations **withdrawn** when the data grid supersedes them (`document.py:1512-1513`), whose
`RegionReport` keeps its original reason (`compile.py:1132-1136` rewrites only `verdict` and
`tokens_escalated`).

**Decided: graph-side.** A superseded refusal is not an outstanding refusal to adjudicate — the
compiler went on to read the region. A SHACL membrane over the compiled graph can see only the
graph-side 24 anyway, so counting report-side would make the manifest assert something its own
membrane class cannot check. **The manifest records the number 24, the side, and the reconciliation**
(`11 escalated + 5 superseded = 16 reason-bearing reports on apple; the graph keeps 11`) so a future
re-measurement reading 29 recognises a known difference rather than drift.

### D3 — liveness is **not** a `dec` criterion; it is `tab`'s tenth, widened beyond `tab:`

Spec §7.2 asks the plan to name what R99 and R100 block: a `dec` criterion, or a residue edge only.

**Decided: neither `dec` criterion nor edge-only — they block `tab`'s tenth criterion, and that
criterion is widened from "every wired `tab:` shape" to "every shape wired into the compile
membrane".** Reasons, in order of weight:

1. `dec`'s denominator is **read from prose that predates it** (`CLAUDE.md:252` and `:249-251`) — that
   is what makes four of five rungs `retrospective false`, and it is the property §7 says the work
   must preserve (*lifting prose into countable form, not inventing criteria*). A liveness criterion
   on `dec` would be this loop **inventing** one.
2. `VACUITY_REGISTRY` is **one artifact spanning four namespaces** — measured: 9 rows, of which 5 are
   `tab:`, 2 `iladub:`, 1 `dec:`, 1 `iladub:`/`dec:` mixed (`tests/etkl/test_vacuity_registry.py:87-127`).
   Splitting it across two rungs gives two criteria that can disagree about the same registry.
3. The criterion is about **the compile membrane's honesty** — the instrument that measures the
   reading — which is `tab`'s subject matter.

So R99 (`iladub:NoLeakShape`) and R100 (`dec:EscalationShape`) join R97 and R98 on `tab`'s criterion
10, and **`dec` stays at 16 criteria: 15 shape-pairing + 1 provenance.**

### D4 — the strip goes to two lines, and the `▸` slot does NOT name a frontier residue

**Two lines: MEASURED and decided.** Claude Code's `statusLine` documentation states multi-line is
supported (*"Multiple lines: each `echo` or `print` statement displays as a separate row"*, with a
worked two-line example), while character limits and wrap-vs-truncate are **undocumented**, and
multi-line combined with ANSI escapes is flagged as more prone to rendering glitches than single-line.
Measured via the `claude-code-guide` agent against
`https://code.claude.com/docs/en/statusline.md`, 2026-08-20. Line 1 keeps the existing strip; line 2
is the arc. `tests/test_cockpit.py::test_it_exits_zero_and_prints_one_line_with_stdin_attached`
becomes a **two**-line assertion — a deliberate change with its reason in the docstring, not a silent
relaxation (spec §6). The fallback if the harness turns out to truncate in practice is the compact
form (bars without fractions) on **one** line, with fractions behind `--verbose`; the fallback must
**not** abbreviate the rung names (decision 8).

**The `▸` slot: the spec says it should name the residue `arc-frontier.rq` names. This plan declines,
and this is the deviation most worth overturning.** `arc-frontier.rq` returns many rows; picking one
for a one-character slot requires a **ranking**, and a ranking inside `cockpit.py` is a tuned constant
by another name — the exact defect `tests/test_cockpit.py::test_no_stuck_verdict_is_computed_anywhere`
exists to pin. Instead the arc line ends with two **counts**, and the selection stays in the queries a
session runs deliberately:

- `frontier N` — open residues blocking at least one unmet criterion.
- `ready N` — unmet criteria whose every `prog:blockedBy` row is now **closed**. This is *"work that
  is ready and is not being done"*, which spec §5 calls the query the maintainer's complaint most
  directly asks for.

The `▸` slot keeps the newest-handoff filename it has today.

---

## Corrections this plan carries into the manifest

Measured, each with its source. **Do not copy the spec's superseded figures.**

| the spec says | measured, and what to write |
| --- | --- |
| §7.4: **eight** escalation reasons; `TRANSPOSED` is a kind | **NINE.** `TRANSPOSED` is a reason (`compile.py:688` passes it to `escalate_region`); `RegionKind` (`regions.py:27-30`) has exactly three members, none of them `TRANSPOSED`. **`tab`'s denominator is 10** = 9 reasons + criterion 10. (census § *Seam 2*) |
| §6: `tab` renders **`?`**, numerator unmeasured | `tab`'s numerator is **measured** and renders a number. `?` now belongs only to a rung with zero criteria. (census § *Seam 1*) |
| §7.4: the criterion is *does not fire **or** adjudicated* | **D1** above. Silence alone is never met. |
| §7.4: R74's closure names `test_cbh_p0_known_defects_are_pinned_not_hidden` | **No such function.** The real pin is `tests/etkl/test_datagrid.py::test_cbh_p0_table_b_leak_is_pinned_not_hidden` — **verified collectable 2026-08-20** (`./.venv/bin/python -m pytest --collect-only -q`, 1252 tests, 0 errors; the id appears verbatim). Task 2 corrects the register row. |
| §7.4 / R43, R44, R45 cite `battery-run-final.log` as their measurement evidence | **Absent from the repo and from git history** (`git log --all -- '*battery-run-final*'` → empty). **No `prog:oracleArtifact` may point at it.** This is M5's real-world case. |
| §11 seam 4: *"confirm every `prog:oracleTest` resolves"* | **The suite collects clean under the venv runner:** `./.venv/bin/python -m pytest --collect-only -q` → `1252 tests collected in 2.61s`, **0 errors, 0 collection-time skips**, measured 2026-08-20. `tests/etkl/test_membrane_equiv.py` collects 31 node ids (it does **not** skip). Per-criterion ids are still each implementer's to verify against this list. |

| §11 seam 6: *"re-measure the residue→residue backfill set; this spec's pattern found 7 rows, the handoff's found 6"* | **7 confirmed, and the spec's list is exactly right** — `residues-open.md:18` R14, `:46` R51, `:73` R89, `:76` R96; `residues-closed.md:11` R4, `:26` R102, `:28` R87 (re-run 2026-08-20 with the spec's own command). **Refinement worth carrying: only 5 are real residue→residue *edges*** — R51 and R4 mention no other row, so they are prose about themselves. The edges are R14→R10, R89→R102, R96→R95, R102→{R34,R89,R99}, R87→R88. **This backfill is NOT this loop's work** (spec §3.3: the load-bearing edge is residue→criterion); the seam is discharged, not actioned. |
| §11 seam 3: `prog:declaredOn` per criterion | **Measured — see § `prog:declaredOn` below.** Every date the spec asserted is confirmed, including its two proof cases: `holon`'s four built bullets have `metOn == declaredOn` (so M4 genuinely bites), and `graincorp-stem` has `declaredOn` 2026-08-02 **<** `metOn` 2026-08-03. |

**The reason list is a copy of a grep and can drift** — there is no enum and no registry, deliberately
(`_suggester_uri`, `holon.py:409-421`, slugifies the string rather than looking it up, its docstring
giving the reason). **Task 6 re-runs the grep and carries its output inline**; if the grep and the
census disagree, the census is wrong and the grep wins.


---

## `prog:declaredOn` — MEASURED, per criterion group (spec §11 seam 3)

Measured 2026-08-20 by `git blame -L <line>,<line> --date=short -- <path>` cross-checked against
`git log -L <range>:<path> --date=short` walked to the **oldest** commit in each range's history
(and by `git log -S"<iri>"` pickaxe for the manifest entries, which agrees with blame on every
subject line). **Introduction date, not last-touch.** The implementer re-verifies each before
writing it and states the command; where a re-run disagrees, **the re-run wins.**

| criteria | declaring prose | introduced | `retrospective` |
| --- | --- | --- | --- |
| `dec:01–15` (shape pairing) | `CLAUDE.md:252` — *"Every vocabulary/shape ships with a worked example that conforms **and** a negative test that must fail"* | **2026-05-31**, `ee221de` (the commit that created `CLAUDE.md`) — **only one commit in its history, never touched since** | **false** for all fifteen |
| `dec:16` (provenance reuse) | `CLAUDE.md:249-251` | **2026-05-31**, `ee221de` — introduced as `hol:DecisionHolon ⊑ prov:Activity` and only **renamed** `hol:`→`dec:` at `84110a2` 2026-07-01. Lines 250-251 untouched since. **The rule's introduction is the declaration; the rename is not** | **false** |
| `holon:01–04` (*What is built*) | `docs/holonic-interaction.md:147-156` | **2026-06-23**, `781527f` (*feat(holons): align iladub to W3C Holon CG / HGA + grounding governance*) — last touched `d0b3e55` 2026-07-01, an `iladub:`→`etkl:` namespace rename only | **true** — and the measurement is *why*: the bullets and the artifacts they describe landed in the **same commit**, so `metOn == declaredOn` and **M4 refuses `retrospective false`**. The clause fires on real data, not a fixture |
| `holon:05–06` (*Planned work*) | `docs/holonic-interaction.md:160-163` | **2026-06-23**, `781527f`, in their current form. An **ancestor** sentence (*"A membrane-health check that reports a compiled document's cleanliness."*) existed at `0597988` **2026-06-02**; the section heading is from the file's creation but **its content was fully replaced** at `781527f` | **false** |
| `substrate:01–03` | `docs/narrative/scope-evolution.md:99-101` | **2026-07-03**, `20c3be4` (the file-creating commit; the sentence is verbatim in that version). The heading at `:97` was **reworded** at `3b36609` 2026-08-20, the content was not | **false** |
| `etkl:01` (graincorp-stem) | `tests/corpus-manifest.ttl:24` | entry **2026-08-02**, `a22733e`; `cor:expectedVerdict cor:CompilesAbove` + `cor:scoreFloor` **2026-08-03**, `8fd217a1` | **false** — `declaredOn` 2026-08-02 **<** `metOn` 2026-08-03. **The spec's proof case is confirmed by measurement**: the denominator moved before the numerator, and it moved *through* a recorded HOLD |
| `etkl:02–07` | `tests/corpus-manifest.ttl:44,55,69,84,95,106` | **2026-08-04** — `e121c42` (graincorp-capacity, cbh-stem), `2855b52` (ons, bfs), `06c6b39` (apple), `cab08ec` (who-wfa) | **false** |
| `tab:01–10` | this loop constructs them (spec §7.4: the one rung that had to be built) | **the date this loop declares them** | **false** |

**⚠ `substrate`'s three requirements are ONE SENTENCE spanning lines 99-101, not three lines.** All
three criteria carry the same `prog:source` and the same `prog:declaredOn`. Do not fabricate three
distinct declaring lines to make them look independent.

---

## File structure

| file | status | responsibility |
| --- | --- | --- |
| `tests/arc-manifest.ttl` | **create** | the asserted state: 5 rungs, 42 criteria, their oracles and blocking edges, and the validated-runner record |
| `tests/arc-shapes.ttl` | **create** | the SHACL membrane — M1, M2, M3, M4, M6, M8, M9 (the graph-internal refusals) |
| `tests/test_arc_manifest.py` | **create** | runs the membrane; owns M5 and M7 (the refusals needing the filesystem); owns the negative fixtures |
| `tests/arc-*-leak.ttl` | **create** | one negative fixture per refusal — each must fail, per CLAUDE.md § Serialization |
| `vocab/queries/arc-position.rq` | **create** | per rung, `(met, declared)` |
| `vocab/queries/arc-frontier.rq` | **create** | open residues blocking an unmet criterion, with rung + criterion |
| `vocab/queries/arc-unblocked.rq` | **create** | unmet criteria whose every blocker is closed |
| `vocab/queries/arc-orphan.rq` | **create** | open residues blocking no criterion of any rung |
| `tests/test_arc_queries.py` | **create** | the four derivations, each against a fixture graph with a known answer |
| `scripts/cockpit.py` | **modify** | `arc()` reads the manifest by regex; `render()` gains line 2 |
| `tests/test_cockpit.py` | **modify** | one-line → two-line; the honesty test preserved in substance; the agreement test added |
| `tests/corpus-manifest.ttl` | **modify** | six `cor:adjudication` HOLD nodes |
| `docs/superpowers/residues.md` | **modify** | the two tally repairs |
| `docs/superpowers/residues-open.md` | **modify** | R74's broken pointer |

**Branch:** `git checkout -b arc-denominator` from `main` @ `2922c1f` before Task 1.

---

## The `prog:` interface — defined once, consumed by every task

`prog:` = `https://w3id.org/iladub/progress#`.

**`prog:Rung`** — `rdfs:label`, `prog:rungKey` (exactly one of `"etkl" "dec" "holon" "tab" "substrate"`),
`prog:criterion` (0..n). **No ordering property exists.** No `prog:precedes`, no index (spec §9,
decision 8).

**`prog:Criterion`** — an **IRI**, never a blank node, of the form
`urn:iladub:arc:crit:{rungKey}:{nn}`. Carries exactly one each of `prog:statement` (prose),
`prog:ofRung` (the key literal, redundant with the IRI **on purpose** — see M9), `prog:declaredOn`
(`xsd:date`), `prog:met` (`xsd:boolean`), `prog:retrospective` (`xsd:boolean`); one `prog:metOn`
(`xsd:date`) iff `prog:met true`; one `prog:oracle`; zero or more `prog:blockedBy` (a residue row id
literal, `"R43"`); and exactly one `prog:source` (`"file:line"` — where the prose that declares this
criterion lives, which is what makes `prog:declaredOn` auditable).

**`prog:Oracle`** — `prog:oracleArtifact` (repo-relative path, 0..n) and `prog:oracleTest`
(`path::function[param]`, 0..n). An **unmet** criterion may name a *target* oracle that does not exist
yet; a **met** one may not.

**`prog:Manifest`** — one node, `<urn:iladub:arc:manifest>`, carrying `prog:validatedWith` → a node
with `prog:interpreter`, `prog:pythonVersion`, `prog:rdflibVersion`. This is M5's third arm.

### The refusals

| # | refusal | layer |
| --- | --- | --- |
| M1 | a `prog:Criterion` without exactly one each of `prog:declaredOn`, `prog:statement`, `prog:met`, `prog:retrospective`, `prog:ofRung`, `prog:source` | SHACL |
| M2 | `prog:met true` without `prog:metOn` — and `prog:metOn` present while `prog:met false` | SHACL (`sh:sparql`) |
| M3 | `prog:metOn` earlier than `prog:declaredOn` | SHACL (`sh:sparql`) |
| M4 | `prog:metOn` **equal to** `prog:declaredOn` while `prog:retrospective false` | SHACL (`sh:sparql`) |
| M5 | `prog:met true` whose `prog:oracleArtifact` is not on disk, or whose `prog:oracleTest` is not collectable, or whose manifest `prog:validatedWith` does not match the running interpreter | **pytest** |
| M6 | a `prog:Rung` whose `prog:rungKey` is not one of the five settled names | SHACL (`sh:in`) |
| M7 | `prog:blockedBy` naming a residue row absent from `docs/superpowers/residues.md` | **pytest** |
| M8 | `prog:blockedBy` on a criterion that is `prog:met true` | SHACL (`sh:sparql`) |
| **M9** | a `prog:Criterion` that is a blank node, or whose IRI does not match `^urn:iladub:arc:crit:(etkl\|dec\|holon\|tab\|substrate):[0-9]+$`, or whose `prog:ofRung` disagrees with its IRI | SHACL |

**M9 is this plan's addition to the spec, and it is load-bearing, not tidiness.** Spec §6 requires
`cockpit.py` to read the manifest **without rdflib** (the performance contract, `cockpit.py:34-38`).
A regex read of arbitrary Turtle is not safe; a regex read of a file where *every criterion is a
top-level IRI subject encoding its own rung* is. M9 is what buys §6's fast reader its safety, and the
agreement test (Task 8) is what proves the two readers agree.

**A rung with zero criteria is NOT a refusal.** It renders `?`. Unknown ≠ zero (decision 6).

### Two facts about layering that a reviewer should check first

- **M5 and M7 cannot be SHACL.** They ask about the filesystem, about pytest collection, and about
  `sys.version` — none of which is in the graph. Putting them in `arc-shapes.ttl` is impossible, not
  merely inelegant, and the precedent is `tests/corpus-shapes.ttl` + `tests/test_corpus.py` (the
  shape guards the register's integrity; the pytest oracle guards everything about the world).
- **Nothing here derives.** The membrane validates what was asserted; the four `.rq` files derive.
  Never use SHACL to compute a fraction (CLAUDE.md §8).

---

## Task 1: the membrane and the vocabulary

**Files:**
- Create: `tests/arc-shapes.ttl`
- Create: `tests/test_arc_manifest.py`
- Create: `tests/arc-manifest.ttl` — **seed only** in this task: the five `prog:Rung` nodes with
  **zero** criteria, plus the `prog:Manifest` node. Every rung reads `?`.
- Create: one negative fixture per refusal, named `tests/arc-<refusal>-leak.ttl`

**Interfaces:**
- **Produces:** `tests/arc-shapes.ttl` (the seven SHACL refusals M1–M4, M6, M8, M9); and in
  `tests/test_arc_manifest.py`: `validate_manifest(data_path, shapes_path) -> (conforms, report_text)`
  wrapping pySHACL with `inference="rdfs"`, `advanced=True`; `oracle_rows(graph)` yielding
  `(criterion_iri, met, artifacts, tests)`; `blocked_rows(graph)` yielding `(criterion_iri, residue_id)`.
- **Consumes:** nothing.

- [ ] **Step 1: read the primaries.** The spec in full; then `tests/corpus-shapes.ttl` (56 lines) and
      `tests/test_corpus.py:1-120` — the pattern this task copies. Note how `cor:prefixes sh:declare`
      is set up; `sh:sparql` constraints need it.

- [ ] **Step 2: write the failing membrane tests, one per refusal.** Seven SHACL refusals and two
      pytest refusals, each as its own test with its own `arc-*-leak.ttl` fixture. For each, the test
      asserts **non-conformance** and that the report names the right constraint. The names and what
      each must pin:

      | test | the fixture is a manifest where… | must be refused because |
      | --- | --- | --- |
      | `test_m1_a_criterion_without_its_required_fields_is_refused` | a criterion omits `prog:declaredOn` | a criterion with no declaration date cannot participate in §3.2 at all |
      | `test_m2_a_met_criterion_without_a_date_is_refused` | `prog:met true`, no `prog:metOn` | a claim with no date is not auditable |
      | `test_m2b_an_unmet_criterion_carrying_a_met_date_is_refused` | `prog:met false` **with** `prog:metOn` | the inverse leak: a date left behind when a criterion was un-met |
      | `test_m3_met_before_declared_is_refused` | `prog:metOn` < `prog:declaredOn` | met before it was defined |
      | `test_m4_same_day_grandfathering_must_be_labelled` | `metOn` == `declaredOn`, `retrospective false` | §3.2 — grandfathering is labelled, never hidden |
      | `test_m6_a_sixth_rung_is_refused` | `prog:rungKey "governance"` | a sixth rung is a decision, not an edit |
      | `test_m8_a_met_criterion_may_not_be_blocked` | `prog:met true` + `prog:blockedBy "R43"` | a met criterion is not blocked; this catches the stalest kind of row |
      | `test_m9_a_blank_node_criterion_is_refused` | a criterion authored as `[ ... ]` | §6's rdflib-free reader cannot see it |
      | `test_m9b_an_iri_that_disagrees_with_its_rung_is_refused` | IRI says `:tab:`, `prog:ofRung "dec"` | the two encodings must agree or the fast reader and rdflib disagree |
      | `test_m5_a_met_criterion_pointing_at_an_absent_artifact_is_refused` | met, `prog:oracleArtifact "battery-run-final.log"` | **use that literal string** — it is cited by three live register rows and is absent from the repo and from git history |
      | `test_m5b_a_met_criterion_whose_oracle_test_does_not_collect_is_refused` | met, `prog:oracleTest "tests/etkl/test_datagrid.py::test_cbh_p0_known_defects_are_pinned_not_hidden"` | **use that literal id** — it is R74's real broken pointer |
      | `test_m5c_a_manifest_validated_under_another_interpreter_is_refused` | `prog:rdflibVersion "7.1.4"` | spec §7.2.2: green is relative to a runner, and a gauge inheriting that would silently un-meet criteria for an environment reason |
      | `test_m7_a_blocking_edge_to_a_nonexistent_residue_is_refused` | `prog:blockedBy "R999"` | a dangling edge is worse than no edge |
      | `test_a_rung_with_no_criteria_conforms_and_is_not_a_refusal` | a rung with zero criteria | **positive** — unknown ≠ zero (decision 6). This is the one test in the file that asserts conformance |

      **MEASURE before writing M5b:** run `./.venv/bin/python -m pytest --collect-only -q` once and
      decide how the collectability check is implemented — a subprocess call per node id would be
      unusably slow at 42 criteria. Collect **once** into a set and check membership. State the
      measured collection time in the test's docstring.

- [ ] **Step 3: run them; they must all fail.** `./.venv/bin/python -m pytest tests/test_arc_manifest.py -v`
      Expected: every test fails, on a missing `tests/arc-shapes.ttl` or a missing helper.

- [ ] **Step 4: write `tests/arc-shapes.ttl` and the pytest oracle** until every test passes.
      **Constraint:** the shapes file derives nothing and computes no fraction. **`prog:` terms only
      — no `holon:` IRI appears anywhere** (CLAUDE.md § Source ownership; `tests/test_source_ownership.py`
      enforces it and will run on this file).

- [ ] **Step 5: write the seed manifest** — five rungs, zero criteria, the `prog:Manifest` node with
      the **measured** interpreter facts. Measure them, do not copy this plan's:
      `./.venv/bin/python -c "import sys,rdflib;print(sys.executable, sys.version.split()[0], rdflib.__version__)"`

- [ ] **Step 6: run the full suite.** `./.venv/bin/python -m pytest -x -q`
      Expected: green, and the collected count has grown from the measured 1252 baseline.

- [ ] **Step 7: `## FALSIFICATION`** — delete `tests/arc-shapes.ttl`'s M9 node-shape clause, show
      `test_m9_*` failing, restore, show green. **Do this for at least M9, M5c and M8**, the three
      whose subjects are most easily deleted without another test noticing.

- [ ] **Step 8: commit.** `feat(arc): the membrane before the manifest — nine refusals and a seed`

---

## Task 2: the register repairs, and R74's broken pointer

Done **before** any criterion is authored, because M7 reads `residues.md` and Task 6 points an oracle
at R74's real test.

**Files:** Modify `docs/superpowers/residues.md`; modify `docs/superpowers/residues-open.md`.

**Interfaces:** Produces nothing consumed programmatically; M7 (Task 1) reads the index it repairs.

- [ ] **Step 1: re-measure both figures and paste the commands inline into the commit message.**
      ```
      awk -F'|' '/^\| R[0-9]/ {print $3}' docs/superpowers/residues.md | sort | uniq -c
      grep -cE '^\| ~?~?R[0-9]+' docs/superpowers/residues-open.md docs/superpowers/residues-closed.md
      ```
      **Measured 2026-08-20, twice, independently: 73 open + 21 closed = 94, and the index and the
      two detail files agree exactly** (`residues-open.md` 73, `residues-closed.md` 21). **If your run
      disagrees, your run wins** — report the difference rather than writing the expected number.

- [ ] **Step 2: repair `residues.md:40`** — it says *"94 rows, 20 closed"*. Write the measured figure
      **and the command that produced it**, so the next reader can re-run rather than re-count.

- [ ] **Step 3: repair the convention example at `residues.md:25`** — it writes `R97 (17/87 closed)`
      while the row it quotes (`residues-open.md:77`) reads `(18/87 closed)`. **Verify the row's
      current text before editing**; the example is quoted from a real row and must match it.

- [ ] **Step 4: repair R74's closure pointer in `residues-open.md`.** It names
      `test_cbh_p0_known_defects_are_pinned_not_hidden`, which does not exist. The real pin is
      `tests/etkl/test_datagrid.py::test_cbh_p0_table_b_leak_is_pinned_not_hidden`. **Verify it
      collects before writing it** (`./.venv/bin/python -m pytest --collect-only -q | grep table_b_leak`),
      and record in the row that the old name was wrong, not merely that the new one is right.

- [ ] **Step 5: this closes nothing.** These are repairs. **Do not strike any row, do not touch any
      tally snapshot, do not change the closed count** (spec §9). A reviewer who sees a struck number
      in this commit should reject it.

- [ ] **Step 6: run** `./.venv/bin/python -m pytest tests/test_doc_governance.py -q` — the register is
      Evidence class and lint-enforced.

- [ ] **Step 7: `## FALSIFICATION`** — no new test ships here, so the falsification is the
      measurement: paste both commands' raw output, before and after, in the task report.

- [ ] **Step 8: commit.** `fix(register): the tally, its own example, and a pointer to a test that never existed`

---

## Task 3: the `etkl`, `holon` and `substrate` rungs

Three rungs whose criteria are **read from prose that already exists**. 16 criteria total.

**Files:** Modify `tests/arc-manifest.ttl`.

**Interfaces:**
- **Consumes:** Task 1's `prog:` shapes and `validate_manifest`.
- **Produces:** criteria `urn:iladub:arc:crit:etkl:01..07`, `…:holon:01..06`, `…:substrate:01..03`.

- [ ] **Step 1: re-verify the measured `prog:declaredOn` dates in § `prog:declaredOn` — MEASURED
      above.** They are already measured; your job is to confirm, not to discover. Per criterion:
      ```
      git blame -L <line>,<line> --date=short -- <path>
      git log -L <line>,<line>:<path> --date=short --format='%h %ad %s' | tail -5
      ```
      **The date is the commit date of the line of prose that declares the criterion** — not the
      file's creation date, not the last touch, and not today. Two measured traps: `holonic-interaction.md`
      was created 2026-06-02 but its *"What is built"* content was **fully replaced** at `781527f`
      2026-06-23; and `scope-evolution.md:97`'s heading was reworded at `3b36609` 2026-08-20 while the
      sentence declaring `substrate`'s three requirements dates to 2026-07-03. **Record each confirmed
      date and its command in the task report**, and put the declaring line in `prog:source`.

- [ ] **Step 2: author the `etkl` rung — 7 criteria, one per `cor:Document`.** The statement, verbatim
      from spec §7.1 as corrected at `820ab24`:

      > *this document compiles via `compile_document` to `cor:CompilesAbove` with a pinned
      > `cor:scoreFloor`, under a `cor:adjudication` whose rationale **accepts** that score — not one
      > that holds it.*

      **Met today: exactly one** — `graincorp-stem-2026-07-31` (floor 0.95, achieved 0.9655). It is
      **`retrospective false`**, and this is now measured rather than asserted: the entry landed
      **2026-08-02** (`a22733e`) and its `cor:expectedVerdict cor:CompilesAbove` + `cor:scoreFloor`
      landed **2026-08-03** (`8fd217a1`), so `declaredOn` **<** `metOn` on separate commits.
      It is the model's proof case. **The other six were declared 2026-08-04** — `e121c42`
      (graincorp-capacity, cbh-stem), `2855b52` (ons, bfs), `06c6b39` (apple), `cab08ec` (who-wfa).
      **The other six are `met false`.** Oracle for each: the corresponding
      `tests/test_corpus.py::test_expected_verdict[<file>]` node id — **all seven verified collectable
      2026-08-20** (see § Corrections). Artifact: `tests/corpus-manifest.ttl`.

- [ ] **Step 3: author the `holon` rung — 6 criteria**, from `docs/holonic-interaction.md`
      § *What is built* (4 bullets) and § *Planned work (not done yet)* (2 bullets). Verify the line
      numbers with `grep -n -e "What is built" -e "Planned work" docs/holonic-interaction.md` — the
      spec's `:145-156` / `:158-163` are a measurement from 2026-08-20 and may have moved.
      **All six carry `prog:declaredOn "2026-06-23"`** (`781527f`) — measured, see the table above.
      The four met are **`retrospective true`**, and the measurement is why rather than a convention:
      the bullets and the artifacts they describe landed in the **same commit**, so
      `metOn == declaredOn` and **M4 refuses `retrospective false` outright**. The two unmet — the
      `etkl:membraneHealth` check, and the full raw→clean traversal example — are
      **`retrospective false`**, so flipping either is a real measurement.
      Oracles for criteria 3 and 4: `tests/test_hga_alignment.py::test_governed_grounding_conformant`
      and `::test_ungoverned_grounding_rejected` (**both verified collectable**). Criteria 1 and 2 name
      their `.ttl` artifacts; **check whether a test asserts each is standalone** — `::test_holons_module_standalone`
      and `::test_dec_module_standalone` exist — and name it if it does.
      The two unmet criteria name **target** oracles that do not exist yet. That is permitted (spec §3);
      M5 bites only on `met true`.

- [ ] **Step 4: author the `substrate` rung — 3 criteria**, from `docs/narrative/scope-evolution.md`
      § `substrate`: the immutable **event ledger** (memory), **validation-at-write** (sensory), and
      **in-engine policy** (motor). All three `retrospective false`, all three `met false`.
      **RE-MEASURE before writing `met false` — an unmet criterion is still an assertion.** The
      handoff measured 34 LOC in `src/iladub/fluree/` (two JSON-LD policy templates) + `writegate.py`
      (70 LOC), **zero** server/runtime code, **zero** event-ledger implementation, and `membrane.py`
      running inside the compiler process rather than at a write endpoint. Confirm each, and state the
      command. **This is the only honest `0` on the strip and it must stay earned.**
      **All three carry `prog:declaredOn "2026-07-03"` (`20c3be4`) and the SAME `prog:source`,
      `docs/narrative/scope-evolution.md:99-101`** — the three requirements are one sentence, not
      three lines (measured). Do not fabricate three distinct declaring lines to make them look
      independently declared.

- [ ] **Step 5: run the membrane.** `./.venv/bin/python -m pytest tests/test_arc_manifest.py -q`
      Expected: green. If M4 fires, a date is wrong or a `retrospective` flag is missing — **fix the
      flag or the date, never the shape.**

- [ ] **Step 6: `## FALSIFICATION`** — flip `graincorp-stem`'s criterion to `prog:retrospective true`
      while leaving its dates, confirm nothing fails (M4 only bites on same-day), then set its
      `prog:metOn` back to `prog:declaredOn` and confirm **M4 now fires**. Restore. This proves M4 is
      pinning the grandfathering clause and not merely present.

- [ ] **Step 7: commit.** `feat(arc): three rungs whose denominators were already written down`

---

## Task 4: the `dec` rung — 16 criteria

**Files:** Modify `tests/arc-manifest.ttl`.

**Interfaces:** Consumes Task 1 and Task 3's manifest. Produces `urn:iladub:arc:crit:dec:01..16`.

- [ ] **Step 1: MEASURE the shape inventory before authoring anything.** The spec measured **15 shapes
      across `dec:` / `risk:` / `iladub:` / `gsh:`, of which 10 carry both halves and 5 are
      positive-only**. Re-derive the list and state the command. The five positive-only, per the spec:
      `dec:ConfidenceShape` (`dec-shapes.ttl:38`), `risk:RiskAssessmentShape` (`risk-shapes.ttl:35`),
      `risk:SensitivityShape` (`:49`), `gsh:PermissionShape` (`governance-shapes.ttl:45`),
      `iladub:PromotionDecisionShape` (`iladub-shapes.ttl:53`). **Verify each line number on disk** —
      spec §7.2.1 documents two load-bearing citations from the previous handoff that were both wrong
      by one line or by a whole directory, which is why M5 exists.

- [ ] **Step 2: author criteria 01–15, one per shape.** Statement, quoted from `CLAUDE.md:252`:
      *"Every vocabulary/shape ships with a worked example that conforms **and** a negative test that
      must fail."* `prog:declaredOn` is **2026-05-31** (`ee221de`) — the same date for all fifteen,
      because one Contract line declares them all, and that line has **exactly one commit in its
      history and has never been touched since**. Re-confirm once with
      `git log -L 252,252:CLAUDE.md --date=short --format='%h %ad %s'`.
      All fifteen are **`retrospective false`** (the rule predates every shape it governs — the
      strongest denominator in the repo, and nobody had counted it). Ten are `met true`, five
      `met false`. Each met criterion names **both** oracles: the conformance test and the negative
      test. A candidate negative-test list was collected 2026-08-20 (56 node ids matching
      `negative|leak|violat` collect clean) — **map each shape to its own negative test and verify the
      pairing; do not assume a `*-leak.ttl` fixture belongs to the shape whose name it resembles.**
      Each of the five unmet names a **target** oracle: *a negative fixture that trips this shape.*

- [ ] **Step 3: author criterion 16 — the provenance hole.** Statement, from `CLAUDE.md:249-251`:
      `dec:DecisionHolon ⊑ prov:Activity`, `dec:consideredEvidence ⊑ prov:used`,
      `dec:decidedBy ⊑ prov:wasAssociatedWith`, `dec:produced ⊑ prov:generated` — declared at
      `vocab/ontology/dec.ttl:38,55,72,85`, **asserted by no test**. Re-measure:
      `grep -rn "Activity" tests --include="*.py"` → the spec measured **0 hits**;
      `tests/test_hga_alignment.py:69-70` pins only `dec:partOf` and `dec:Event`.
      `met false`, `retrospective false`, `prog:declaredOn "2026-05-31"` — the rule was introduced at
      `ee221de` as `hol:DecisionHolon ⊑ prov:Activity` and only **renamed** `hol:`→`dec:` at `84110a2`
      2026-07-01. **The rule's introduction is the declaration; a namespace rename is not a
      re-declaration.** Target oracle: a test asserting all four subproperty axioms.

- [ ] **Step 4: author NO liveness criterion on this rung** — **D3**. R99 and R100 attach to `tab`'s
      criterion 10 in Task 6. If you believe D3 is wrong, say so in the task report and stop; do not
      add a sixteenth-and-a-half criterion to settle it yourself.

- [ ] **Step 5: run the membrane and check the fraction reads 10/16.** If it reads anything else, one
      of the pairings in step 2 is wrong — **re-measure the pairing; do not adjust the target.**

- [ ] **Step 6: `## FALSIFICATION`** — point criterion 16's `prog:oracleArtifact` at
      `vocab/ontology/dec.ttl` and flip it to `met true`; **M5 must NOT fire** (the file exists), which
      shows M5 alone cannot defend a false claim, and the `prog:oracleTest` arm is what does. Then add
      a `prog:oracleTest` naming a function that does not exist and show **M5b firing**. Restore.

- [ ] **Step 7: commit.** `feat(arc): dec reads 10/16, and the sixteenth is a hole in the Contract`

---

## Task 5: the corpus adjudication pass — six documents, six recorded HOLDs

**The deliverable is not a moved fraction. It is six documents moving from "nobody has looked" to
"measured, reasoned, held."** Expect `etkl` to stay at 1/7.

**Files:** Modify `tests/corpus-manifest.ttl`; modify `tests/test_corpus.py` **only** to add the
gameability falsifier (see step 5).

**Interfaces:** Consumes the census. Produces `cor:adjudication` nodes read by Task 6's arm (a).

- [ ] **Step 1: do NOT re-run the corpus.** The 315.3 s run is spent and its per-document,
      per-reason, per-page table is in `docs/superpowers/2026-08-20-escalation-reason-census.md`.
      Read it; cite it by section in each rationale.

- [ ] **Step 2: write six `cor:adjudication` nodes** — `cor:by`, `cor:on "2026-08-20"^^xsd:date`,
      `cor:rationale`. **Every `cor:expectedVerdict` stays `cor:Unadjudicated`.** A HOLD is encoded AS
      `cor:Unadjudicated` + a `cor:adjudication` carrying the reason
      (`tests/corpus-manifest.ttl:16-20`); there is no `cor:Hold` term and you must not invent one.
      Each rationale states: the **measured score**, the **escalation census for that document**
      (per reason, per page, graph-side — **D2**), and **what is being held and why**.
      The census's own characterisation is the material: apple's 11 are `REGION_TILING_FAILED` ×4 on
      p0 and ×4 on p2 (the cash-flow / income statements), `MATRIX_AMBIGUOUS` ×1 on p0 and ×1 on p2
      (the `Three Months Ended … Nine Months Ended` double header), `DATAGRID_RESIDUE` ×1 on p1;
      bfs's 10 are `ROUND_TRIP_FAIL` ×5 all on p5 (all region-level `#htable{n}-rt` URIs),
      `KIND_NOT_SUPPORTED` ×3 (p0 masthead, p6 ×2), `REGION_TILING_FAILED` ×2 (p4, p5 — chart captions
      with mangled glyph runs); who-wfa's 3 are `MATRIX_AMBIGUOUS` ×1 per page on the identical
      z-score header block — **one defect, three firings.** Say that; it is what an adjudication is for.

- [ ] **Step 3: all six HOLD, including the three that escalate nothing — and the rationale must say
      why.** cbh-stem (0.9047), graincorp-capacity (1.0000) and ons (0.9720) emit **no escalation
      record at all**, and a score is **not** an acceptance: nobody has checked the reading against
      the document. Two specific reasons to record: cbh-stem's **86 escalated tokens sit inside
      asserted regions and mint no record** (`compile.py:960`), so its escalation surface is invisible
      to a record count; and ons books **70 free-text "ignored band" classification reasons and zero
      escalations** (census § *Method*, the stated trap), which a naive reading would mistake for a
      clean document. **graincorp-capacity is the nearest to acceptable — name what would accept it**
      (a `cor:contract`/`cor:terms`/`cor:shapes` triple and a passing
      `test_grounding_where_contracted`, which it does not have today), so the rung has a stated path
      rather than a permanent 1/7.

- [ ] **Step 4: record graincorp-stem's stale adjudication as a finding, and do not repair it here.**
      Its 2026-08-02 note describes page-1/2 `REGION_TILING_FAILED` escalations **that do not survive
      at HEAD** — it escalates nothing now. Its later notes (2026-08-03) are current and its floor
      holds (0.9655 ≥ 0.95, reproduced in the census). Add a **new** dated `cor:adjudication` saying
      the 2026-08-02 note is superseded and why. **Do not edit the historical note** — the manifest's
      adjudications are an append-only record, which is the whole reason there are three of them.

- [ ] **Step 5: write the gameability falsifier — spec §8 names it and it is the one test this task
      must not ship without.** The assertion: **a document whose `cor:scoreFloor` is pinned at its
      currently-measured score, with a rationale that records a HOLD rather than accepting the score,
      does NOT satisfy the `etkl` criterion.** Concretely, the test constructs a synthetic manifest
      entry in that exact state and asserts the `etkl` criterion's met-predicate returns false for it.
      **MEASURE FIRST, before writing the call:** the criterion's met-ness in `tests/arc-manifest.ttl`
      is an *asserted boolean*, not a computed one (spec §3.1) — so **there is no met-predicate
      function to call unless this task writes one.** Decide and state which of these you did:
      (i) write a small reader that computes the `etkl` criterion from `corpus-manifest.ttl` and pin
      the manifest's asserted booleans equal to it, or (ii) pin the *rule* directly on the manifest
      (`cor:Unadjudicated` + `cor:adjudication` ⇒ not met) without a general reader.
      **(i) is the stronger test and is preferred**, because it makes the `etkl` rung's numerator
      derived-and-checked rather than merely asserted-and-refused. If you choose (ii), say why in the
      task report.

- [ ] **Step 6: run** `./.venv/bin/python -m pytest tests/test_corpus.py -q` — the manifest-integrity
      shape (`tests/corpus-shapes.ttl`) must still conform. **It requires a `cor:sha256` and a
      `cor:adjudication` on any non-`Unadjudicated` verdict**; you are adding adjudications while
      leaving verdicts `Unadjudicated`, which that constraint permits. Confirm it, do not assume it.

- [ ] **Step 7: `## FALSIFICATION`** — change one HOLD rationale to an accepting one and pin the
      verdict to `cor:CompilesAbove` with a floor at the measured score; show the step-5 test
      **failing**. Restore; show green. **This is the single most important falsification in the plan**
      — it is the defect `820ab24` fixed in prose, and this is the test that stops it recurring.

- [ ] **Step 8: commit.** `feat(corpus): six documents move from unlooked-at to measured, reasoned, held`

---

## Task 6: the `tab` rung — 10 criteria

**Files:** Modify `tests/arc-manifest.ttl`.

**Interfaces:** Consumes Task 5's adjudications. Produces `urn:iladub:arc:crit:tab:01..10`.

- [ ] **Step 1: RE-GREP the reason list from the code. Do not copy it from the spec or from this
      plan.** There is no enum and no registry — the reasons exist only as string literals at
      `escalate_region(` call sites, deliberately (`_suggester_uri`, `holon.py:409-421`: *"a
      hand-maintained table drifts from the call sites … and the drift is silent"*). **The manifest's
      reason list is a copy of a grep and must carry the grep that produced it.** Run a grep over
      `escalate_region(` call sites in `src/` and record every reason literal with its `file:line`.
      The census measured **nine** at `820ab24`: `MULTI_TABLE_AMBIGUOUS` (`compile.py:596`),
      `REGION_TILING_FAILED` (`:656`, `:763`, `:939`), `TRANSPOSED` (`:688`), `ROW_GROUP_AMBIGUOUS`
      (`:739`), `MATRIX_AMBIGUOUS` (`:830`), `MERGE_AMBIGUOUS` (`:911`), `KIND_NOT_SUPPORTED` (`:978`),
      `DATAGRID_RESIDUE` (`:1145`), `ROUND_TRIP_FAIL` (`holon.py:493`). **If your grep disagrees, your
      grep wins** — report the difference and adjust the denominator.

- [ ] **Step 2: author criteria 01–09, one per reason, in the D1 two-armed form.** Statement:

      > *This escalation reason is disposed: either it fires on the 7-document corpus and every firing
      > document carries a dated `cor:adjudication` naming and disposing of it; or it fires nowhere on
      > the corpus and names a collectable `prog:oracleTest` that exercises the path, plus a recorded
      > reason distinguishing corpus gap from dead path.*

      `prog:declaredOn` for these nine is **the date this loop declares them** — they are the one
      rung §7 says had to be *constructed*, so they are **`retrospective false`** and every future flip
      is a genuine measurement.

- [ ] **Step 3: for the five firing reasons, wire the blocking edges — and expect all five unmet.**
      From spec §7.4, **re-verify each row is still open before writing it** (M7 checks existence, not
      openness; a struck row would be a stale edge M8 cannot catch): `REGION_TILING_FAILED` → R43, R44,
      R62; `KIND_NOT_SUPPORTED` → R44, R71; `MATRIX_AMBIGUOUS` → R45, R62; `ROUND_TRIP_FAIL` → R44;
      `DATAGRID_RESIDUE` → R79, R83, R84. **M8 forbids `met true` on any criterion carrying an open
      blocker, so Task 5's six adjudications cannot flip these — that is the guard working, not a
      failure of Task 5.**

- [ ] **Step 4: for the four corpus-dead reasons, MEASURE the fixture that exercises each.** A
      first-cut grep over `tests/` (2026-08-20) found the literal in:
      `MERGE_AMBIGUOUS` → 7 test modules + `tests/etkl/fixtures.py`; `MULTI_TABLE_AMBIGUOUS` →
      `test_closing_slice.py`, `test_segment.py`, `fixtures.py`; `ROW_GROUP_AMBIGUOUS` →
      `tests/etkl/test_tiling_gate.py` **only**; `TRANSPOSED` → 5 modules + `fixtures.py`.
      **A file containing the literal is not an oracle.** Resolve each to a specific **node id** that
      actually drives the reason through `escalate_region`, and verify it collects. Then:
      - a reason with such a node id → `met true` **iff** it also carries no open blocker (`TRANSPOSED`
        has no blocking row in spec §7.4's table — **measure whether one exists**; `MERGE_AMBIGUOUS`
        has none; `MULTI_TABLE_AMBIGUOUS` → R74; `ROW_GROUP_AMBIGUOUS` → R80, R74, R77);
      - a reason with **no** such node id is **dead path** → `met false`, and **raise a residue row**
        for it (this is the loop's one permitted new row, and it is a real finding).
      **Expect `tab` to land at 1/10 or 2/10.** If it lands higher, an open blocker went missing.

- [ ] **Step 5: author criterion 10 — the compile membrane's vacuity registry, widened per D3.**
      Statement: *every shape wired into the compile membrane is live, or registered idle with an
      adjudicated reason distinguishing corpus gap from dead shape.* Half-met and the half is
      recorded: `VACUITY_REGISTRY` (`tests/etkl/test_vacuity_registry.py:87`) exists and **both its
      arms are green** — an idle shape must be registered, and a registered shape that goes live
      **fails** the guard until its row is deleted. What is unmet is the adjudication of the four rows
      that say *"corpus gap or dead shape, not adjudicated here"* (`tab:AggregationCellShape`,
      `tab:BaseFactShape`, `tab:PivotedDimensionShape`, `tab:SectionTotalShape` — measured 2026-08-20;
      `tab:LicenceRefusalShape` carries a real adjudication and is not one of the four).
      `met false`; `prog:blockedBy` R97, R98, R99, R100. Oracles:
      `tests/etkl/test_vacuity_registry.py::test_every_idle_shape_is_registered` and
      `::test_no_registered_shape_has_gone_live` (**both verified collectable**).

- [ ] **Step 6: record D2 in the manifest, not only in this plan.** Put the graph-side/report-side
      reconciliation in a comment at the head of the `tab` block: **24 graph-side, 29 report-side, the
      difference is apple p1's 5 withdrawn escalations** (`document.py:1512-1513` →
      `_remove_escalation_record`, while `compile.py:1132-1136` rewrites only `verdict` and
      `tokens_escalated`). A future re-measurement reading 29 must recognise a known difference, not
      drift. Also record that **`ROUND_TRIP_FAIL` is two mechanisms under one label** — region-level
      (`holon.py:493`, all 5 corpus firings) and cell-level (`_emit_roundtrip_fail_cell`,
      `holon.py:55`, corpus-dead) — so a count keyed on the label alone cannot tell them apart, and one
      document hitting the cell-level path could inflate it by hundreds. **Whether the manifest should
      split them is deliberately left open; say so rather than deciding it silently.**

- [ ] **Step 7: run the membrane.** Expected: green, `tab` at its measured fraction.

- [ ] **Step 8: `## FALSIFICATION`** — take one firing reason (`REGION_TILING_FAILED`), flip it to
      `met true` leaving its `prog:blockedBy` R43/R44/R62 in place, and show **M8 firing**. Then remove
      the blockers and show it conforming — **which is the point**: the edges are what hold the rung
      honest, and M8 is what makes them binding. Restore both.

- [ ] **Step 9: commit.** `feat(arc): tab counts the reading's own refusals, and silence is not a pass`

---

## Task 7: the four derivations

**Files:** Create `vocab/queries/arc-position.rq`, `arc-frontier.rq`, `arc-unblocked.rq`,
`arc-orphan.rq`; create `tests/test_arc_queries.py`.

**Interfaces:**
- **Consumes:** the full manifest from Tasks 3, 4, 6.
- **Produces:** four query files, each with a stable result shape the cockpit test (Task 8) and any
  future session can rely on:
  `arc-position` → `(?rungKey ?met ?declared)`; `arc-frontier` → `(?residue ?rungKey ?criterion)`;
  `arc-unblocked` → `(?rungKey ?criterion ?statement)`; `arc-orphan` → `(?residue)`.

- [ ] **Step 1: read `vocab/queries/` for the house style** — 30 files exist; match their prefix
      declarations, comment header and formatting rather than inventing a new one.

- [ ] **Step 2: write the failing tests first**, each against a **small hand-built fixture graph with
      an answer you computed by hand** — not against the live manifest, whose answer changes every
      loop. One test per query, plus:
      - `test_arc_position_counts_a_rung_with_no_criteria_as_unknown_not_zero` — the rung must be
        **absent or null**, never `0/0` rendered as zero (decision 6; spec §9 forbids the `0` reading
        explicitly, so a test asserting `0` here contradicts the spec and must not ship).
      - `test_arc_orphan_derives_nothing_about_the_residue_itself` — the `NOT EXISTS` is holon-scoped:
        it closes only within the query and asserts nothing about the row (CLAUDE.md §8).
      - `test_no_query_infers_a_fact_from_absence_of_evidence` — inspect the four `.rq` sources and
        assert that every `NOT EXISTS` / `MINUS` is inside a query whose output is a *selection*, never
        a *derived fact about a criterion's met-ness*.
      - **A live-repo arm for `arc-orphan`:** R101 is the measured first instance of a residue that
        blocks no criterion of any rung, and spec §7.4 says that is a **finding, not a gap** — assert
        it appears, and if it does not, say so rather than adjusting the query.

- [ ] **Step 3: run them; they must fail** on the missing `.rq` files.

- [ ] **Step 4: write the four queries.** Open world, evidence-positive, monotone. `arc-position` is a
      `SELECT` with `COUNT` grouped by rung — **the `COUNT` closes within one rung only**, which is the
      holon-scoped closure CLAUDE.md §8 permits. **No query writes anything and none is a `CONSTRUCT`
      that adds `prog:met`.**

- [ ] **Step 5: run against the live manifest and print the four results in the task report.** These
      are the figures the strip will show; a reviewer needs to see them next to the manifest.

- [ ] **Step 6: `## FALSIFICATION`** — delete the `FILTER NOT EXISTS` from `arc-orphan.rq` and show
      its test failing; delete the `prog:met false` binding from `arc-frontier.rq` and show a **met**
      criterion's blocker appearing in the frontier, which is the defect that query exists to avoid.
      Restore both.

- [ ] **Step 7: commit.** `feat(arc): four derivations — position, frontier, ready, orphan`

---

## Task 8: the cockpit — two lines, and a fast reader that agrees with rdflib

**Files:** Modify `scripts/cockpit.py`; modify `tests/test_cockpit.py`.

**Interfaces:**
- **Consumes:** `tests/arc-manifest.ttl` (regex only) and `docs/superpowers/residues.md`.
- **Produces:** `cockpit.arc() -> list[tuple[str, int | None, int | None]]` — one
  `(rungKey, met, declared)` per rung **in the settled order** `etkl, dec, holon, tab, substrate`
  (a *display* order, not a `prog:precedes` claim — the manifest still asserts no ordering, spec §9);
  `(None, None)` counts for a rung with no criteria. Plus `cockpit.frontier_counts() -> tuple[int, int]`
  returning `(frontier, ready)`.
  **This changes `arc()`'s signature from `(pos, stages)`. It is a deliberate interface change; every
  caller is in this file and in `tests/test_cockpit.py`.**

- [ ] **Step 1: honour the performance contract before writing a line.** `cockpit.py:34-38` forbids
      rdflib, pytest, the network and the corpus. `arc()` splits the manifest on top-level
      `<urn:iladub:arc:crit:` subjects and reads `prog:met true|false` within each block. **M9 (Task 1)
      is what makes that safe** — every criterion is a top-level IRI subject encoding its own rung.
      If M9 is not in `arc-shapes.ttl`, stop: this step's premise is gone.

- [ ] **Step 2: write the agreement test first — it is the point of the task.**
      `test_the_strips_reading_equals_rdflibs_reading_of_the_same_file`: parse `tests/arc-manifest.ttl`
      with rdflib, run `vocab/queries/arc-position.rq`, and assert the result **equals** `cockpit.arc()`
      exactly. *This test would have caught the `residues()` regex defect on the day it shipped* (fixed
      since, `8bd3120`). It may use rdflib — it is a test, not the strip.

- [ ] **Step 3: preserve the honesty test in substance.**
      `test_the_arc_gauge_reports_unknown_and_must_not_guess` currently asserts `pos is None` and
      `"stage ?/" in …`. Both literals change with the interface. **The assertion that must not weaken
      is: a missing source yields `?` and never a number.** Rewrite it to point `cockpit.ARC_MANIFEST`
      at an absent path and assert every rung renders `?` — and keep the docstring's warning verbatim,
      because it is the reason the test exists.

- [ ] **Step 4: change the one-line test to two lines, with its reason in the docstring.**
      `test_it_exits_zero_and_prints_one_line_with_stdin_attached` becomes a **two**-line assertion.
      Record in the docstring: multi-line `statusLine` is documented as supported (*each print
      displays as a separate row*), limits and wrap-vs-truncate are **undocumented**, and multi-line
      plus ANSI is flagged as glitch-prone — so if rendering breaks in practice the fallback is the
      compact single-line form with fractions behind `--verbose`, **never abbreviated rung names**
      (decision 8). **This is a deliberate relaxation of a pin, and a reviewer must be able to see why
      from the test alone.**

- [ ] **Step 5: implement `arc()`, `frontier_counts()` and the second render line.** Target form:
      ```
      arc  etkl ▰▱▱▱ 1/7  dec ▰▰▰▱ 10/16  holon ▰▰▰▱ 4/6  tab ▱▱▱▱ 1/10  substrate ▱▱▱▱ 0/3  frontier N  ready N
      ```
      **The fraction sits beside every bar** — a bar reads as a percentage and these are checklists
      (decision 6). A rung with no criteria renders `?`, never an empty bar. **The `stage ?/5` segment
      on line 1 is replaced by this line**, and `arc()`'s old `^### `-counting denominator goes with
      it — the manifest is the denominator now. **Do not delete `_newest_loop_doc`/`entry_point`**;
      the `▸` slot keeps the filename (D4).

- [ ] **Step 6: `test_no_stuck_verdict_is_computed_anywhere` must still pass unchanged.** It walks
      `cockpit.py`'s AST for verdict strings and for `is_stuck`/`velocity_index`/`health_score` names.
      **If you were tempted to rank the frontier residues, this is the test that says no** (D4).

- [ ] **Step 7: run the full suite.** `./.venv/bin/python -m pytest -q`, then render the strip for
      real: `./.venv/bin/python scripts/cockpit.py --no-color --refresh </dev/null | cat -A | head`
      and paste both lines with their measured lengths into the task report.

- [ ] **Step 8: `## FALSIFICATION`** — introduce a deliberate off-by-one in `arc()`'s regex (drop the
      last criterion of one rung) and show the **agreement test failing**; restore. Then delete
      `tests/arc-manifest.ttl` and show the honesty test still passing with every rung at `?` — and
      **confirm nothing raised**, since a status line that raises is worse than no status line.

- [ ] **Step 9: commit.** `feat(cockpit): five fractions the strip can defend, on a second line`

---

## Self-review against the spec

**Coverage.** §3 model → Task 1 (`prog:` shapes) + Tasks 3/4/6 (the instances). §3.1 asserted-`met` →
Task 1 M2/M5, Task 8 step 2. §3.2 `retrospective` → Task 1 M4, Tasks 3/4/6's flags. §3.3 the edge →
Task 6 step 3, Task 7. §4 M1–M8 → Task 1 (**plus M9**, flagged as this plan's addition). §5 the four
derivations → Task 7. §6 the surface → Task 8. §7.1 `etkl` → Task 3 step 2 + Task 5. §7.2 `dec` →
Task 4. §7.2.1 the wrong pointers → Task 4 step 1 + Task 1's M5 fixtures. §7.2.2 the runner →
Global Constraint 1 + M5c. §7.3 `holon` → Task 3 step 3. §7.4 `tab` → Task 6 (**with D1 replacing the
two-armed wording**). §7.5 `substrate` → Task 3 step 4. §8 the falsifiers → each task's
`## FALSIFICATION`, with §8's gameability falsifier at Task 5 step 5/7. §10 register repairs → Task 2.
**§11's seven seams are ALL discharged before the first line of code**, which is the property that
makes this a plan rather than a draft: 1 and 2 measured in the census; **3 measured** (the
`prog:declaredOn` table, re-verified per criterion in Task 3 step 1 and Task 4 steps 2–3);
**4 measured** (1252 tests collect clean under the venv runner, 0 errors, 0 collection-time skips);
**5 measured** (D4 — multi-line `statusLine` is documented as supported); **6 measured** (7 rows, the
spec's list exact, 5 real edges — and it is not this loop's work); **7 answered** by D3.

**Reconciled against §9 (CLAUDE.md rule 5).** §9 forbids: persisted tally history (no task builds one);
a velocity index (Task 8 step 6 pins the refusal); ordering between rungs (Task 8's display order is
named as display-only; no `prog:precedes` anywhere); auto-writing the manifest (Global Constraint 4;
Task 5 step 5 option (i) computes a *check*, never a write); a sixth rung (M6); closing a residue
(Task 2 step 5 says so explicitly); a `CLAUDE.md` edit (no task touches it — including the stale
`CLAUDE.md:452-456` claim that the `holon` rung's 4/6 contradicts, which is left standing on purpose).
**The two contradictions §11 warned about are specifically excluded:** no task expects the manifest to
write itself, and Task 7 step 2's first test asserts a criterion-less rung reads **unknown, not zero**.

**One new residue row is expected and permitted** — Task 6 step 4, if a reason turns out to have no
fixture exercising it (dead path). That is a finding this loop measured, not a deferral.

**Open, and deliberately not decided here:** whether the manifest should split `ROUND_TRIP_FAIL`'s two
mechanisms (Task 6 step 6); and whether the strip should visibly distinguish a recorded HOLD from
"nobody has looked" on the `etkl` rung (spec §7.1 calls this a render question the plan may raise —
it is raised, not answered, because the manifest records the difference either way).
