# Evidence — R261 loop (b), Task 0: baseline and seams (2026-10-02)

**Serves:** prog:criterion:etkl:03 — ag-trade/cbh-stem-2026-08-03.pdf: this document compiles via
`compile_document` to `cor:CompilesAbove` with a pinned `cor:scoreFloor`, under a `cor:adjudication`
whose rationale accepts that score — not one that holds it. Loop (b) is attempting to bind cbh's
grand total `1,951,264` as a total-of-totals `PrintedTotal`.

**Topic:** r261-totals-family · **Date:** 2026-10-02 · **Branch:** `r261-grand-total` · **HEAD
measured:** `019b0ed`.

**Doc impact: none.** Measurement only; no `src/` change, no vocabulary or published term changes.

Plan: `docs/superpowers/plans/2026-10-02-r261-grand-total.md` (§§ "Measured seams", "Decisions
this plan takes where the spec is silent"). Task brief: plan Task 0.

This task is MEASUREMENT ONLY: no `src/` change. Three scratch scripts were written and run from
the scratchpad directory (not committed, per the prior loop's § 3 convention — a diagnostic over a
committed compile, not a committed instrument itself): `r261_task0_d1_cbh.py`,
`r261_task0_d1_fixture.py`, `r261_task0_step4_box_sources.py`.

---

## § 0. Step 1 — whole-corpus canonical-hash baseline (Task 7's "before")

Instrument: `scripts/r261_baseline.py --baseline` (unmodified, same instrument the loop (a)
evidence used), run serially, nothing else compiling at the same time.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python scripts/r261_baseline.py --baseline
```

Output:

| document | score | triples | sha256(canonical NT) |
|---|---|---|---|
| cbh-stem-2026-08-03 | 0.9106957424714434 | 13624 | `8ab724dd0efb124ff22f70ad2829800e0f85ca09dcab5accf2ac9affc2bd479e` |
| graincorp-capacity-2026-08-04 | 1.0 | 5859 | `4a7ffe8598fdb5d2b69f8e98cb228f85ea254132a62c2565ff4b1f0532984f68` |
| graincorp-stem-2026-07-31 | 0.9995511669658886 | 32422 | `96436660c468a30fc92a7c14af95e8d25dc4dd1bf8b71054c7dc1e616bb3375f` |
| apple-fy2026q3-statements | 0.9418604651162791 | 6255 | `f8c56e57e59947631d27def1caedaf6591683965af67abbd9dd3e01aeaee8bfc` |
| bfs-population-bilan-2023 | 0.9021428571428571 | 16778 | `4a176ec3138f99cbcd61db4c736a4fb834ba226e2d6e0aeea5d1616c358a225a` |
| ons-index-of-services-2026-02 | 0.8684895833333334 | 12454 | `4847d19fbd326488078653dbe1373d6f4d9634359b869f8b77eb6c319b336c08` |
| who-wfa-boys-zscore-0-5 | 0.9962779156327544 | 12274 | `7931db4b52d368bf32338c5e6773e3c47f79e33919b948e6ea2dd8c7fe41ea18` |

**Byte-identical to loop (a)'s own "after" baseline** (`docs/superpowers/2026-10-01-r261-totals-family-evidence.md`
§ 7.1, measured at `8cf306e`): every score, triple count and sha256 matches across all 7 rows. The
corpus has not moved between loop (a)'s close and this loop's Task 0 — the correct "before" for
this loop's Task 7 C2 diff is therefore identical to loop (a)'s "after".

---

## § 0.1 D1 on cbh's r2 pass (Step 2)

D1 (plan § "Decisions", `D1`): an operand's table band is the unique `j` with
`reports[j].table_uri == t`, where `t` is the operand `PrintedTotal`'s `tab:totalOf` object. Zero
or several such `j` ⇒ no claim (mirrors ruling R3).

**Instrument:** `r261_task0_d1_cbh.py` (scratchpad, not committed). Monkeypatches
`iladub.etkl.document.compile_tables` — the **module-level name** `document.py` binds via `from
.compile import compile_tables` (measured: `src/iladub/etkl/document.py:111`), not
`iladub.etkl.compile.compile_tables` itself, since patching the latter would not reach
`document.py`'s already-bound reference — to capture the one call whose `doc_uri` ends in `/r2`
for page 0 (the section-repair pass-2 compile Loop Q runs, `document.py:1579-1584`). Then runs the
whole `compile_document` with the **recorded readers** (`BAML_LIVE` and `ILADUB_RECORD_READINGS`
both unset — no API calls; the recorded JSON files under `readings/printed_total/` already cover
cbh's four port totals). Over the captured `CompilationReport`: for every `(pt, t)` in
`g2.subject_objects(TAB.totalOf)`, lists every `j` with `rep2.regions[j].table_uri == t`.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python \
  /private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/001554b5-6d54-4e42-831b-fe6ba897a981/scratchpad/r261_task0_d1_cbh.py
```

Output (full `rep2.regions` dump, then the four pairs):

```
captured r2 compile_tables call, doc_uri=https://example.org/etkl/doc/p0/r2
rep2.regions: 12 bands
  band 0: kind=RegionKind.NON_TABLE verdict=ignored table_uri=None
  band 1: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable1
  band 2: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 3: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable3
  band 4: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 5: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable5
  band 6: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 7: kind=RegionKind.UNSUPPORTED_TABLE verdict=asserted table_uri=.../r2#htable7
  band 8: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 9: kind=RegionKind.UNSUPPORTED_TABLE verdict=escalated table_uri=None
  band 10: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=.../r2#table10
  band 11: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=.../r2#table11

4 tab:PrintedTotal -> tab:totalOf pairs in rep2.graph
  #printedtotal2-l0 (cellText=374,904) -> totalOf #htable1 -> j=[1]
  #printedtotal4-l0 (cellText=737,289) -> totalOf #htable3 -> j=[3]
  #printedtotal6-l0 (cellText=660,363) -> totalOf #htable5 -> j=[5]
  #printedtotal8-l0 (cellText=178,708) -> totalOf #htable7 -> j=[7]
```

**Result: exactly one `j` each, `{1, 3, 5, 7}` — matches the brief's expectation exactly.** D1
needs no review before Task 4 on this corpus.

---

## § 0.2 D1 on the fixture (Step 3)

Same measurement over `tests.etkl.fixtures.printed_total_pdf` with an **always-yes table-level
reader** (`iladub.etkl.printedtotal.default_reader` monkeypatched to a reader whose `ask` always
returns `PrintedTotalReading(answer="yes")`, mirroring `tests/etkl/test_printed_total.py`'s
`_Reader`/`_compile` pattern — no network touched, no `BAML_LIVE`/`ILADUB_RECORD_READINGS`/
`ANTHROPIC_API_KEY` needed since the reader is fully faked). The fixture is a single page, so this
calls `compile_tables(pdf_path, 0, validate_shapes=False)` directly — no `compile_document`/Loop Q
needed (table and band index coincide here; no grid-donation path is exercised).

**Instrument:** `r261_task0_d1_fixture.py` (scratchpad, not committed).

```
PYTHONPATH="$PWD" .venv/bin/python \
  /private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/001554b5-6d54-4e42-831b-fe6ba897a981/scratchpad/r261_task0_d1_fixture.py
```

Output:

```
rep.regions: 5 bands
  band 0: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=#table0
  band 1: kind=RegionKind.UNSUPPORTED_TABLE verdict=escalated table_uri=None
  band 2: kind=RegionKind.RECORD_TABLE verdict=asserted table_uri=#table2
  band 3: kind=RegionKind.NON_TABLE verdict=asserted table_uri=None
  band 4: kind=RegionKind.NON_TABLE verdict=ignored table_uri=None

2 tab:PrintedTotal -> tab:totalOf pairs
  #printedtotal1-l0 (cellText=5,100) -> totalOf #table0 -> j=[0]
  #printedtotal3-l0 (cellText=2,700) -> totalOf #table2 -> j=[2]
```

**Result: `#table0 → 0`, `#table2 → 2` — matches the brief's expectation exactly.** The
grand-total line (`7,800`, band 4) never produces a `PrintedTotal` here (total-of-totals binding
was dropped by controller ruling R4 in loop (a); band 4 is `ignored`, carrying no claim), so only
the two table-level totals appear in the `tab:totalOf` pairs, as expected.

---

## § 0.3 Step 4 — does a port-total word supply an extremal coordinate of the probe's derived box?

**Instrument:** `r261_task0_step4_box_sources.py` (scratchpad, not committed; `scripts/
r261_grand_total_role_probe.py` is evidence and was not amended, per the plan's N11). Re-implements
`derived_box` (`scripts/r261_grand_total_role_probe.py:71-94`) line-for-line, additionally tagging
every word (and each operand table band's `.top`, each total line's `.bottom`) with its origin —
one of the four port-total table bands, one of the four port-total lines themselves, or the
grand-total line — then reports, for each of x0/y0/x1/y1, which origin supplies the raw (pre
±4 pt padding, pre page-clamp) extremal value. No API call: the script exits right after printing
the box and its sources.

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python \
  /private/tmp/claude-501/-Volumes-WD-Green-dev-git-iladub/001554b5-6d54-4e42-831b-fe6ba897a981/scratchpad/r261_task0_step4_box_sources.py
```

Output:

```
operand 374,904: table band 1, 13 lines
operand 737,289: table band 3, 19 lines
operand 660,363: table band 5, 17 lines
operand 178,708: table band 7, 8 lines

--- derived box (post +/-4pt padding, page-clamped): [45.68, 101.44, 1147.886, 693.46] ---
  x0: raw=49.68 supplied by: table band 1 (operand 374,904's table), word 'VNA #'
  y0: raw=105.43999999999994 supplied by: table band 1 (operand 374,904's table) .top
  x1: raw=1143.8860000000002 supplied by: table band 1 (operand 374,904's table), word 'Time Loading'
  y1: raw=689.4599999999999 supplied by: grand-total line '1,951,264' .bottom
```

**Finding: no extremal coordinate is supplied by a port-total word (a port-total's own line).**
All three of x0/y0/x1 come from **table band 1's own cell words** (the first operand's table —
`#htable1`, un-carved, its own full-precision pdfplumber word geometry) and y1 comes from the
**grand-total line's own word** (`1,951,264`, not a `PrintedTotal` in production per loop (a)'s
ruling R4 — it stays an escalated band, so its extent is never passed through N4's 2 dp rounding
either). None of the four port-total LINES (`374,904`/`737,289`/`660,363`/`178,708` themselves, as
opposed to their table bands) supplies any of the four extremal coordinates.

**Consequence for Task 6 Step 3 (recorded per the brief, as a finding — not a tolerance).** N4
(plan § "Measured seams") observes that an operand total band is carved by the time the grand
total is reached, so its extent survives in production only via its `PrintedTotal`'s
`tab:hasBBox`, rounded to 2 dp (`holon.py:684-690`, `Decimal(str(round(word.x0, 2)))`) — a
potential < 0.01 pt divergence between the probe's full-precision box and a production box built
from rounded bboxes, **if** a port-total word supplied an extremal coordinate. **It measurably does
not, for cbh's current geometry**: the box's bounds are pinned by band 1's own (un-carved,
full-precision) table-cell words on three sides and by the grand-total line's own (also
full-precision — it is never emitted as a `PrintedTotal`, so N4's rounding never touches it) word
on the fourth. **The 2 dp-rounding concern N4 raises is therefore moot for Task 6's crop on this
document**: a production box built the same way (operand table bands' words + the grand-total
line, no port-total `PrintedTotal` bboxes contributing an extremal corner) would coincide with the
probe's box exactly, not merely to within 0.01 pt. This is recorded here as the measured fact
Task 6 Step 3 should re-check against its own production-box construction, not assumed to
generalize to a different document's geometry.

---

## § 0.4 Commands run, in order (corpus-runs-are-serial; checked clear before each)

```
# Step 1
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python scripts/r261_baseline.py --baseline

# Step 3 (fixture — no corpus compile, run first since it carries no corpus-serial constraint)
PYTHONPATH="$PWD" .venv/bin/python <scratchpad>/r261_task0_d1_fixture.py

# Step 2 (cbh r2 pass — corpus compile, run alone)
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python <scratchpad>/r261_task0_d1_cbh.py

# Step 4 (derived-box sources — single compile, run alone)
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python <scratchpad>/r261_task0_step4_box_sources.py
```

`pgrep -fl "compile_document\|r261_"` was checked clear immediately before Steps 2 and 4; macOS has
no `timeout` and none was used. `BAML_LIVE` and `ILADUB_RECORD_READINGS` were unset throughout
(confirmed by the `env -u` prefix on every corpus-touching command); Step 3's fixture reader is
fully faked, so no `ANTHROPIC_API_KEY` was read or needed for any command in this task — no API
call was made.

---

## § 0.5 Concerns for Task 4 review

None. Both D1 checks (cbh, the fixture) produced exactly the expected mapping with no ties, no
misses, and no second finding beyond the box-source observation in § 0.3, which is itself scoped
and handed to Task 6 Step 3 as instructed, not treated as a defect in D1 or in this task.

---

## § 1. Task 1 — does `AskTotalRole` through BAML reproduce P4b? (2026-10-02)

**Serves:** prog:criterion:etkl:03 — plan Task 1
(`docs/superpowers/plans/2026-10-02-r261-grand-total.md`): a PROPOSITION, run before any spec.

**Built:** `baml_src/total_role.baml` — `enum TotalRoleAnswer`, `class TotalRoleVerdict`, `function
AskTotalRole(page: image, value: string) -> TotalRoleVerdict`, client `Claude`. The prompt is
`scripts/r261_grand_total_role_probe.py`'s `PROMPT` (N8's wording) verbatim, with `{value}` →
`{{ value }}` and the literal `Reply with JSON only: {...}` line replaced by `{{ ctx.output_format
}}` — the same translation `printed_total.baml` applied to P1's wording. Generated with
`.venv/bin/baml-cli generate --from baml_src` (14 files written to `baml_client/`, which is
gitignored and regenerated by CI — `.github/workflows/ci.yml:22-24` — so only the `.baml` source is
committed, matching every other BAML function in this repo).

**Probe change (Step 2):** `scripts/r261_grand_total_role_probe.py` gained `VIA` (default `http`,
byte-identical to before — unchanged code path, unchanged call signature on that path) and
`VIA=baml`, which calls `sync_client.b.AskTotalRole(Image.from_base64("image/png", ...), value)`
(same pattern as `printedtotal.py`'s `BamlPrintedTotalReader`) instead of the raw HTTP request.

**Defect found and fixed before the recorded run:** the generated `TotalRoleAnswer(str, Enum)`
member *values* are the uppercase NAMES (`baml_client/types.py`: `TABLE_TOTAL = "TABLE_TOTAL"`,
etc.) — the `@alias("table_total")` only governs how the enum is rendered into the prompt and
parsed from the model's JSON text, not the Python enum's `.value`. A first run compared
`r.answer.value` directly against `ALLOWED` (`("table_total", ...)`) and every one of the 18 asks
came back `UNPARSED` despite the BAML debug log showing correct parses (`TOTAL_OF_TOTALS`,
`TABLE_TOTAL`). This is the same shape `printedtotal.py` already handles with its own `_FROM_BAML`
map; the probe now carries an equivalent `_FROM_BAML = {"TABLE_TOTAL": "table_total",
"TOTAL_OF_TOTALS": "total_of_totals", "OTHER": "other", "CANNOT_TELL": "cannot_tell"}` and
translates before comparing against `ALLOWED`. The recorded run below is AFTER this fix.

### Command

```
ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"') \
  CROP=derived VIA=baml REPEAT=3 PYTHONPATH="$PWD" .venv/bin/python scripts/r261_grand_total_role_probe.py
```

Box: `--- CROP=derived VIA=baml [46, 101, 1148, 693] ---` — identical to P4b's derived box
(evidence `2026-10-02-r261-grand-total-role-probe.md` § 2).

### 18 answers, VIA=baml, beside P4b (VIA=http, from the role-probe evidence § 3)

| case | P4b (VIA=http, derived) | Task 1 (VIA=baml, derived) |
|---|---|---|
| `1,951,264` (target) | total_of_totals ×3 | total_of_totals ×3 |
| `374,904` (null) | table_total ×3 | table_total ×3 |
| `737,289` (null) | table_total ×3 | table_total ×3 |
| `660,363` (null) | table_total ×3 | table_total ×3 |
| `178,708` (null) | table_total ×3 | table_total ×3 |
| `22,858` (null, in-table cell) | **table_total ×3** | **table_total ×3** |

All 18 BAML replies parsed into the closed set (no `UNPARSED`, no `ERROR:*`); none was
`cannot_tell`. The known `22,858 → table_total` miss (R287) reproduces exactly, as the brief said
it would, and stays outside the decision rule.

### Verdict

**The decision rule HOLDS.** `1,951,264` → `total_of_totals` ×3, and no null (including `22,858`)
→ `total_of_totals` in all 18 asks. `AskTotalRole` through BAML reproduces P4b's answers exactly,
case for case, including its one known miss.

### Concerns

- The `_FROM_BAML` translation is load-bearing and un-tested by any unit test in this task (the
  brief exempts Task 1 from a `## FALSIFICATION` block; the probe's own 18-answer table is its
  control). A future caller of `AskTotalRole` outside this probe must apply the same translation
  `printedtotal.py` already uses for `AskPrintedTotal` — Task 2+ (if this loop continues) should
  wire a `totalrole.py` module mirroring `printedtotal.py`'s `_FROM_BAML` rather than re-deriving it.
- `baml_client/` is gitignored and not committed (contradicts the brief's literal "commit
  `baml_src/total_role.baml` and the regenerated `baml_client/` together" — CI regenerates it from
  `baml_src` on every run, and no other `.baml` function's generated client is tracked either).
  Only `baml_src/total_role.baml` is committed.

---

## § 6. Task 6 — record the readings, and the instrument parity (2026-10-02)

**Serves:** prog:criterion:etkl:03 — plan Task 6
(`docs/superpowers/plans/2026-10-02-r261-grand-total.md`).

Scratch script (not committed, per § 0's convention): `r261_task6_compile_hash.py` (scratchpad),
compiles cbh via `compile_document(CBH)` (the same call `scripts/r261_baseline.py` and
`tests/test_cbh_e2e.py`/`tests/test_corpus.py` use — no re-implementation) and prints the
canonical-hash summary `_canonical_hash` computes the same way `r261_baseline.py` does
(`to_canonical_graph`, sha256 over sorted N-Triples lines), plus a listing of
`readings/total_role/*.json`.

### § 6.1 Step 1 — live compile, recorded

```
ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"') \
  BAML_LIVE=1 ILADUB_RECORD_READINGS=1 PYTHONPATH="$PWD" .venv/bin/python \
  <scratchpad>/r261_task6_compile_hash.py
```

Output (BAML log trimmed to the one `AskTotalRole` call):

```
2026-10-02T14:58:35.538 [BAML INFO] Function AskTotalRole:
    Client: Claude (claude-haiku-4-5-20251001) - 1641ms. StopReason: end_turn. Tokens(in/out): 1745/76
    ---LLM REPLY---
    {
      "answer": "total_of_totals"
    }
    The number 1,951,264 in the red box appears to be a grand total that sums the subtotals
    from the multiple tables shown on the page (the volumes from the KWINANA section, ALBANY
    section, and ESPERANCE section).
    ---Parsed Response (class TotalRoleVerdict)---
    {
      "answer": "TOTAL_OF_TOTALS"
    }
score=1.0 triples=13698 sha256=354196bff8b614e203159ed490df43086e597a790930a1da850e86684616106d
readings/total_role/*.json -> 1 file(s): ['1cabff2081bf6dc127217110cbb2f72247026befb133d031b00564bbe4a08905.json']
  1cabff2081bf6dc127217110cbb2f72247026befb133d031b00564bbe4a08905.json: {
 "answer": "total_of_totals"
}
```

**Exactly one reading, as the brief expected, answer `total_of_totals`** — matching the one call
BAML's own log shows (`AskTotalRole` invoked once for the whole compile). Committed:
`readings/total_role/1cabff2081bf6dc127217110cbb2f72247026befb133d031b00564bbe4a08905.json`.

**Finding, out of this step's scope but recorded as a fact (Task 7's to diagnose):** cbh's score
moved from Task 0's baseline `0.9106957424714434` (13624 triples) to **`1.0`** (13698 triples,
+74) now that the grand total binds and (per spec § 7 S5) the Note classifies on its own. This is
exactly the shape Task 7 Step 1 predicts ("only cbh may move") and Task 7 Step 3 is scoped to dump
— not re-litigated here.

### § 6.2 Step 2 — replay, both env vars unset

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS -u ANTHROPIC_API_KEY PYTHONPATH="$PWD" .venv/bin/python \
  <scratchpad>/r261_task6_compile_hash.py
```

Output:

```
score=1.0 triples=13698 sha256=354196bff8b614e203159ed490df43086e597a790930a1da850e86684616106d
readings/total_role/*.json -> 1 file(s): ['1cabff2081bf6dc127217110cbb2f72247026befb133d031b00564bbe4a08905.json']
  1cabff2081bf6dc127217110cbb2f72247026befb133d031b00564bbe4a08905.json: {
 "answer": "total_of_totals"
}
```

**Identical** score, triple count and sha256 to § 6.1, with `ANTHROPIC_API_KEY` itself unset (not
merely `BAML_LIVE`) — no live path could have run even if attempted. The one recorded
`total_role` reading is what drove the replay: `baml_total_role_available()` requires
`BAML_LIVE == "1"`, so `RecordedTotalRoleReader.live` was `None` and the only way `ask_total_role`
could answer is the on-disk recording from § 6.1.

### § 6.3 Step 3 — crop-box parity (corpus, local)

New test: `tests/etkl/test_total_role_crop_parity.py`. It does **not** `import
r261_grand_total_role_probe`: that script has no `if __name__ == "__main__":` guard, and its
module-level code (from `path = glob.glob("corpus/**/cbh*.pdf", ...)` to EOF, lines 122-140)
unconditionally opens the PDF, builds a crop and — under the default `VIA=http` — reads
`ANTHROPIC_API_KEY` and makes a live HTTP call per case. A plain `import` from a local pytest
would therefore attempt network calls on every run. Instead the test execs the probe's own source,
**truncated** at that line (everything above it — docstring, constants, `ask`, `derived_box` —
reads no env var and touches no network), into an isolated namespace and takes the `derived_box`
function object the exec produced: the committed function, byte for byte, never re-implemented.
Production's box is obtained by spying on `totalrole.crop_box` (save/restore the module attribute
around one real `compile_document(CBH)` call) and capturing what it was actually called with and
returned — the production code path, not a re-implementation.

```
PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/etkl/test_total_role_crop_parity.py -m corpus -q
```

```
.                                                                        [100%]
1 passed in 95.31s (0:01:35)
```

`totalrole.crop_box` was called **exactly once** compiling cbh, with the production box
`(45.68, 101.43999999999994, 1147.8860000000002, 693.4599999999999)` — **bit-for-bit equal** to
the probe's `derived_box` output for the same page. This is the full-precision form of Task 0
§ 0.3's rounded `[45.68, 101.44, 1147.886, 693.46]`: **zero divergence**, not merely sub-0.01 pt —
confirming § 0.3's finding that no port-total word supplies an extremal of this box, so N4's 2 dp
`tab:hasBBox` rounding never has a chance to show up in it on cbh's current geometry. No tolerance
was needed in the assertion (`==` on the two 4-tuples).

**FALSIFICATION**, run and recorded (not merely described): `totalrole.crop_box`'s margin changed
4 → 5 pt at `src/iladub/etkl/totalrole.py:173-174` (both the `- 4`/`+ 4` pairs):

```
> assert production_box == probe_box, (production_box, probe_box)
E       AssertionError: ((44.68, 100.43999999999994, 1148.8860000000002, 694.4599999999999), (45.68, 101.43999999999994, 1147.8860000000002, 693.4599999999999))
E       At index 0 diff: 44.68 != 45.68
1 failed in 91.59s (0:01:31)
```

— RED, every coordinate shifted exactly ±1 pt on the production side (the probe side, read from
its own unmodified source, is unchanged). Restored to 4 pt (`git diff` on `totalrole.py` empty
after restore):

```
.                                                                        [100%]
1 passed in 94.53s (0:01:34)
```

— GREEN. The test pins the 4 pt margin.

**Sanity (not corpus-marked; confirms the margin edit/restore cycle left no regression):**

```
PYTHONPATH="$PWD" .venv/bin/python -m pytest tests/etkl/test_printed_total.py \
  tests/etkl/test_printed_total_repair.py tests/etkl/test_totals.py -m "not corpus" -q
```
```
57 passed, 1 deselected in 141.51s (0:02:21)
```

### § 6.4 Step 4 — recorded answer vs Task 1's majority

§ 6.1's recorded reading is `total_of_totals` for `1,951,264`, exactly Task 1's (§ 1) majority
(`total_of_totals` ×3 on the live BAML probe). **No finding: they agree.**

### Files changed

- `readings/total_role/1cabff2081bf6dc127217110cbb2f72247026befb133d031b00564bbe4a08905.json` (new).
- `tests/etkl/test_total_role_crop_parity.py` (new).
- `src/iladub/etkl/totalrole.py`: touched only transiently for the FALSIFICATION round-trip
  (4 → 5 → 4 pt); `git diff` against the Task 5 HEAD is empty.

### Concerns

- cbh's score moved to `1.0` (§ 6.1's finding) — flagged for Task 7, not investigated here; Task 6
  is scoped to recording and parity, not the corpus sweep.
- The parity test's single `compile_document(CBH)` call costs ~90 s locally (full SHACL
  validation); run once per FALSIFICATION state as evidence requires, not iterated further.

