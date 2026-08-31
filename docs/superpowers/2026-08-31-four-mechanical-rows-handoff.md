# Handoff — the 2026-08-30 menu is exhausted; what is left needs a ruling, not an edit

**Topic:** `R137`, `R152`, `R138` closed by repair, the `test`-job-name guard shipped, and why the
next loop cannot be another row-closing loop

**Part 5 was written FIRST**, before parts 1–4, per CLAUDE.md § Loop & context hygiene. Authored at
roughly **55,000 working tokens — 1.1× the 50,000 originating floor**; the override is logged. That
is the lowest figure any handoff in this repo records, and it is low for a structural reason worth
stating: this loop closed a menu somebody else had already reasoned out, so almost none of the
session's budget went on originating anything.

## 5. The next concrete action — TYPED, per action

Branch off `main` once this loop's PR is merged.

### ASSERTED — the outcome is known; doing it *is* the work

Nothing. **The 2026-08-30 menu is empty**: `R137`, `R152` and `R138` are struck, and the
`test`-job-name row the 2026-08-31 handoff added is shipped. This is the honest state, not a gap —
every remaining open row that a reasonable next loop would pick up is blocked on a decision, and
that is what the next two subsections are.

### PROPOSED — rests on a prediction that must be RUN before anything is built on it

**`R139`'s instrument half — a lint for downward same-file `file:line` citations.** This loop is the
reason it is now the strongest candidate, and the reason is not enthusiasm: closing `R138` **committed
`R139`'s exact failure a second time, in a different medium, while applying its own remedy elsewhere
in the same edit.** Two measured instances now, one `.py` and one `.md`, both by an author who knew
the rule. A convention a rule-aware author breaks twice is evidence for an instrument.

**The prediction, and it is the thing to run first:** *a lint that flags a `file:line` citation whose
target is the same file and whose line is below the citation's own position has a false-positive rate
low enough to ship on this tree.* It could easily be false — this repo cites lines constantly, and a
naive rule would flag `residues-*.md` rows quoting historical citations, this handoff, and every
`⚠️ CORRECTED` note that quotes what was wrong. **Run the census before designing anything:** count
the hits over tracked `.py` + `.md`, split into genuine live citations vs. quotations-of-a-past-
citation. If the split cannot be made mechanically, the lint is not shippable and `R139`'s instrument
half should be recorded as *refused with a measurement* rather than left open a fourth month.

Budget minutes for the census, not hours. If it refutes, the loop to run is one of the next two.

### PROPOSED — blocked on a ruling the maintainer has not made; NOT scoped here

Unchanged from `docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5, and **not re-derived
here** — open that table:

- **`R132`** (one `_DOC` for every document) — the hard part is an identity/merge ruling, not the edit.
- **`R127`** (uncapped `dec:rationale`) — coupled; four shipped oracles must be re-homed in the same act.
- **`R131`** half (b) (minting page-scope health) — stays `holon:06`'s.

## 1. Goal

Close the three mechanical rows the 2026-08-30 handoff queued, plus the one the 2026-08-31 handoff
added. Done: `R137`, `R152`, `R138` struck; `tests/test_required_check_name.py` shipped. The register
moves **34/142 → 37/142 closed**. One row updated rather than raised (`R139`, second instance). **No
new row was opened**, which is the first loop in some time that can say so.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/residues-closed.md`, rows `~~R137~~`/`~~R138~~`/`~~R152~~` | The closure evidence, each with its falsification transcript. The index line is a pointer — open the row |
| `docs/superpowers/residues-open.md`, row `R139` | The **second** measured instance of the downward-citation class, and what it changes about the instrument half |
| `tests/test_residue_register_integrity.py` | `R137`'s guard, and the one thing it deliberately does not check |
| `tests/etkl/test_compile_membrane_shapes.py` (tail) | `R152`'s guard, why its scope is wider than the row prescribed, and the tiling arm that proves the widening is sound |
| `tests/test_required_check_name.py` | The `test`-job-name guard, and the half of the question it cannot see |
| `…/specs/2026-08-25-the-membrane-reports-its-health-design.md` § 4.5 | `R138`'s repair — a `⚠️ POINTERS CORRECTED` note plus symbol references |

