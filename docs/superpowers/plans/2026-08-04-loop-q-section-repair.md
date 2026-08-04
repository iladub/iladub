# Loop Q — Section Repair, Stitching, Key Attribution, Naming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CBH compiles end-to-end — sections repaired at section scope (spec §4.0), stitched into one logical table (§4.1), rows carrying their port keys (§4.2), the denormalized column name recovered by the cascade (§4.3) against a CBH demo contract (§4.4) — with the GrainCorp stem pinned byte-exact throughout; closes R42 (both gaps).

**Architecture:** The repair lives in `compile_document`'s driver, strictly ordered AFTER band-level compile and document carriage (spec §4.0): still-escalated ruled bands with intra-page repetition (verbatim raw grid-line identity + agreeing interior-rule sets — an AXIOM over author marks and raw text) are re-compiled as candidates with loop P's peel+weld (ink-witness interior, resurrected from reverted `b515283`, reachable ONLY via the repair flag), disposed by the existing region membrane — monotone by construction. Stitching generalizes loop M's chain assembly intra-page; per-section totals associate by loop-H exact arithmetic; key attribution injects section captions as candidate concepts (loop K's injection pattern) and the naming cascade (explicit-naming AXIOM → unique-admitting-contract-field AXIOM → BAML pick-among-verified/quarantine) resolves the column name.

**Tech Stack:** Python 3 (`.venv`), rdflib SPARQL, pySHACL membrane, BAML (Fake proposer injected; live behind BAML_LIVE), reportlab fixtures, pytest.

