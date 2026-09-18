# Evidence — R253's symptom reproduces, its explanation does not: the live disposal is UNRELIABLE, not blocked

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]]'s row.

**Date:** 2026-09-18. **Branch:** `r253-the-grain-of-the-ask`, cut from `main` at `cb3a266`.

**Doc impact: none.** No published term, shape, `rdfs:comment` or nav entry is touched. `src/`,
`vocab/` and `baml_src/` end this loop **byte-identical to `main`** — the loop's product is two
instruments and this measurement.

Every figure carries the command that produced it. **This loop wrote a spec, ran its control, and
then found the control itself too small to settle anything** (§ 8). That spec is not committed; § 8 is
the record of what it claimed, what killed the first version of this document's conclusion, and what
is left genuinely open.

**Read § 8 before quoting § 7.** An earlier draft of this file concluded that R253's premise was
flatly refuted. Two further traced runs, which landed after that draft was written, refuted *the
draft* — one of them reproducing R253's recorded figure exactly. The correction is kept visible
rather than tidied away, because the sequence is the finding: **a conclusion drawn from six readings
of a non-deterministic reader was wrong at nine.**

---

## The short version

| claim | status |
| --- | --- |
| [[R253]]: *"the live disposal types NOTHING end-to-end"* | **REFUTED as a standing claim** — 2 of 5 live compiles carried 109 and 110 to the graph (§ 7) |
| [[R253]]'s recorded figure (`\|A\|` = 110, control fails, types 0) | **REPRODUCED** — 1 of 9 readings, so the original measurement was real (§ 7) |
| [[R253]]: *"nothing in the pipeline can supply that set"* | **beside the point** — the reader supplies the 26 empties itself in 6 of 9 readings (§ 7) |
| the handoff's prediction (spanned supplied ⇒ end-to-end) | **CONFIRMED**, offline (§ 1) |
| `spanned` could ever have protected an *assertion* | **NO** — arithmetic, by construction (§ 2) |
| this loop's own spec (the ask's span clause is the blocker) | **UNSETTLED, n = 2 against n = 9** — not committed (§ 8) |
| the cause of the intermittent zero | **at least three reader regimes, one cause unestablished** (§ 9) |

---

## 1. The handoff's prediction, run offline — CONFIRMED, with two null arms firing

The 2026-09-18 handoff typed its part 5 **PROPOSED** and ordered the prediction run before anything
was built on it. Instrument: `scripts/unshown_ink_grain_control.py` — a `FakeRegionReader` (no
model, no network), `compile_document` through the real dispatch with `validate_shapes=True`, four
arms, **each in its own interpreter**.

```
$ ./.venv/bin/python -u scripts/unshown_ink_grain_control.py
ARM 1 — position-grain ask: reader reports every empty place
  |reading|=136  |spanned|=0
  disposed per page_bands call: [110, 110]
  COMPILED  score=1.0000  tab:unshownText=110  tab:EntryCell=406  emptied cellText=110

ARM 2 — the handoff's prescription: 110 U (1,6), spanned supplied
  |reading|=111  |spanned|=25
  disposed per page_bands call: [110, 110]
  COMPILED  score=1.0000  tab:unshownText=110  tab:EntryCell=406  emptied cellText=110

ARM 3 — NULL: reader withholds the empties, spanned supplied
  |reading|=110  |spanned|=25
  disposed per page_bands call: [0, 0]
  COMPILED  score=1.0000  tab:unshownText=0  tab:EntryCell=406  emptied cellText=0

ARM 4 — NULL: reader withholds the empties, no spanned
  |reading|=110  |spanned|=0
  disposed per page_bands call: [0, 0]
  COMPILED  score=1.0000  tab:unshownText=0  tab:EntryCell=406  emptied cellText=0
```

