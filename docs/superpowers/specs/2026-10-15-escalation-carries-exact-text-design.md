# Spec: an escalated region carries its exact text, not a layout render

**Serves:** maintenance — loop (a) of `docs/superpowers/2026-10-15-r44-subject-chosen-handoff.md`
§ 5.2, chosen by the maintainer on 2026-10-15 in session over (b), the band-role reading
(tab:07). This loop meets no criterion. It repairs a § 6 defect on every escalation, and (b)'s
oracle will need the text it produces.

**Topic:** compile · **Date:** 2026-10-15. **Branch:** `r318-exact-surface-text`, cut from `main`
after #346.

**Doc impact: none.** No term is added and no term changes meaning. `iladub:surfaceText` already
says *"The literal text in the document that triggered the candidate"* (`vocab/ontology/iladub.ttl:83-85`).
This loop makes the escalation sites honour that definition.

**Global Constraint: the neurosymbolic gate (CLAUDE.md § 8).** One decision changes, classified in
§ 3.3. No NEURAL worker is added and no tuned constant appears. A tuned constant is removed from the
provenance path: the 80-column canvas width.

---

## 0. The concern, first

Every escalated region is a proposition (CLAUDE.md § 3) whose `iladub:surfaceText` should be the
ink it quarantines. At almost every escalation site it is instead `render_ascii(band)`
(`src/iladub/etkl/roundtrip.py:137`), which places each word on an 80-character canvas scaled by
x. Two words that land on the same column overwrite each other, and a word that runs past column 80
is cut. So the one literal that a reader, an adjudicator or a later NEURAL worker gets for a
quarantined region **is not what the page says**. Two accepted adjudications have already blamed
"the text layer" for damage this renderer did (§ 1.4).

## 1. What was measured

1. **The census (handoff appendix, at `9d3c73c`).** Of the 71 live `KIND_NOT_SUPPORTED` and
   `REGION_TILING_FAILED` regions, compared whitespace-insensitively, **59 lose text** between
   `band_text(band)` and the rendered `surfaceText`. Example from bfs p4r0: `G1 Composantes de
   l'évolution démographique, de 1971 à 2023` is carried as `G1 Composantesde
   l'évolutidémographiquede 1971à2023`.
2. **The sites.** `ascii_view = render_ascii(band)` at `compile.py:1281` is passed to
   `escalate_region` (`holon.py:557`) by every band-level escalation in `compile.py`:
   MULTI_TABLE_AMBIGUOUS, the RECORD paths, TRANSPOSED, ROW_GROUP_AMBIGUOUS, MATRIX_AMBIGUOUS,
   MERGE_AMBIGUOUS, REGION_TILING_FAILED and KIND_NOT_SUPPORTED (`grep -n "escalate_region(\|ascii_view" src/iladub/etkl/compile.py`,
   2026-10-15). `ascii_view` is also stored as `RegionReport.ascii` (`compile.py:765`).
   Three other sites:
   - `ruleguard.py:200` (RULE_SEPARATED_INK) escalates `r.ascii`, the stored report field. For an
     appended data grid, that field is `render_ascii` over the grid's lines (`compile.py:1938`).
   - `holon.py:726` (ROUND_TRIP_FAIL) escalates `render_region_ascii(region)`, a render of the
     **parsed reading** and not of the ink. `band` is in scope there.
   - `compile.py:2195` (DATAGRID_RESIDUE) already carries words joined in reading order, the
     same form as `band_text`. **It is the only site that is exact today.**
3. **The exact text already exists.** `bands.band_text(band)` (`bands.py:82-90`) is a pure
   raw-extraction join: words left to right, lines newline-joined, no normalisation. `etkl:bandText`
   already carries it for ignored bands (`holon.py:635`).
