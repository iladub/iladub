# Handoff — the score gate ran: the switch is free, and the score cannot see the defect

**Topic:** Four loops deferred compiling a document behind the alignment universe. It ran. bfs p5
carries **92 more cells and 1103 more triples at a score identical to ten decimal places**, with
adoption retained, no escalation gained and [[R44]]'s reason census unmoved. Six of seven
documents are byte-identical. PR #237's headline cost — *"cbh loses 5 rows"* — **does not exist at
compile scope.**

**Serves:** prog:criterion:etkl:05 — bfs. [[R44]] gates it through tab:02, tab:07 and tab:09.

**Date:** 2026-09-16. **Tree:** branch `r239-alignment-universe-gate`, cut from `main` at `d653036`.
**No shipped file edited. No behaviour changed.** One instrument added, measurement only.

**Doc impact: none.**

---

*(§ 5, the next concrete action, is written when the N1 null control resolves — it is the one part
of this document whose content depends on the outcome, and it is typed there as assertion or
proposition per CLAUDE.md § "The handoff's next action is TYPED".)*

---

## 1. Where the primaries are

- **This loop's evidence** — `2026-09-16-r239-alignment-universe-gate-evidence.md`. § 1 is the
  proof the monkeypatch reaches `compile_document`; § 2 is the reading rule, **committed before
  the baseline landed** (`fc05357`); § 2d is the prediction, **committed before bfs compiled**
  (`72faef7`); § 3 is the result; § 3d is the one thing measured only as arithmetic.
- **The instrument** — `scripts/r239_alignment_universe_gate.py`. Three universes (`before`,
  `alignment`, `null`); § 8 class PROCEDURAL; the null control and the patch-reach argument are in
  its docstring.
  `PYTHONPATH=src .venv/bin/python scripts/r239_alignment_universe_gate.py alignment <out>`
- **The differ** — `scripts/corpus_snapshot_diff.py`, shipped, a separate code path from this
  loop's ad-hoc comparison. Both agree.
- **The snapshots** — session-local under the scratchpad (`before/`, `alignment/`, `null/`), seven
  JSON files each. **They do not survive the session**; § 3's figures are the surviving record.
- **The prior loops** — PR #236 (blast radius: the `x1` re-key regresses 20 cells), PR #237
  (universe, not key — the grid-scope measurement), PR #238 (the straddle universal, refuted
  48/48).
- **The rows** — [[R238]] and [[R239]], `residues-open.md:167` and `:168`; index
  `residues.md:398-399`.

## 2. What was decided, and where it is recorded

| decision | recorded |
| --- | --- |
| The gate RAN — four loops of deferral ended | evidence § 3, both rows |
| bfs p5: 404 → 496 cells, +1103 triples, score unmoved to 10 dp | evidence § 3c |
| The score is an ink ratio (`document.py:1582`) and is **blind to this defect** | evidence § 3c |
| Only 1 of 7 documents moves; six byte-identical | evidence § 3b |
| **cbh's 5-row cost is a GRID-scope artefact — it does not survive to compile scope** | evidence § 2d, § 3b |
| Adoption is what carries a grid reading into the graph | evidence § 2d |
| Control P passed (bfs moved) and is corroborated by the startup line | evidence § 3a |
| N2 passed 7/7 against a prediction committed before bfs compiled | evidence § 3a |
| What the 92 cells ARE | **NOT measured** — evidence § 3d |

## 3. Unverified or assumed

- **§ 3d — what the 92 cells are.** 46 rows × 2 columns = 92 is *arithmetic agreement only*. The
  probe is named in § 3d; do not cite the match as the answer until it has been run.
- **Whether alignment's 12 columns are the right 12** — unchanged from PR #237, checked on 3 of 27
  rows, presence only. This loop did not touch it.
- **Why graincorp-capacity p0 straddles nothing** — still uninvestigated, four loops on.
- **What p5 region16 `DATAGRID_RESIDUE` holds** — still unanswered, five loops on.
- **Do not trust the `tab` rung's `file:line` citations or `FIRES n` counts** — [[R236]], [[R237]].

## 4. What this session did, and what it cost

Ran the gate three loops had deferred, across all seven documents, under three universes, with the
reading rule and then the prediction each committed before the data that tested them existed. Both
held.

**The cost worth carrying: I reversed a correct caution on a bad measurement, and it cost ten
minutes.** The two corpus runs were deliberately serialized because this repo has a recorded
history of memory kills. I then reversed that on a single RSS reading of ~206 MB — **taken
mid-run on a small document, which is not peak** — and launched both concurrently. The system
killed both. The original caution was right, the "correction" was wrong, and the reasoning that
produced it (an early figure read as headroom) is the kind a fresh session would repeat for
exactly the same plausible reason. Recorded in user memory as `corpus-runs-are-serial`.

**A second, smaller one, committed while the first was still fresh:** the alignment run was piped
through `tail -20`, so the instrument's `universe=alignment …` confirmation line could not flush
until exit — meaning patch installation was unreadable for the whole run, and control P had to
carry that weight alone. That is the same mistake as the pytest-into-`tail` rule already in
memory, in a different shape. The null run was launched without the pipe.