**Arm 2 is the prediction and it holds**: with the spanned set supplied, a reading carries through
`region_unshown` → `dispose` → `Band.unshown` → `_UnshownCarriage` → the membrane and reaches the
graph — 110 `tab:unshownText`, 406 `tab:EntryCell` intact, 110 emptied `tab:cellText`, compile green.
So the subject was [[R253]] and not [[R252]]; [[R252]] stays open, untouched, as the boundary on the
other six documents.

**Arms 3 and 4 are the null and they fire.** Both dispose nothing, so the instrument is not measuring
its own join.

## 2. `spanned` could never have protected an assertion — arithmetic, not luck

```
src/iladub/etkl/unshownink.py:176
    return frozenset(reading.empty_cells & has_glyph)         # the disagreement
```

A position covered by a span but not holding the glyph is by definition in
`all_positions - has_glyph`; the intersection removes it. So a reader reporting a spanned position as
empty **cannot mint a `tab:UnshownInk`** — it can only feed the null control. Arm 1 measures exactly
this: a 136-address reading (the 25 column-0 places included) disposes **110**, not 135, not 406.

## 3. The withheld positions genuinely show a reader nothing

Column 0 of gcap band 3, from the text layer:

```
grid 27x16
  row  0: '2025/26'
  row  1: <no glyph>
  row  2: <no glyph>
  row  3: '2026/27'
  row  4: <no glyph>
  … rows 5–26: <no glyph>
```

Two year labels, at rows **0** and **3**, and **25 positions with no glyph**. Spec § 8.7 called this
*"the spanning year label a reader reads as ONE cell"*. A reader asked *"does this place show a
mark?"* answers **no** at all 25 — the text layer's own answer.

## 4. The seam is one module, one commented-out caller, one test

```
$ grep -rn "spanned" src/ tests/ scripts/ | grep -v '\.pyc' | grep -iE "unshown|dispose"
src/iladub/etkl/unshownink.py:130:            spanned: frozenset[tuple[int, int]] = frozenset()) …
src/iladub/etkl/unshownink.py:172:    text_layer_empty = (all_positions - has_glyph) - spanned
src/iladub/etkl/unshownink.py:180:                   spanned: frozenset[tuple[int, int]] = frozenset()):
src/iladub/etkl/unshownink.py:195:    return dispose(reader.read_empty_cells(crop, nrows, ncols), cells, nrows, ncols, spanned)
src/iladub/etkl/compile.py:494:            # `spanned` IS NOT SUPPLIED, AND THAT BLOCKS THE DISPOSAL — measured, not feared.
tests/etkl/test_unshown_ink.py:326:    got = dispose(_reading({(0, 0)}), _grid3x3(), 3, 3, spanned=frozenset({(1, 2)}))
```

Declared in **one** module, defaulted at **every** call site, supplied by **no** production caller
(`compile.py:494` is a comment saying so), pinned by exactly **one** test.

## 5. Two `page_bands` calls per compile, and this turns out to matter

Located, not assumed:

```
call 1: from document.py:1437 in compile_document      grid 27x16  cells=406  empties=26
call 2: from compile.py:875   in compile_tables        grid 27x16  cells=406  empties=26
```

Identical partition, identical grid, identical empties. **With a live reader this is two model
calls per compile, and only the second one's result reaches the graph** — see § 9, where that is
the difference between a document carrying 110 facts and carrying none.

## 6. An instrument defect, recorded because it is this thread's third of its kind

A first version of the four-arm instrument ran all arms in one interpreter and reported arm 3 as
`[110, 0]` — two different answers from one reading and one spanned set. **That was the
instrument's defect, not the pipeline's.** Re-run one arm per process, every arm's two calls agree.
`main()` now re-execs itself per arm for that reason.

## 7. LIVE — every band-3 reading taken this session

Instrument: `scripts/unshown_ink_live_oracle.py` (single readings) and a `dispose`-wrapping trace of
`compile_document` (full compiles). gcap band 3 — 27×16, 406 populated, **110 zeros, 26
text-layer-empty** — `claude-sonnet-5` via the pinned `ClaudeLongAnswer` client.