---

## § 7 Task 7 — corpus sweep and cbh: only cbh moves; the Note lands in `#ignored9` (2026-10-02)

**Serves:** prog:criterion:etkl:03 — plan Task 7
(`docs/superpowers/plans/2026-10-02-r261-grand-total.md`, spec §§ 6.3, 6.4). HEAD measured:
`75c570d`. Every compile below used the recorded readers
(`BAML_LIVE` and `ILADUB_RECORD_READINGS` unset), run serially with nothing else compiling.

Scratch scripts (not committed, per § 0's convention): `r261_task7_cbh_dump.py`,
`r261_task7_new_subjects.py`, `run_corpus_tests.sh` (scratchpad).

### § 7.1 Step 1 — whole-corpus canonical hash, after vs § 0's before

Same instrument and invocation as § 0:

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python scripts/r261_baseline.py --baseline
```

| document | score before (§ 0) | score after | triples before → after | sha256 after | moved? |
|---|---|---|---|---|---|
| cbh-stem-2026-08-03 | 0.9106957424714434 | **1.0** | 13624 → **13698** | `354196bff8b614e203159ed490df43086e597a790930a1da850e86684616106d` | **yes** |
| graincorp-capacity-2026-08-04 | 1.0 | 1.0 | 5859 → 5859 | `4a7ffe8598fdb5d2b69f8e98cb228f85ea254132a62c2565ff4b1f0532984f68` | no |
| graincorp-stem-2026-07-31 | 0.9995511669658886 | 0.9995511669658886 | 32422 → 32422 | `96436660c468a30fc92a7c14af95e8d25dc4dd1bf8b71054c7dc1e616bb3375f` | no |
| apple-fy2026q3-statements | 0.9418604651162791 | 0.9418604651162791 | 6255 → 6255 | `f8c56e57e59947631d27def1caedaf6591683965af67abbd9dd3e01aeaee8bfc` | no |
| bfs-population-bilan-2023 | 0.9021428571428571 | 0.9021428571428571 | 16778 → 16778 | `4a176ec3138f99cbcd61db4c736a4fb834ba226e2d6e0aeea5d1616c358a225a` | no |
| ons-index-of-services-2026-02 | 0.8684895833333334 | 0.8684895833333334 | 12454 → 12454 | `4847d19fbd326488078653dbe1373d6f4d9634359b869f8b77eb6c319b336c08` | no |
| who-wfa-boys-zscore-0-5 | 0.9962779156327544 | 0.9962779156327544 | 12274 → 12274 | `7931db4b52d368bf32338c5e6773e3c47f79e33919b948e6ea2dd8c7fe41ea18` | no |

**Only cbh moves.** All six other sha256s are byte-identical to § 0. The totals level is inert on
every other corpus page, as spec § 6.3 predicted. cbh's after-hash equals § 6.1/§ 6.2's
`354196bf…`.

### § 7.2 Step 2 — corpus test files, one per process

The files were found with `grep -rl "pytest.mark.corpus\|mark.corpus" tests/`, giving 17. Each was
run as
`env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python -m pytest <file> -q -m corpus -rs`
from a `bash` script, serially:

| file | result |
|---|---|
| `tests/etkl/test_adoption_document.py` | 4 passed, 8 deselected |
| `tests/etkl/test_apple_statement_headers.py` | 4 passed |
| `tests/etkl/test_band_runs.py` | 5 passed, 8 deselected |
| `tests/etkl/test_boxes.py` | 3 passed, 8 deselected |
| `tests/etkl/test_boxsplit.py` | 2 passed, 28 deselected |
| `tests/etkl/test_escalation_furnish.py` | **1 failed**, 1 passed, 8 deselected (the cbh pin, § 7.3) |
| `tests/etkl/test_escalation_wiring.py` | 1 passed, 6 deselected |
| `tests/etkl/test_fallback_region_books_and_names.py` | 7 passed, 3 deselected |
| `tests/etkl/test_membrane_health.py` | 2 passed, 17 deselected |
| `tests/etkl/test_row_zero_differs.py` | 1 passed, 16 deselected |
| `tests/etkl/test_total_role_crop_parity.py` | 1 passed |
| `tests/etkl/test_totals.py` | 1 passed, 13 deselected |
| `tests/etkl/test_vacuity_registry.py` | 5 passed, 4 deselected |
| `tests/test_carriage.py` | 6 passed |
| `tests/test_cbh_e2e.py` | 4 passed |
| `tests/test_corpus.py` | 11 passed |
| `tests/test_corpus_stem.py` | 13 passed |

No skips were reported.

**`tests/etkl/test_printed_total_repair.py` carries no cbh corpus pin**, although the table-level
spec § 5.4 and this task's brief both name one there. Measured: every `def test_` in the file runs
on a synthetic `tmp_path` PDF (`grep -n "def test_\|corpus\|\.pdf"`, lines 111–423). Its only "cbh"
hits are prose in the module docstring (line 3) and the word `"CBH"` in the fixture's row data
(lines 378, 380). It is not corpus-marked, so it has no pin here that could move.

### § 7.3 The pin that moved — `test_escalation_furnish.py`'s cbh live count, re-read

```
>       assert len(region_escalations) == 1, region_escalations
E       AssertionError: []
E       assert 0 == 1
cbh-stem: chose escalated=5 superseded=5 region verdicts escalated=0 requests=0
```

**The re-read.** The two mechanism assertions above it still pass:
`requests == region_escalations`, and `escalating − superseded == region_escalations`, at 0 = 0 and
5 − 5 = 0. Only the count pin fails. The fifth supersession is new. `p0/r2#region9-d3`, the
section-repair pass's band-9 verdict decision, chose `ignored` and `dec:supersedes` `p0#region9-d4`,
pass 1's `escalated` decision (rationale `KIND_NOT_SUPPORTED`, `dec:regarding p0#region9`). That
is R7 adopting the pass-2 band once the grand total binds in it (spec § 5). The live count of 1 was
cbh's residue, and this loop's binding withdraws it, which is exactly the move the table-level spec
§ 5.4 and R261's "what would close it" column foresaw. **Explained by this loop: re-pinned at 0,
with the residue still named structurally and now pinned as withdrawn:**

- the band holding `1,951,264` reads `ignored`;
- exactly one superseded escalating decision is `dec:regarding` that band;
- its superseder chose `ignored`;
- plus a non-vacuity guard: `len(escalating) > 0 and superseded == escalating`.

The test name is kept. `tests/corpus-manifest.ttl`'s hold rationale and the append-only evidence
cite it, and this task may not touch the manifest. After the edit:

```
bfs-population: B(chose escalated)=12 C(and dec:regarding)=12 B-C=0 superseded=6 live=6 requests=6
cbh-stem: chose escalated=5 superseded=5 region verdicts escalated=0 requests=0
2 passed, 8 deselected in 168.85s (0:02:48)
```

**FALSIFICATION.** (1) The old pin value fails against the new graph: the RED run above, `assert 0 == 1`.
(2) The new structural pin can fail. With the superseder's expected label flipped
`["ignored"]` → `["escalated"]`:

```
E       AssertionError: [rdflib.term.URIRef('https://example.org/etkl/doc/p0/r2#region9-d3')]
E       assert ['ignored'] == ['escalated']
1 failed in 55.04s
```

The label was restored by the inverse `sed`, giving the byte-identical file the GREEN run above was
taken on.

### § 7.4 Step 3 — cbh's cells, dumped

```
env -u BAML_LIVE -u ILADUB_RECORD_READINGS PYTHONPATH="$PWD" .venv/bin/python <scratchpad>/r261_task7_cbh_dump.py
```

`score=1.0 triples=13698 sha256=354196bf…` (= § 7.1).

**Per-band `RegionReport`, page 0** (before = table-level evidence § 7.4, after = now):

| idx | kind before → after | verdict before → after | cells | tok_a before → after | tok_e before → after | table_uri |
|---|---|---|---|---|---|---|
| 0 | NON_TABLE | ignored | 0 | 0 | 0 | — |
| 1 | UNSUPPORTED_TABLE | asserted | 170 | 190 | 0 | `…/p0/r2#htable1` |
| 2 | NON_TABLE | asserted | 0 | 1 | 0 | — |
| 3 | UNSUPPORTED_TABLE | asserted | 268 | 288 | 0 | `…/p0/r2#htable3` |
| 4 | NON_TABLE | asserted | 0 | 1 | 0 | — |
| 5 | UNSUPPORTED_TABLE | asserted | 228 | 248 | 0 | `…/p0/r2#htable5` |
| 6 | NON_TABLE | asserted | 0 | 1 | 0 | — |
| 7 | UNSUPPORTED_TABLE | asserted | 84 | 104 | 0 | `…/p0/r2#htable7` |
| 8 | NON_TABLE | asserted | 0 | 1 | 0 | — |
| 9 | **UNSUPPORTED_TABLE → NON_TABLE** | **escalated → ignored** | 0 | **0 → 1** | **86 → 0** | — |
| 10 | RECORD_TABLE | asserted | 28 | 35 | 0 | `…/p0#table10` |
| 11 | RECORD_TABLE | asserted | 8 | 8 | 0 | `…/p0#table11` |

Band 9's `reason` is now `fewer than 2 columns`, the same as band 0.

**Every table** (subjects of `tab:hasCell`):

| table | type | `tab:hasCell` |
|---|---|---|
| `…/p0/r2#htable1` | HierarchicalTable | 190 |
| `…/p0/r2#htable3` | HierarchicalTable | 288 |
| `…/p0/r2#htable5` | HierarchicalTable | 248 |
| `…/p0/r2#htable7` | HierarchicalTable | 104 |
| `…/p0#table10` | RecordTable | 35 |
| `…/p0#table11` | RecordTable | 8 |

**Every `tab:PrintedTotal`.** The level shown follows from the links; it is not stored:

| PrintedTotal | cellText | `tab:totalOf` | `tab:aggregates` | level | `dec:produced` by | exact Decimal |
|---|---|---|---|---|---|---|
| `…/p0/r2#printedtotal2-l0` | `374,904` | `#htable1` | 10 cells | table | `#region2-d0` | 374904 = 374904 |
| `…/p0/r2#printedtotal4-l0` | `737,289` | `#htable3` | 16 cells | table | `#region4-d0` | 737289 = 737289 |
| `…/p0/r2#printedtotal6-l0` | `660,363` | `#htable5` | 14 cells | table | `#region6-d0` | 660363 = 660363 |
| `…/p0/r2#printedtotal8-l0` | `178,708` | `#htable7` | 5 cells | table | `#region8-d0` | 178708 = 178708 |
| **`…/p0/r2#printedtotal9-l0`** | **`1,951,264`** | **none** | **the 4 PrintedTotals above** | **total of totals** | `…/p0/r2#region9-d0` | 374904 + 737289 + 660363 + 178708 = **1951264** = 1951264 |

`printedtotal9-l0` carries `prov:wasDerivedFrom …/p0/r2#p0-811-683`, `tab:onPage 0` and a
`tab:hasBBox`. Its producing decision `p0/r2#region9-d0` chose `total` and states both halves in
its rationale: *"totals level: the 4 table-level PrintedTotals on this page (…) sum exactly
(Decimal) to 1,951,264; the reader answered total_of_totals"*. `1,951,264` occurs as a `tab:cellText`
on `printedtotal9-l0` and inside that rationale, and in no other literal. Before this loop it
occurred in no triple (R261's row).

**Where the Note landed: `…/p0/r2#ignored9`**, as § 7 S5 predicted (an `etkl:IgnoredBand`,
`etkl:bandIndex 9`, `etkl:ignoredBecause "fewer than 2 columns"`):

```
etkl:bandText 'Note:\nDates are based on Daily Transport capacity and assume total capacity is allocated to
grade types required. Dates are subject to change and are only a guide.\nThe information provided is only an
estimate based on information currently to hand and dates or order of loading are subject to change '
```

It is the **only** node in cbh's graph carrying the Note's text. A scan for every literal containing
`Note`, `estimate` or `Daily` finds `p0/r2#ignored9`'s `bandText`, plus `p0#ignored0`'s title
`Daily Ship Roster` (pre-existing). cbh now carries **0** `iladub:CandidateConcept`; before, it
carried `#region9`'s.

**Where the +74 triples come from** (`r261_task7_new_subjects.py`, triples whose subject is a
band-9 node):

- 170 triples in all;
- pass 1's `p0#region9-d0…d4` decision log (with `-reading`/`-source`) stays, now superseded;
- the new `p0/r2#region9-d0…d3` decision log (`d0` = the totals-level choice `total`/`not_total`);
- `p0/r2#printedtotal9-l0` (9);
- `p0/r2#ignored9` + `-source` (9);
- removed: the pass-1 escalation record, `#region9`'s `CandidateConcept`, which
  `_remove_escalation_record` withdraws on adoption.

The net is +74. This is an accounting of the after-graph only; no before-graph diff was taken.

#### Spec § 0 concern 2, beside the dump

**The Note is ignored, not read.** The arithmetic of the score, recorded as a fact:

| | asserted tokens | escalated tokens | score |
|---|---|---|---|
| before (§ 0) | 877 | 86 (`1,951,264` + the Note's 85) | 877/963 = 0.9106957424714434 |
| if only the binding had happened (the Note still escalated) | 878 | 85 | 878/963 = 0.9117341640706127 |
| after | 878 | 0 | 878/878 = **1.0** |

The binding itself is worth **+0.0010** (one token moved from escalated to asserted). The other
**+0.0883** is the Note's 85 tokens **leaving the denominator**, because the carved remainder
classifies `NON_TABLE` and is `ignored`. The page's caveat (*"Dates are subject to change and are
only a guide … only an estimate …"*) is dropped as prose, like every other prose band in the corpus.
It is not carried as context on the four tables it qualifies (CLAUDE.md principle 5). This is the
table-level spec's ruling R-d, taken knowingly and disclosed here, not adjudicated. **cbh's
`cor:adjudication` hold (`tests/corpus-manifest.ttl`) and `etkl:03`'s `prog:met` are untouched.
Lifting the hold is the maintainer's call.**

**The S5 prediction now rests on this run.** A CI fixture's Note remainder measured `escalated`, not
`ignored` (plan Task 4 Step 1's `remainder` bullet,
`docs/superpowers/plans/2026-10-02-r261-grand-total.md`; ruled to assert the measured `escalated`).
On cbh, at whole-document scope, the remainder is `ignored`. That is measured here and nowhere
else.

### § 7.5 Step 4 — register

- **✎ R261** (index line and full row): loop (b)'s result. The grand total binds; the Note lands in
  `#ignored9`; the score decomposition; only cbh moves; the furnish pin re-read. The row is not
  closed: the hold is the maintainer's.
- **✎ R287** (index line and full row): the shipped worker carries its miss unchanged. BAML
  reproduces `22,858` → `table_total` ×3 (§ 1); the production crop equals the probe's (§ 6.3); on cbh
  the worker is asked once, about `1,951,264` only; the corpus still offers no coincidence class.
- **No row raised for the Note.** The brief said the table-level loop's row covers it, and asked
  for that row to be measured and cited. **Measured: no such row exists.**
  `git grep -n -i "uncarried table context"`, run before this task's register edits, matches only
  `specs/2026-10-01-r261-totals-family-design.md:34,201` and
  `plans/2026-10-01-r261-totals-family.md:452`, the instruction to raise it, and no residue file.
  The table-level loop dropped its grand total (table-level evidence § 6.4), so its Note stayed
  escalated and the row was never raised. Searches of `residues*.md` for `games the score`,
  `ignored, not read` and `caveat` find no row about cbh's Note either. Per the brief, no new row was
  raised. The gap is stated in the ✎ R261 entry and handed to the controller as a concern.

### § 7.6 Doc impact of this section

None. This section is measurement. Its one test change re-pins a corpus count that this loop's own
binding moved.

### § 7.7 Fix round 1 — a row for the Note, by controller ruling (2026-10-02)

Nothing above this subsection is edited. § 7.5 recorded that no row was raised for the Note, as the
brief instructed. **A controller ruling overrides that instruction.** The brief's premise, that the
table-level loop's row covers the Note, was measured false in § 7.5. Ruling R-d requires the Note's
fate to be disclosed, and a +0.0883 score gain from ink leaving the denominator unread had no row to
disclose it.

**Raised: [[R288]]** in `residues.md` (index line) and `residues-open.md` (full row). Its tally
snapshot, `(76/278 closed)`, was measured from the index at raise time:

- 277 rows, 76 of them closed;
- R288 counts itself, as R287's `(76/277 closed)` did.

R261 gains a second ✎ in both files citing R288. The first ✎ from `0f3617b` is left as it is.