## 3. What was decided, and where that decision is recorded

- **`R152`'s scope was WIDENED beyond the row, on a measurement.** The row prescribed
  `wired_shape_files()` — the compile leg — but `membrane._payload_nt` skolemizes for **three** legs
  (`compile.py:546`, `feed.py:615`, `tiling.py:70`), so the premise is about all of them. The guard
  reads the compile ∪ grounding union from the wiring modules, and a second arm proves the tiling leg
  is covered by inclusion rather than asserting it. Recorded in `~~R152~~` and in the test docstring.
- **`R138` was closed by the row's *preferred* disjunct (symbols), not by re-measuring the numbers.**
  Recorded in `~~R138~~` and in the spec's own correction note.
- **`R138`'s scope was NOT widened.** The same drift affects other sections of that spec; those are
  left standing, because rewriting a dated Evidence artefact's *arguments* is a heavier act than
  repairing the pointers one register row names. Recorded in the correction note, which names the
  `grep` that finds the rest. **Reversible — nobody has ruled it.**
- **The register's prose tally (`residues.md:41`, "As of 2026-08-24: 116 rows, 24 closed") was left
  untouched and is now staler by three.** Not an oversight: the file carries three ⚠️ CORRECTED notes
  about exactly this drift and has already ruled the sentence a convenience and the counting command
  the authority. Adding a fourth correction is the pattern the file criticises. **Recorded here and
  nowhere else — reversible, and a candidate for a fifth arm of the new integrity test if anyone
  disagrees with the ruling.**
- **Falsification evidence, per row** (CLAUDE.md plan-rule 4). Every ablation was restored and the
  tree verified clean afterwards:

  ```
  R137  (a) delete index row R135        → test_every_detail_row_has_an_index_row        1 failed, 5 passed
        (b) flip R126 closed → open      → test_every_index_row_has_exactly_one_detail…  1 failed, 5 passed
        (c) unstrike ~~R126~~ in closed  → test_a_row_is_struck_iff…[closed]             1 failed, 5 passed
  R152  (a) sh:nodeKind into dec-shapes  → …skolemization[dec-shapes.ttl]                1 failed, 14 passed
        (b) isBlank() into a sh:select   → …skolemization[tab-shapes.ttl]                1 failed, 14 passed
        (c) drop tab-physical from wiring→ test_the_tiling_leg_adds_no_shape_file…       1 failed, 13 passed
  ci    (a) rename job test → tests      → test_ci_defines_a_job_named_exactly_test      1 failed, 1 passed
        (b) delete the pull_request trigger → test_ci_still_runs_on_pull_requests        1 failed, 1 passed
  ```

  `R137`'s (a) and (b) are the two that stayed **green across 67 tests** when the row was raised on
  2026-08-25; that contrast is the closure. `R138` has no ablation of this shape — it is a
  documentation repair, and its evidence is that the cited symbols resolve where the numbers did not.

## 4. Unverified or assumed

- **`R138`'s repair committed `R139`'s defect and was caught by re-measuring after the edit.** The
  correction note first listed the file's other stale citations by line number — all below the note,
  all shifted by inserting it. Replaced with a `grep` command. **The catch was manual; nothing in the
  suite would have found it**, which is exactly `R139`'s open half.
- **`tests/test_required_check_name.py` pins only the half that lives in the working tree.** That the
  *ruleset* still requires the context `test` is not checked — that needs a network call and a token.
  If the ruleset is changed, this test goes on passing while being wrong. Stated in its docstring.
- **`R152`'s guard does not make `sh:nodeKind` work at the membrane.** It fails the day someone writes
  the constraint; it does not repair the seam disagreement. That is `R88`'s territory.
- **The corpus-marked suite was NOT run.** Only `-m "not corpus"`. Unchanged from the last two loops.
- **The 150K executing floor is still labelled `NO SOURCE` in `tiers.py`.**