`raw recall` and `raw control` are computed **independently of `dispose`**, and that matters: `dispose`
returns the empty set on *any* refusal, so it collapses *"the ask made the reader withhold"* into
*"the reader found nothing"*. Without the raw figures the two regimes below are indistinguishable.

```
$ ANTHROPIC_API_KEY=… BAML_LIVE=1 BAML_LOG=off \
      ./.venv/bin/python -u scripts/unshown_ink_live_oracle.py
```

| # | ask | source | \|A\| | control /26 | off-target | dispose |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **SHIPPED** | oracle | 135 | 26 ✓ | 0 | 109 |
| 2 | **SHIPPED** | oracle | 136 | 26 ✓ | 0 | 110 |
| 3 | **SHIPPED** | oracle | 134 | 26 ✓ | 0 | 108 |
| 4 | **SHIPPED** | compile A, call 1 | 136 | 26 ✓ | 0 | 110 |
| 5 | **SHIPPED** | compile A, call 2 | 135 | 26 ✓ | 0 | 109 |
| 6 | **SHIPPED** | compile B, call 1 | **0** | ✗ | — | **0** |
| 7 | **SHIPPED** | compile B, call 2 | 136 | 26 ✓ | 0 | 110 |
| 8 | **SHIPPED** | compile D, call 1 | **0** | ✗ | — | **0** |
| 9 | **SHIPPED** | compile D, call 2 | **110** | ✗ | — | **0** |
| — | place-grain (§ 8) | oracle | 133 | 26 ✓ | 0 | 107 |
| — | place-grain (§ 8) | oracle | 136 | 26 ✓ | 0 | 110 |

**Nine readings of the shipped ask: 6 satisfy refusal 3's control and 3 do not.** Every passing
reading disposes 108–110 with **zero false positives**, and **no reading in the whole table ever
invented a cell** (off-target 0 throughout). Recall among the passing six is 108, 109, 110 — reported,
never averaged, as `unshownink.py`'s module docstring requires.

**Row 9 is R253's recorded figure, reproduced.** `|A| = 110` — the hidden cells and nothing else, the
26 empty places withheld — control fails, region refused, types 0. That row's original measurement was
**real**; what it was not is *structural*. It is one of at least three answers this reader gives to one
crop.

**And the full compiles:**

| compile | call 1 → | call 2 → | graph |
| --- | --- | --- | --- |
| A (traced) | 110 | 109 | **109** |
| B (traced) | 0 | 110 | **110** |
| C (untraced) | not captured | not captured | **0** |
| D (traced) | 0 | 0 (`\|A\|`=110) | **0** |
| E (traced) | — | — | **aborted before band 3** |

**2 of 5 carried facts; 2 typed 0; 1 aborted.** So *"types NOTHING end-to-end"* is false as a standing
claim, and *"works end-to-end"* would be equally false. The honest word is **unreliable**.

Compile E aborted with an exception whose traceback **was filtered by the invoking `grep` and is not
captured** — a suspected fourth regime, recorded as unmeasured rather than guessed at. ([[R254]]
records `BamlValidationError` from truncation on the *shared* client; this one is at `max_tokens
16000`, so that explanation is available but not evidenced.)

## 8. This loop's spec, its control, and why the control was too small

**What the spec claimed.** That the ask's span clause —

```
A position covered by a cell that SPANS several rows or columns is not empty — you see that
cell's content there. Report a position as empty only when the place itself shows nothing.
```

— asks at **cell** grain while `headers._grid_cells` reads at **place** grain, and that this mismatch
is what makes refusal 3 unsatisfiable. The remedy was to delete the clause, ask at place grain, and
remove the `spanned` parameter.

