# Handoff: R301's plan seams are measured, and three of them amend the spec (2026-10-08)

**Serves:** maintenance. This is [[R301]], continuing the spec
`docs/superpowers/specs/2026-10-08-r301-producer-guard-design.md` (PR #322), whose § 4 assigned
U1–U4 to the plan's first measurements.

**Topic:** compile · **Date:** 2026-10-08 · **Branch:** `r301-producer-guard-plan`, cut from
`r301-producer-guard-spec` at `6442818`.

**Doc impact: none.** It adds this handoff and three probe scripts. No vocabulary, shape or compile
path changes.

**Why a handoff and not the plan.** The session reached 55K working tokens (1.1× the originating
floor) once the measurements were in, before any plan text was written. The measurements were
delegated to two subagents. Authorship was not delegated. The preflight was logged as `handoff`.

## 5. Next concrete action (written first, at about 59K working tokens, 1.2× the floor)

1. **ASSERTED: settle S1–S3 (§ 1) before the plan is written, as a spec addendum or by a ruling
   in chat.** Each is a measured fact that contradicts or underdetermines a spec sentence.
   Following CLAUDE.md § Plan authoring rule 6, the spec is the file to fix, not the plan. Each
   item below carries a *proposed* remedy. None of them is ruled.
   - **S1. The withdrawal extent's prefix rule over-reaches.** `str(t) + "-"` also matches
     `…#p7-datagrid-2…` (a second grid, R290) and `…#p7-datagrid-residue` (the residue
     candidate), checked by string test. Spec § 2.2's roots would sweep a sibling grid.
     *Proposed:* exclude every root that lies in the URI space of another report's `table_uri`,
     or that is the residue IRI. Today's corpus is not exposed: p5 and p7 each have one owner and
     no residue at guard time (U1). Exposure is still structural, which is why it needs an
     explicit ruling.
   - **S2. The refusal decision's IRI and label must not alias the verdict.**
     - `recorder.band(i)` builds a fresh `BandRecorder` whose counter restarts at `-d0`. It
       **overwrites** the band's existing `d0`: measured on a synthetic, the labels on `d0` became
       `['kind', 'verdict']`.
     - `ReadingRecorder` is bound to the pre-adoption graph (`decisionlog.py:79`), and adoption
       rebinds `graph` (`compile.py:2061`).
     - `document._verdict_decision` returns the first subject under prefix `#region{idx}-d`
       labelled `"verdict"`, in set order. A refusal labelled `verdict` in that space could
       therefore be returned instead of the original.

     *Proposed:* mint the refusal at a distinct, deterministic IRI outside `-d{n}`, such as
     `{doc}#region{i}-refusal`, written directly rather than through `BandRecorder`. Give it a
     label other than `verdict`, such as `refusal`, and set `dec:order` to one past the
     superseded head's order.
   - **S3. Oracle O2's wording is wrong as written.** `vocab/queries/effective-chain.rq` returns
     `dec:chosen/rdfs:label`, so a refusal whose chosen option is labelled `refuse` reads `refuse`
     and never `escalated`. If the refusal regards the band's own `#region{i}`, the query returns
     the whole pass-1 chain plus the refusal, with the refusal as the last row. Both were measured
     on synthetics. *Proposed:* restate O2 as "the chain's last row is the refusal, with `chosen`
     = `refuse`". Do not relabel the option to fit the oracle.
2. **Then write the plan, in a fresh session. ASSERTED** once (1) is settled. § 1's M-items are its
   "Measured seams" section: cite them, and re-measure any line number before writing against it.

## 1. What was measured

**U1 (the spec's PROPOSED first measurement): CONFIRMED, by a run.**
- Command: `scripts/r301_u1_ledger_probe.py i2` and `… stock`, at `6442818`, about 6 s each.
- It compiles fed-h41 p7 under `doc_uri = …/p7/adopt` (the driver's own URI, `document.py:1786`).
  An in-memory hook places the pre-adoption guard (the position handoff's `pre` hook, with the
  spec § 2.2 extent).
- Results:

  | ledger | asserted | escalated | touched | gate (`< 137`) |
  |---|---|---|---|---|
  | stock | 137 | 137 | {1} | refuses on the tie (G3 reproduced) |
  | I2 prototype | 137 | 0 | {1, 3} | opens |

- The select over the adoption branch's **new** graph, after `carry_from_pdf` and before install,
  returns **12 cells**. They have the same IRIs and texts as the fallback grid's 12 (`r7c1…r7c12`,
  the glued-sign row, e.g. `'63,061-'`). The rows are the same too: `(8, 9, 12, 15, 16, 18, 19,
  20, 21)`.
- So § 2.1 step 5 is motivated. Without it, I2 would install a 1.0000 page holding the 12 refused
  cells.
- The I2 prototype in the probe treats `reports[len(bands)+k]` as covering fallback grid k's
  `rows`. That is exactly what M6 below says `build_ledger` cannot see today.

**U2: CONFIRMED, by a run.**
- Command: `scripts/r301_u2_admission_probe.py`, about 8 s.
- On p7 without adoption, the spec § 2.2 extent removes **291 roots / 1933 triples**, following
  **0** blank nodes. p7's bboxes are URIRef roots (`-rNcN-bbox`), not blank nodes as on p5.
- `{t}-admission` survives with all 19 of its triples. Its 16 option IRIs keep no triples of their
  own, which leaves 17 dangling `chosen`/`optionSpace` edges.
- `C._validate` conforms (no refusing leg) with and without an escalation added.
- The negative control (`scripts/r301_u2_admission_control.py`) refuses on the `dec` leg when
  `optionSpace` is cut to 1, or when `decidedBy` is removed. So the conforming verdict came from an
  exercised shape: `dec:DecisionHolonShape` (`dec-shapes.ttl:15-32`) constrains edges only, and no
  shape targets `dec:Option`.
- **Not run:** whether the 17 dangling edges matter to anything downstream. Nothing checks them.

**U4: measured.**
- `compile.py` imports `document` nowhere. `document.py:111-112` imports `compile` at top level.
- A top-level `from .document import …` in `compile.py` raised `ImportError` (circular), measured
  on a scratch copy. A function-local import is safe.
- `_verdict_decision` and `_effective_verdict` (`document.py:1113`, `:1128`) depend only on rdflib
  and `DEC`. `decisionlog.py` imports nothing intra-package and already defines `DEC`
  (`decisionlog.py:16-21`), so it is a cycle-free home.
- Two tests reach them through `document` (`tests/etkl/test_section_repair.py:488,493`), so a move
  needs a re-export.

**M-items: the seams the plan cites.**
- **M1, the select.**
  - `tab:RuleSeparatedInkShape` is at `vocab/shapes/tab-shapes.ttl:597-616`, with a `sh:select`
    on a blank-node `sh:sparql`.
  - **No `src/` code reads any `sh:select`.** The only reader is the test-only
    `_runnable`/`_prefix_header` (`tests/etkl/test_vacuity_registry.py:305-317`, which rewrites
    `$this`→`?this`).
  - Cell→owner goes through `tab:hasCell`|`tab:hasDataCell`, the same two predicates as
    `ruleink._CELL_PREDS` (`ruleink.py:18`).
- **M2, escalation.**
  - `holon.escalate_region(g, cand_uri, doc_uri, ascii_text, reason, anchor, confidence, page)`
    is at `holon.py:557`.
  - `RULE_SEPARATED_INK` is in no enum, `sh:in` or table. `_suggester_uri` (`holon.py:538`)
    derives `urn:iladub:suggester/rule-separated-ink-rule` from the string.
  - The `0.0` precedent is at `holon.py:164-167` (it cites `DATAGRID_RESIDUE`, `compile.py:2140`).
- **M3, the ledger.**
  - `build_ledger` is at `adoption.py:43-120`.
  - Coverage is coordinate-based: `band.top <= line.top <= band.bottom`. `Band.lines` are `Line`
    objects, not `_lines` indices.
  - `touched` ranges over `range(len(bands))`, while `booked_bands` ranges over `reports`. That
    asymmetry is G3.
  - Call sites: `compile.py:2030`, `:2127`, `scripts/ledger_contract_census.py:44`, and 11 in
    `tests/etkl/test_adoption_ledger.py` (doubles `_B`, `_R` and `_L`, with no `table_uri`).
- **M4, appended text.** `roundtrip.render_ascii(band: Band, width=80)` (`roundtrip.py:137`)
  takes a `Band`, not line indices, so the spec § 2.4(d) remedy needs a `Band` built over the
  grid's lines. The plan names that seam.
- **M5, the driver.**
  - Adoption is called at `document.py:1786-1792`. The outcome is inferred at `:1800-1821`:
    `grid_idx = len(pages[p].regions)`, then the "no data grid region" note, then "superseded no
    escalated band", then § 1g at `:1844-1865`.
  - **The band count is already in hand:** `band_lists[p] = page_bands(pdf_path, p)`
    (`document.py:1492`, `:1509-1510`), with the same arguments the adoption re-compile uses.
  - Driver `compile_tables` calls: `:1543` (pass 1), `:1606` (section repair) and `:1787`
    (adoption).
  - `DocumentReport.notes` are appended at `:1640`, `:1667`, `:1750`, `:1808`, `:1820` and
    `:1864`.
- **M6, constructors.**
  - `RegionReport(` has 23 calls in `compile.py` and 1 in `tests/etkl/test_printed_total.py:573`.
    All pass six fields positionally.
  - `CompilationReport(` has 1 call in `src` (`compile.py:2203`), positional.
  - A new defaulted field appended last breaks neither class.
- **M7, a test that flips by design.**
  - `tests/etkl/test_header_stack.py:214-241` (`spanner_with_space_ruled_pdf`, `fixtures.py:1058`)
    asserts that `compile_tables(pdf)` raises `MembraneRefusal` "rule-separated ink".
  - Under the guard it escalates instead. That is the spec's "feed the shape's fixture to the
    producer: it escalates" pin, so the test is **rewritten**, not deleted.
  - O3's bypass fixture already exists in `tests/test_rule_separated_ink.py:31-52`.
- **M8, held-out gating.**
  - `held-out/` is gitignored (`.gitignore:55`), and no test compiles fed-h41.
  - Skip idiom: `tests/test_corpus_stem.py:8-14` (`pytest.mark.corpus`, plus `skipif` on the
    file).
  - The marker is registered at `pyproject.toml:100`.
- **M9, admission.**
  - `{t}-admission` is minted only by `datagrid.emit_data_grid` (`datagrid.py:687`, `:765-819`).
    It carries type, `chosen`, `optionSpace` and `decidedBy`. On the fallback path it has **none**
    of `dec:regarding`, `dec:order`, `rdfs:label` or `dec:rationale`; the driver adds those only
    at adoption (`document.py:1933-1945`).
  - Band tables mint no `-admission`: their chain head is the `verdict` judgement.
  - `effective-chain.rq` reaches a refusal that supersedes such an admission through its branch B
    (measured on a synthetic).

## 2. Where the primaries are

- The spec: `docs/superpowers/specs/2026-10-08-r301-producer-guard-design.md` (PR #322).
- The probes, committed here, which read no hidden state:
  - `scripts/r301_u1_ledger_probe.py` (`i2|stock`). It execs an in-memory copy of
    `compile_tables` with two hooks and edits no source.
  - `scripts/r301_u2_admission_probe.py` and `scripts/r301_u2_admission_control.py`.
  - Their outputs are not committed. Re-run them; each takes under 10 s.
- The predecessors: `2026-10-08-r301-guard-position-handoff.md` (G1–G4) and
  `2026-10-08-r301-guard-prototype-handoff.md` (F2–F7).

## 3. What was decided

Nothing at the time of writing; S1–S3 were proposals.

**RULED later the same day:** the maintainer accepted all three proposed remedies in chat on
2026-10-08. They are recorded in the spec's § 8 addendum (`8fa08fc`, on PR #322's branch),
which overrides the spec sentences they amend. § 5 item 1 is therefore done. **The next action
is § 5 item 2:** write the plan in a fresh session, from spec §§ 2–8 and § 1 of this file.
§ 8's `dec:order = 0` for an admission head is flagged there as the plan's interpretation, not
a ruling.

## 4. Unverified

- S1's sweep was shown by string test, not by a page that has two grids and one of them refused.
  The corpus has no such page (spec § 7).
- U2 ran on p7 only. p5's extent (113 triples, 6 blank nodes) was measured by the prototype, not
  re-run with the § 2.2 root exclusion.
- The I2 prototype's join (appended region k covers fallback grid k's `rows`) was run on p7 only.
  O5 across the corpus is untested.
- O4, the guard being the identity on the other 10 documents, is still inferred (spec U3).