**Doc impact:** increment — the dimension-split wiki entry (spec header's expectation) + loop-Q exemplars entries; no contradiction.

## Global Constraints

- **Branch situation:** work on `loop-q-section-repair`, stacked on UNMERGED `loop-p-grid-region` (13 commits; contains the peel/weld machinery + the loop-P docs). Never rebase or touch the loop-P commits. `/opt/homebrew/bin/git` (or `export PATH="/opt/homebrew/bin:$PATH"`) for every git command — system git is broken this session.
- **§8 gate:** recognition + repair-scope decisions are AXIOMs (SPARQL over evidence graphs, zero numeric literals — geometry emitted as facts); the two-pass driver glue, Decimal arithmetic, and BAML wiring are justified PROCEDURAL (say so in docstrings); constraint side (membrane disposal) reuses the shipped shapes. Confidence never promotes; every grounded node behind exactly one `iladub:PromotionDecision`.
- **Monotonicity is load-bearing and test-pinned:** the repair may only turn escalations into membrane-passing assertions. A band that asserts in pass 1 is NEVER re-read; a candidate whose re-reading fails the membrane stays escalated with its pass-1 report. The stem-shaped fixture must traverse the driver with ZERO repair activity, and the real stem must re-measure EXACTLY **0.9655 / 2152 / 133 records / 585 grounded / 1265 quarantined, chains [3]**. Any drift = STOP-and-report.
- **Honest failure (§7):** unrecognized/unconfirmed sections stay escalated; a total that does not arithmetically confirm refuses association (recorded as a fact); non-member markers quarantine; nothing fabricated for coverage.
- Baselines at branch base (`loop-p-grid-region` head 4b54e64): non-corpus 840 passed / 5 skipped (+1 machine-local scrubbed-env release-gate failure, environmental); `tests/etkl/` 493/493; corpus battery: stem exact, CBH 0.0698 honest-inert, apple deliberately red (R41, unrelated — must stay red).
- Canonical tests: `./.venv/bin/python -m pytest`, FOREGROUND only, never backgrounded; controller runs full suites and all `-m corpus` batteries.
- Commit trailer: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- **Salvage rule:** the ink-witness implementation, `line-enclosed` interplay, and their unit tests exist in reverted commit `b515283` — resurrect content with `/opt/homebrew/bin/git show b515283:<path>` instead of rewriting from scratch; every resurrected piece must land behind the repair flag only (the default band path stays byte-identical — that is what the revert protected).

## File Structure

| File | Responsibility |
|---|---|
| `tests/etkl/fixtures.py` (modify) | `multi_section_ruled_pdf(path, n_sections=2, with_totals=True)` — the CBH page shape: N sections (heading + notice strips, identical wrapped-header grids, data rows) with per-section total lines between them; reuses `sectioned_ruled_table_pdf`'s drawing internals. |
| `tests/etkl/test_section_repair.py` (create) | Loop battery: red E2E pins, recognition units, monotonicity pins (stem-shaped), totals association, attribution, cascade. |
| `src/iladub/etkl/sectiongraph.py` (create) | PROCEDURAL layer of the recognition AXIOM: evidence graph of still-escalated ruled bands (raw grid-region line texts, interior-rule x-sets), runs the query, returns candidate section groups. |
| `vocab/queries/section-repeat.rq` (create) | Intra-page repetition derivation (open world; the page is the closure boundary). |
| `vocab/queries/grid-region-ink.rq` (create, salvaged) | The ink-witness interior derivation (from `b515283`'s grid-region.rq), used ONLY by the repair path. |
| `src/iladub/etkl/gridregion.py` (modify) | `grid_lines(band, rules, *, ink_witness=False)` — repair-scoped variant + salvaged ink-fact emission. |
| `src/iladub/etkl/compile.py` (modify) | `compile_tables(..., section_repair_bands: frozenset[int] | None = None)` — those band indices build with ink-witness peel + weld; None = byte-identical. |
| `src/iladub/etkl/document.py` (modify) | Driver step 3: recognition over still-escalated bands → pass-2 re-compile with `section_repair_bands` → monotone adoption; intra-page chain links; totals association; section keys into the graph. |
| `vocab/ontology/tab.ttl` (modify) | Owned terms for section evidence/keys (grep-first, only missing; versionInfo bump). |
| `src/iladub/feed.py` (modify) | Section-key candidate injection into the section's records (imitate loop K's injected-keys path). |
| `baml_src/` + `src/iladub/propose_ground.py` (modify) | `ProposeSplitKeyName` (markers + context sketch → scored candidates) + Fake proposer for tests. |
| `examples/shipping/cbh-*.ttl` (create) | CBH demo contract/terms/shapes: `port` field with WA-ports scheme (§4.4; illustrative, example.org). |
| Docs (Task 7) | R42 close, spec status notes, exemplars, dimension-split wiki page + index. |

---

### Task 1: Fixtures + red pins

**Files:**
- Modify: `tests/etkl/fixtures.py`
- Test: `tests/etkl/test_section_repair.py`

**Interfaces:**
- Produces: `multi_section_ruled_pdf(path, n_sections=2, with_totals=True) -> dict` with keys `sections` (list of `{"key": str, "notice": str, "rows": [...], "total": str}`), `header_names`, `cols`. Section keys: `"GERALDTON"`, `"KWINANA"` (n=2). Every later task imports it.

- [ ] **Step 1:** Build `multi_section_ruled_pdf` by refactoring `sectioned_ruled_table_pdf`'s body into a parameterized `_draw_section(c, y_off, key, notice, rows, truth)` helper both builders call, plus per-section total lines (`with_totals=True`). **CORRECTION (measured at first dispatch):** the multi-section fixture MUST carry the real CBH's DOUBLED-EDGE geometry — a twin outer border ~0.3 pt beside the first and hrules starting ~0.5 pt inside (salvage the exact deltas from the wave: `/opt/homebrew/bin/git show b515283 -- tests/etkl/fixtures.py`) — so its sections ESCALATE at band level exactly like the specimen (clean edges let loop P's band-level peel/weld assert them at 1.0, which is a different, valid path that needs no repair). Verify by compile probe: every section band escalates. Keep `sectioned_ruled_table_pdf` itself byte-identical (its clean-edged, band-level-asserting behavior is the loop-P pin AND the future clean-edge stitching case).
- [ ] **Step 2:** Red E2E pins in `tests/etkl/test_section_repair.py` (assert the CORRECT end state; RED now):

```python
"""Loop Q (spec 2026-08-04 §4.0-§4.2): section repair, stitching, key attribution."""
import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("reportlab")

from rdflib import RDF

from iladub.etkl.document import compile_document
from iladub.etkl.holon import TAB
from tests.etkl.fixtures import multi_section_ruled_pdf, stem_shaped_ruled_table_pdf


def test_sections_repair_and_stitch(tmp_path):
    """RED until Tasks 2-4: both sections escalate at band level (loop P machinery is
    inert by default), the driver's section repair re-reads them, the membrane admits
    the readings, and the chain links them into ONE logical table."""
    pdf = tmp_path / "multi.pdf"
    truth = multi_section_ruled_pdf(str(pdf))
    rep = compile_document(str(pdf))
    page = rep.pages[0]
    asserted = [r for r in page.regions if r.verdict == "asserted"]
    assert len(asserted) >= 2, [(r.kind.name, r.verdict, r.reason) for r in page.regions]
    assert any(len(c) == 2 for c in rep.chains), rep.chains   # the two sections chained
    caps = {str(t) for c in rep.graph.subjects(RDF.type, TAB.RegionCaption)
            for t in rep.graph.objects(c, TAB.captionText)}
    for s in truth["sections"]:
        assert any(s["key"] in c for c in caps), (s["key"], caps)


def test_repair_is_monotone_on_stem_shape(tmp_path):
    """The stem-shaped page must traverse the driver with ZERO repair activity:
    same regions, verdicts, reasons, and graph as a driver without the repair.
    Pins spec §4.0's ordering guarantee structurally."""
    pdf = tmp_path / "stemlike.pdf"
    stem_shaped_ruled_table_pdf(str(pdf))
    rep = compile_document(str(pdf))
    # the stem-shaped single-section page has no intra-page repetition: the repair
    # must not fire — pin via the driver's own record (Task 4 exposes it):
    assert getattr(rep, "repaired_bands", ()) == ()
```

(CORRECTION, verified at plan time: `stem_shaped_ruled_table_pdf` does NOT exist at branch head — it was added in the REVERTED wave commit `6d7aa60`. Task 1 must SALVAGE it: `/opt/homebrew/bin/git show 6d7aa60:tests/etkl/fixtures.py` and copy the stem-shaped builder (furniture line + in-column unruled 2-line header stack above a grid whose interior verticals start below the stack, single-row hrule boxes) into `tests/etkl/fixtures.py`, adapting only if its drawing helpers changed in the final fix wave.)
- [ ] **Step 3:** Run — first test FAILS (sections escalate, no 2-chain), second FAILS (`repaired_bands` attribute missing). Record verdicts verbatim. Commit `test(loop-q): multi-section fixture + red pins`.

---

### Task 2: Intra-page section recognition (AXIOM)

**Files:**
- Create: `src/iladub/etkl/sectiongraph.py`, `vocab/queries/section-repeat.rq`
- Modify: `vocab/ontology/tab.ttl` (grep-first; expected new: `tab:EscalatedBand`, `tab:bandIndex`, `tab:gridLineText`, `tab:gridLineOrder`, `tab:interiorRuleXs` — a canonical space-joined string fact is acceptable for set identity, computed by the emitter)
- Test: `tests/etkl/test_section_repair.py` (units)

**Interfaces:**
- Produces: `section_candidates(bands: Sequence[tuple[int, Band, tuple[Rule, ...]]]) -> tuple[tuple[int, ...], ...]` — groups (≥2 members) of band indices whose RAW grid-region line texts repeat verbatim and whose interior-rule x-sets agree. **Recognition is verdict-independent** (spec §4.0 point 3 as corrected): the caller passes ALL ruled bands of the page; only Task 4 filters which members get re-read (the still-escalated ones) vs pass through (already asserting). Grid-region lines = the band's lines minus the leading enclosed non-grid run (reuse `grid_lines`/`peel_leading_captions` in read-only form to compute WHICH lines, peeling nothing). The header-signature identity is over the grid's LEADING lines up to the first line that differs... NO — keep it evidence-positive and simple: identity over the RAW TEXTS of the grid region's first K lines where K = the leading full-width hrule box's line count (the drawn header box; reuse the box arithmetic). Two bands repeat iff those box texts are verbatim-identical AND their interior-x sets are equal (rounded 2dp).
- The AXIOM (`section-repeat.rq`): zero numeric literals; the emitter provides per-band `tab:headerBoxText` (the box lines joined with `\n`) and `tab:interiorRuleXs`; the query derives pairs sharing both facts; the reader assembles connected groups.

- [ ] **Step 1:** Failing units: two CBH-shaped bands (from `multi_section_ruled_pdf` via `detect_bands`/`segment` + per-band rules, mirroring the driver's band construction) → one group with both indices; a stem-shaped band + a CBH band → no group; a single band → no group.
- [ ] **Step 2:** Implement (emitter facts, literal-free query — include the literal-free unit test in the same shape as loop P's). Run green. Commit `feat(loop-q): intra-page section recognition AXIOM`.

---

### Task 3: The repair flag — ink-witness peel + weld behind `section_repair_bands`

**Files:**
- Create: `vocab/queries/grid-region-ink.rq` (salvage: `/opt/homebrew/bin/git show b515283:vocab/queries/grid-region.rq`)
- Modify: `src/iladub/etkl/gridregion.py` (salvage the ink-fact emission + `interior_rule_xs` from `b515283:src/iladub/etkl/gridregion.py`; expose as `grid_lines(band, rules, *, ink_witness=False)` reading `grid-region-ink.rq` when the flag is set; DEFAULT PATH UNCHANGED — byte-identical imports/behavior)
- Modify: `src/iladub/etkl/compile.py` — `compile_tables(..., section_repair_bands: frozenset[int] | None = None)` threading to `_build_ruled_band(sub, sub_rules, sub_hrules, page_chars, section_repair=False)`: when True, the peel uses `ink_witness=True` (everything else — enclosed guard, leading-prefix, leading-box weld — as shipped).
- Test: `tests/etkl/test_section_repair.py` + resurrect the applicable ink-witness units from `b515283:tests/etkl/test_grid_region.py` INTO the new file (renamed, flag-scoped).

**Interfaces:**
- Consumes: Task 2's groups (the driver passes their indices in Task 4).
- Produces: `section_repair_bands` parameter; `None` byte-identical (pin: compile the loop-P `sectioned_ruled_table_pdf` and the stem-shaped fixture with and without `section_repair_bands=None` — identical reports).

- [ ] **Step 1:** Failing unit: CBH-shaped band built with `section_repair=True` peels its strips (captions non-empty, ink-witness interior defeats the doubled border) while the same band with `False` peels nothing (the shipped inert behavior).
- [ ] **Step 2:** Salvage + implement + green. `tests/etkl/ -q` full family: 0 failed (the flag default preserves everything). Commit `feat(loop-q): repair-scoped ink-witness peel behind section_repair_bands (salvaged b515283)`.

---

### Task 4: Driver step 3 — recognition, pass-2 re-compile, monotone adoption, chains, totals

**Files:**
- Modify: `src/iladub/etkl/document.py`
- Modify: `vocab/ontology/tab.ttl` (`tab:SectionTotal`, `tab:confirmsSection` if missing)
- Test: `tests/etkl/test_section_repair.py`

**Interfaces:**
- Consumes: `section_candidates` (Task 2), `section_repair_bands` (Task 3), loop H's `_numeric_token_sum`/aggregation arithmetic (rows.py), loop M's chain assembly.
- Produces: `DocumentReport.repaired_bands: tuple[tuple[int, int], ...] = ()` (page, band-index pairs adopted); intra-page `tab:continuesTable` between adjacent repaired section tables of one recognized group; per-section total association: the NON-TABLE band strictly between section k's grid and section k+1's header (or page end) whose numeric token-sum EQUALS section k's Volume-column Decimal sum → `tab:SectionTotal` + `tab:confirmsSection` facts (justified PROCEDURAL exact arithmetic + presence; a non-matching total refuses association, recorded by absence + a report note, never guessed).
- Driver order (spec §4.0 as corrected, pinned by Task 1's monotonicity test): existing per-page compile → existing carriage → NEW: per page, `section_candidates` over ALL ruled bands (verdict-independent) → pass-2 `compile_tables(page, section_repair_bands={still-escalated members only}, doc_uri=page_uri)` → adopt a band's pass-2 region IFF it asserts (loop-M page-scoped URI idiom; mint pass-2 URIs under `{page_uri}/r2`; record adoption in `repaired_bands`) → chains link ALL recognized members that assert (band-level-asserted AND repaired alike) → totals.

- [ ] **Step 1:** Failing units: adoption swaps only asserting bands; a group whose pass-2 still escalates leaves everything untouched; `repaired_bands` recorded; totals associate on the fixture (`with_totals=True`) and refuse on a tampered total (build the fixture, then compile a variant with a wrong total value — `multi_section_ruled_pdf` gains an optional `bad_total_in=None` index parameter).
- [ ] **Step 2:** Implement; Task 1's `test_sections_repair_and_stitch` goes GREEN except (possibly) the chain assertion if stitching details lag — finish them in this task; monotonicity pin green. `tests/etkl/ -q`: 0 failed. Commit `feat(loop-q): section repair in the driver — recognition, monotone adoption, intra-page chains, arithmetic totals`.

---

### Task 5: Key attribution — captions as candidate markers, injected into records

**Files:**
- Modify: `src/iladub/feed.py` (imitate loop K's injected-keys path — grep `inject` / the SurfaceConcept key-injection block)
- Modify: `src/iladub/etkl/document.py` (expose each repaired section's captions on its table node — already done via `tab:hasCaption`; ensure they survive adoption)
- Test: `tests/test_feed_section_keys.py` (create — feed tests live at `tests/` top level per the existing feed test files; verify with ls and follow the local convention)

**Interfaces:**
- Produces: for every record of a repaired section table, one additional candidate `SurfaceConcept` per section caption (text = caption text, provenance = the caption node), marked as section-key CANDIDATES (`is_section_marker=True` on the SurfaceConcept or a parallel structure — follow loop K's injection shape). Attribution never waits for naming (§4.2): record identities gain the section discriminator (first caption text, positionally, the loop-I value-without-name idiom) so two sections' row r0 stay distinct.
- The DISCRIMINATION of key-vs-notice among captions is NOT decided here — §4.3's cascade does it via scheme membership (a notice grounds nowhere; `GERALDTON` grounds in scheme-port). Feed injects ALL captions as candidates; §7 keeps the non-members quarantined.

- [ ] **Step 1:** Failing tests: records of section 0 carry `GERALDTON` and the notice as candidate concepts with caption provenance; identities `GERALDTON > r0` vs `KWINANA > r0` distinct; a non-repaired table's records unchanged (byte-identity pin on an existing feed fixture).
- [ ] **Step 2:** Implement + green + `tests/ -q -k "feed"` no regression. Commit `feat(loop-q): section captions injected as candidate key concepts (loop K pattern)`.

---

### Task 6: The naming cascade + BAML + CBH demo contract

**Files:**
- Create: `examples/shipping/cbh-contract.ttl`, `cbh-terms.ttl`, `cbh-shapes.ttl` (imitate the stem trio; `port` field, admissibleScheme = WA public ports: Geraldton, Kwinana, Albany, Esperance, Bunbury; a second field `commodity` with its scheme so the negative pick-among-verified test can be constructed against a doctored terms file)
- Modify: `src/iladub/ground.py` or a new `src/iladub/splitkey.py` (the cascade; follow ground.py's structure), `src/iladub/propose_ground.py` (+ `baml_src/split_key_name.baml`): `ProposeSplitKeyName(markers: list[str], context: str) -> list[ScoredKeyCandidate]`, Fake proposer injected in tests, live path behind the existing BAML_LIVE gating idiom
- Test: `tests/test_split_key_naming.py`

**Interfaces:**
- Produces: `resolve_split_key_name(markers, contract, terms, proposer, graph) -> KeyNameResolution` implementing spec §4.3 verbatim:
  1. explicit-naming AXIOM (a `<Name>: <Value>` split-marker form names the dimension; CBH fails it — test with a synthetic marker list `["Port: GERALDTON", ...]`);
  2. unique-admitting-field AXIOM: whole-set scheme membership; ambiguity score = count of admitting fields; exactly 1 → name derived from the contract, asserted via `iladub:PromotionDecision` recording the membership evidence;
  3. BAML: ≥2 admitting → proposer picks among the VERIFIED candidates (winner asserts); 0 admitting → top proposal stays a quarantined `iladub:CandidateConcept` with score + suggested anchor (never asserts on confidence).
  Partial membership abstains step 2 to step 3; non-member markers quarantine as values regardless.
- [ ] **Step 1:** Failing tests, one per cascade arm: unique-admitting asserts `port` with a promotion decision (markers = the four WA ports vs cbh-contract); explicit-naming short-circuits; two-admitting → Fake proposer's pick among the two verified asserts; zero-admitting → CandidateConcept quarantined, nothing asserted; every grounded node exactly one `wasPromotedBy`.
- [ ] **Step 2:** Implement + green. Commit `feat(loop-q): split-key naming cascade + ProposeSplitKeyName + CBH demo contract`.

---

### Task 7: CBH end-to-end, measurement, docs close

**Files:**
- Modify: `tests/corpus-manifest.ttl` — ONLY to add `cor:contract/terms/shapes` (the cbh trio) to the CBH entry (the membrane's all-or-none rule); NO verdict change — François adjudicates.
- Docs: `docs/superpowers/residues.md` (R42 close or narrowing — per measurement; R47 revisit — the totals now read), spec status note, `docs/wiki/concepts/neurosymbolic-exemplars.md` entries, NEW `docs/wiki/concepts/dimension-split.md` + index line, plan status note.

- [x] **Step 1 (controller runs the batteries):** CBH through `compile_document` + grounding: measure score (from 0.0698), sections asserted, chain, records-with-keys, name resolution (`port` asserted via the cascade), quarantine tallies. STEM: exact-pin re-measure. Full non-corpus suite. Record everything verbatim.
- [x] **Step 2:** Docs per measurement — R42 closes ONLY for what actually measured (if any face stays open, narrow honestly); dimension-split wiki page (proposition, sources, confidence); exemplars entries (recognition AXIOM, repair monotonicity, cascade). Doc gates green.
- [x] **Step 3:** ONE docs commit; then the controller runs the final whole-branch review and the finishing flow.

**Status (loop close, 2026-08-04):** Task 7 shipped `tests/test_cbh_e2e.py` — one
module-scoped `compile_document` over the real CBH stem composing structural,
grounding, and cascade assertions in a single measured pass. Measured: score
0.0698 → **0.9047** (0.9046563192904656, floor pinned at 0.90 per convention, never
the measured value); `repaired_bands = ((0,1),(0,3),(0,5),(0,7))` (all 4 escalated
sections repaired and adopted); chains **[4, 1]**; grounding records=58 grounded=134
still-quarantined=775, every `GroundedNode` exactly one `wasPromotedBy`; 49
section-prefixed records distinct across GERALDTON/KWINANA/ALBANY/ESPERANCE; the
naming cascade resolves `port` via the unique-admitting-field AXIOM arm
(`ambiguity_score=1`, one `iladub:PromotionDecision`, no LLM call). `tests/
corpus-manifest.ttl`'s CBH entry gained the `cor:contract`/`cor:terms`/`cor:shapes`
trio (verdict unchanged — François adjudicates). `docs/superpowers/residues.md`:
R42 closed (both gaps, per measurement) as `~~R42~~`; R47 updated (stale
"unexercised" claim corrected — Task 4's adjacent total-confirmation oracle WAS run
on the real document and measured zero `tab:SectionTotal` facts, still open); R48
reviewed, unchanged (accurate); four new residues registered: R50 (totals oracle
LAST-row-only scope), R51 (`_band_subgraph`'s URI-prefix licence coupling), R52
(class-level `.ttl` example debt for `DetectedAggregationRow`/`continuesTable`/
`SectionTotal`), R53 (`GroundedNodeShape` validates `groundsTo` presence, not
resolution — the leak itself is fixed, the membrane gap is not). New wiki page
`docs/wiki/concepts/dimension-split.md` + index line; `neurosymbolic-exemplars.md`
gained a Loop Q section. Full report:
`.superpowers/sdd/2026-08-04-loop-q-section-repair/task-7-report.md`.

---

## Self-review (done at plan time)

- **Spec coverage:** §4.0 → Tasks 2–4 (recognition, flag, driver order + monotone adoption); §4.1 → Task 4 (chains + arithmetic totals); §4.2 → Task 5 (attribution never waits, provenance, notices carried); §4.3 → Task 6 (three arms + partial-membership abstain); §4.4 → Task 6 contract trio + negative fixtures; DoD → Task 7. Loop P interplay: default paths byte-identical (Task 3 pin), monotonicity (Task 1 pin), salvage rule keeps the revert honest (resurrected code reachable only via the flag).
- **Known risks, stated:** (a) Task 4 is the heaviest — adoption/URI-patching in the driver; the loop-M page-scoped idiom is the named pattern, and the monotonicity + byte-identity pins are the safety net; if adoption proves too invasive, the honest fallback is assembling pass-2 as a SEPARATE page compile whose asserted section tables are added alongside pass-1's escalation records (additive, no swap) — permitted, but the escalation records must then carry `tab:repairedBy` pointers so nothing double-counts; decide by measurement, record in the task report. (b) `stem_shaped_ruled_table_pdf` does not exist at branch head (reverted with the wave) — Task 1 salvages it from `6d7aa60` (see the Task-1 CORRECTION note). (c) feed test-file location convention verified by ls in Task 5. (d) CBH page count is 1 in the manifest — cross-page section chains are OUT of scope; if the real document later ships multi-page, that is a new residue.
- **Type consistency:** `section_candidates` returns index groups consumed by Task 4; `section_repair_bands: frozenset[int] | None` consistent across compile/document; `grid_lines(..., ink_witness=False)` keyword-only; `KeyNameResolution` produced/consumed within Task 6 only.