4. **The adjudications that misattribute.** bfs `tests/corpus-manifest.ttl:454` (verified by the
   handoff's session) and ons `:114` (to be re-read). § 3.5 corrects them.
5. **The premise, run 2026-10-15 by a delegated measurement on `r44-subject-handoff`. It is FALSE
   as first stated and TRUE as narrowed.**
   - The instrument (`capture.py`, `analyze.py`, `render.py`) lived in the session scratchpad and
     does not survive. Its method: wrap `compile.escalate_region`, take `band` from the caller frame,
     and join on candidate IRI, never on anchor.
   - **Control passed.** The 71 captured (page, region, reason) triples equal the baseline exactly,
     and `render_ascii(band)` equals the graph's surfaceText on all 71.
   - **Characters: `band_text` equals an independent pdfplumber crop of the band's bbox on 71 of
     71**, compared with whitespace removed. Only half independent, because `geometry.py:50` calls
     the same `extract_words` defaults.
   - **Renders confirm `band_text` against the printed page** on ons p7r0, bfs p4r0, bfs p6r11 and
     fed p6r4. They refute `render_ascii` on ons p7r0 (`IOSIndeoServic1s`). I looked at ons p7r0 and
     arxiv p10r1 myself, in this session.
   - **It differs from the printed reading on at least 10 regions,** all of them extractor defects
     upstream of both renderers:
     - **Missing interword spaces on arxiv.** On p10r1 `band_text` has `preprintarXiv:1610.02357,2016.`
       where the page prints `preprint arXiv:1610.02357, 2016.`, which this session verified on the
       render. A proxy (`x_tolerance=1`) flags 42 of the 47 arxiv regions, and only p10r1 has been
       checked by eye.
     - **Rotated text** on the arxiv attention figures (p12-p14, 8 regions) is broken into single
       letters.
     - On who-covid p0r2, `SITU ATION` and two interleaved columns.
   - **So the narrowed premise holds:** `band_text` is exact to the extractor's words, and strictly
     no worse than `render_ascii` on any region. It is not exact to the printed reading. The
     invariant (§ 3.1) is stated at that strength.

## 2. What the maintainer ruled, 2026-10-15, in session

Loop (a) before loop (b). Recorded nowhere but here and in the handoff's § 5.

## 3. Design

### 3.1 The invariant

**Every `iladub:surfaceText` written by `escalate_region` is `band_text` over the lines of the
escalated region**: its word objects in reading order, lines newline-joined. No escalation site may
pass a positional render.

It is **not** "all the ink the region covers", and the spec must not claim that. Ink held outside
`band.lines` is carried on other nodes or not at all. `Band.unit_markers` (`bands.py:30-34`) goes
on its own node via `_emit_unit_markers` and is booked separately by `_marker_word_count`
(`compile.py:352-358`). `Band.captions` (`bands.py:26-29`) is peeled off above the grid. The
surface text of an escalation is the text of its lines, and nothing more.

It is also **exact to the extractor, not to the printed reading** (§ 1.5). Word segmentation and
rotated text are the extractor's defects, so they are out of scope here (R320). What this loop
removes is the second, positional loss that `render_ascii` adds on top of them.

### 3.2 What changes

- **`RegionReport.ascii` is renamed `text`, and carries `band_text`** wherever it is set from a
  band (`compile.py:1281`) or from a grid's lines (`compile.py:1938`). A field named `ascii`
  holding exact text would mislead the next reader, so the rename is part of the fix. Every reader
  is renamed with it: `ruleguard.py:200`, `tests/etkl/test_r301_appended_region.py`, and the
  `scripts/` probes that read `r.ascii`. Enumerate the probes with
  `grep -rn "\.ascii\b" scripts/` before editing, and do not trust this list.
- **`holon.py:726` (ROUND_TRIP_FAIL) carries `band_text(band)`.** The parsed-reading render
  describes the refuted reading, not the page, and it is not the surface text. Whether it is
  worth keeping elsewhere, as an `rdfs:comment` say, is **not** decided here (§ 6).
- **`render_ascii` and `render_region_ascii` stay**, as public diagnostics: `render_ascii` is
  exported from `iladub.etkl`, and both have their own tests. Neither may be reached from
  `escalate_region` afterwards, and their docstrings stop saying *"Used as escalation surface text"*.
- **`escalate_region`'s parameter `ascii_text` becomes `surface_text`**, with a docstring line
  stating the invariant of § 3.1.

### 3.3 Gate classification

**PROCEDURAL**: raw extraction (source → typed RDF fact). It joins the words the extractor
produced, in the order it produced them, and makes no reading judgement. It is irreducible to
AXIOM because the words are not yet in the graph when they are joined. That is the
`band_text` docstring's own justification, and this loop adds no new code path to justify.

### 3.4 What does not change

Verdicts, reasons, anchors, confidences, cell counts, token counts, scores, chains and the number
of triples. One literal changes per non-residue escalation, and nothing else does.

### 3.5 The adjudications

`tests/corpus-manifest.ttl` adjudications are append-only. Do not edit the bfs and ons entries.
Add **one new dated `cor:adjudication` node per document**. It says the garbling they describe was
the renderer's and not the text layer's, cites this spec, and disposes of nothing else.

Several adjudications on one document is legal, and the file already does it:
- ons carries a 2026-08-20 node and a 2026-09-18 node (`corpus-manifest.ttl:111-113`).
- bfs's 2026-10-05 node says *"This note does not supersede the earlier notes, which are not
  repaired in place"* (`:453`).
- `tests/test_arc_manifest.py:157` reads adjudications existentially, not universally.

Measured during the review on 2026-10-15. **Still to measure:** the line numbers move whenever #346
or anything else lands, so re-read the exact sentences being corrected at implementation.

## 4. Oracles and predictions

1. **Unit oracle (new test).** A band whose words collide on an 80-column canvas, meaning two words
   whose scaled x positions coincide plus a line longer than 80 characters, reaches an escalation
   in `compile.py`. Its candidate's `iladub:surfaceText` **equals `band_text(band)` exactly**.
   **Falsification:** restore `render_ascii` at `compile.py:1281`, and the test must fail.
   **THE SEAM, unmeasured (CLAUDE.md plan rule 5):** can a synthetic band reach an escalation site
   at all? Before writing the test, measure which entry point accepts a constructed `Band`, or
   whether the existing tests reach escalations only through a generated or fixture PDF. A test
   that calls `escalate_region` directly with `band_text` would pin nothing, because it would
   pass with the fix deleted.
2. **Site-coverage oracle (new test).** For each escalation reason that an existing fixture
   reaches, the surfaceText **equals `band_text`** of the escalated region's lines. Name the
   fixtures by measurement, not from this list. The test compares the strings, **never a
   whitespace-split multiset**: R319's 3-tokens-for-38-words suggests that a word object can
   contain spaces, so a whitespace split would count different words from the ones the extractor
   produced. **Falsification:** revert only `holon.py:726`, and the ROUND_TRIP_FAIL case must
   fail. If no fixture reaches ROUND_TRIP_FAIL, say so; do not invent one.
3. **Corpus prediction (PROPOSED, falsifiable within the 24-minute regenerate).** In
   `git diff -- tests/corpus-baseline/`, `graph_sha256` moves on **exactly** arxiv, bfs, fed-h41,
   ons and who-covid, which are the documents with at least one non-DATAGRID_RESIDUE escalation
   (measured from the baseline at `9d4473c`). It does **not** move on apple or caltrain, whose only
   escalations are DATAGRID_RESIDUE and already exact, or on the four documents with none.
   `graph_triples` and every other field are unchanged everywhere. **A diff outside that set means a
   site this spec missed, or a consumer of the old literal. Investigate it; do not regenerate past
   it.**
   **WEAKEST PART OF THIS PREDICTION.** The document set is read off the band reports' verdicts,
   but ROUND_TRIP_FAIL escalations are written into a **scratch graph** by `assert_hier_region`.
   Six callers do this (`compile.py:1530,1831`, `span.py:98`, `rowrole.py:310`,
   `ruledroles.py:542`, `donation.py:415`), and each merges its scratch or drops it on its own
   terms. A merged scratch could carry a `…-rt` candidate onto a document whose reports show no
   ROUND_TRIP_FAIL. Before regenerating, count the `…-rt` candidates in each document's compiled
   graph so that the predicted set is measured rather than inferred.
   **The other half is measured:** nothing in `src/`, `vocab/` or `readings/` reads
   `iladub:surfaceText`. It is written at 9 sites, and the only shape on it is a `sh:minCount 1`
   (`vocab/shapes/iladub-shapes.ttl:18`). So a changed literal cannot move a verdict or a score.
4. **The baseline check.** CI's `check` gate, plus `corpus_baseline.py verify` run locally.

## 5. Residues to raise (in this loop's first commit)

- **R318 (91/308 closed): escalation surfaceText is a lossy layout render.** This loop closes it.
- **R319 (91/309 closed): escalated-token under-count.** It is measured on 13 of the 71 live
  regions, always as an under-count (bfs p6r11 3/38; who p4r0 105/372; fed ×4; arxiv ×5, off by
  one each). `tokens = sum(len(ln.words) …)` counts Word objects (`compile.py:1845,1885`, and
  `:1384,1621`). A ruled band's Words are whole cells, "each non-empty cell becomes one Word"
  (`geometry.py:307-316`, reached via `compile._build_ruled_band`). All 13 bands overlap vertical
  rules, but the path was not traced per region. Left open.
- **R320 (91/310 closed): extractor word segmentation is lossy on arxiv, and rotated text is
  shattered.** Spaces are missing, as in `preprintarXiv:…`, measured on p10r1 and flagged by proxy
  on 42 of 47 regions. The attention-figure pages (p12-p14) break vertical words into letters. This
  is upstream of `band_text` and of everything that reads Words. **A tuned `x_tolerance` is not the
  remedy** (CLAUDE.md § 8). Left open.

## 6. What is NOT done

- No band-role reading, class or worker: that is loop (b), tab:07.
- No change to how many tokens an escalation books: that is R319.
- `etkl:bandText` and `IgnoredBand` are untouched.
- The parsed-reading render of a ROUND_TRIP_FAIL is not preserved anywhere. Whether it should be
  is an open question, not a residue: no one has asked for it.
- No change to `iladub:surfaceText`'s vocabulary definition.

- No change to unshown text (R213). `band_text` includes text that the layer holds and the page
  does not show (`bands.py:35-40`). `render_ascii` included it as well, so this is not a
  regression. But "exact" here means **exact to the text layer**, not to what a reader sees. That
  is the same caveat the census carried ("shown through `band_text` ... not by rendering the
  page").
- The comment at `compile.py:1864`, *"ROUND_TRIP_FAIL never reaches escalate_region"*, is
  misleading: `holon.py:726` does call it, into scratch. It is not corrected here, because the
  comment sits below edits this loop makes (CLAUDE.md plan rule 7). Fix it only line-neutrally, if
  at all.

## 7. Unverified or assumed

- § 1.5's printed-reading defects beyond p10r1 are counted by proxy, not by eye. The narrowed
  premise (exact to the extractor) does not depend on them.
- The 59/71 figure compares strings with whitespace stripped, so a word-order difference would also
  count as loss.
- That `RegionReport.ascii` has no reader beyond those named in § 3.2: measured by
  `grep -rn "\.ascii\b\|ascii=" src/ scripts/` on 2026-10-15, and to be re-run at implementation.
- The corpus prediction (§ 4.3) assumes no escalation site other than those in § 1.2 writes
  `surfaceText` through `escalate_region`. `grep -rn "escalate_region(" src/` on 2026-10-15
  listed exactly those, and that grep should be re-run before regenerating.