**What the control found, and what it did not.** Running the *shipped* clause on the same crop gave
26/26 three times (rows 1–3), which looked like a clean refutation: if the shipped clause also gets the
empties, the clause is not the discriminator. **That conclusion was drawn at six readings and is wrong
at nine.** Row 9 shows the shipped ask producing exactly the withholding behaviour the spec predicted —
`|A| = 110`, the 26 empties withheld, which is *the span clause being obeyed*.

So the position is:

- The span clause **is** implicated in regime (ii). The spec's mechanism is not refuted.
- Whether removing it *reduces* that regime's frequency is **unmeasured**: the rephrased ask was run
  **twice** (both 26/26, disposing 107 and 110). **n = 2 against n = 9 settles nothing** about a
  reader that fails 3 in 9.
- Therefore **nothing was committed.** `baml_src/unshown_ink.baml`, `src/` and `vocab/` end this loop
  byte-identical to `main`, and the prompt was restored with a scripted edit against a `cp` backup,
  never `git checkout`.

**The discipline this loop nearly broke.** Had the last two traced runs not been launched, this
document would have shipped *"R253 is refuted"* on six readings, and R253 would have been closed. The
register would then have carried a confident refutation of a row whose figure reproduces one run in
nine. The instrument that saved it was simply **more samples of the same thing**, which is the cheapest
control available and was not in the spec's oracle list.

## 9. The three regimes, and what causes them

Measured on one crop, shipped ask, nine readings:

| regime | \|A\| | control | dispose | n | fail-safe? |
| --- | --- | --- | --- | --- | --- |
| (i) hidden ∪ empties | 133–136 | ✓ 26/26 | 107–110 | 6 | — (this is the wanted answer) |
| (ii) hidden only, empties withheld | 110 | ✗ | 0 | 1 | **yes** — no claim |
| (iii) empty answer, `refuses_grid=False` | 0 | ✗ | 0 | 2 | **yes** — no claim |
| (iv) suspected: an aborting exception | — | — | — | 1 compile | unknown |

**Every observed failure is fail-closed.** No regime mints a false `tab:UnshownInk`; the cost of
failure is 110 good addresses silently discarded, never a wrong assertion. That is the design working
as § 4.2's open-world clause intended.

**Regime (iii)'s cause is NOT established.** `|A| = 0` with `refuses_grid = False` is neither a grid
refusal, nor an out-of-range address, nor an exception. Truncation is the standing suspect but this
client is at `max_tokens 16000` and a successful 110-address answer used 3198 output tokens, so
truncation is *available* as an explanation and not *evidenced*. **The `note` field was not captured on
either failing run** — capture it, and the raw response, before theorising. Naming a remedy before the
cause is known is exactly what R253 did.

**Regime (ii)'s cause is the span clause being obeyed**, which is § 8's mechanism and is the only
regime with a candidate remedy already drafted.

## 10. What is NOT measured here

- **No frequency claim is supported.** 3 failures in 9 readings and 2 zeros plus 1 abort in 5 compiles,
  on **one crop of one document**, in one session. These are observations. Nothing here is a rate, and
  nothing here should be quoted as one.
- **Regime (iii) and (iv)'s causes are open** — see § 9. The diagnostic fields were not captured.
- **The rephrased ask is untested**, not refuted (§ 8). Two readings.
- **Only graincorp-capacity.** [[R252]] stands: the address spaces disagree on the other six documents,
  so nothing here says the carriage reaches a second one.
- **No score movement.** Every arm and every compile reports `score=1.0000`; the document score is
  blind to cell carriage ([[R240]]), so it is not evidence the carriage is right.
- **The over-reporting reader is still unguarded.** A reader calling every position empty would satisfy
  refusal 3 and mint 406 false `tab:UnshownInk`. That is [[R254]]'s open question and nothing here
  changes it — note that regimes (ii) and (iii) are the *opposite* direction and are safe, which is
  why they cost facts rather than truth.
- **Why there are two `page_bands` call sites at all was not established** — they were located
  (§ 5) and the enquiry stopped there. That is [[R255]].

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
