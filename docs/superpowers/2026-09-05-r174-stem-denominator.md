# R174 is CONFIRMED — stem's rise is one word leaving the denominator

**Measured 2026-09-05.** Runs the **PROPOSED** action 5b of
`docs/superpowers/2026-09-04-r173-bisect-handoff.md`. The prediction stands.

## 0. Verdict

**CONFIRMED, and stronger than predicted.** The rise is a *pure* denominator effect: the numerator
is byte-identical, the denominator loses exactly **one** token, and the entire document-wide diff
is **one line of unread banner ink**. Not one additional cell was read.

**And a finding nobody predicted: the R154 loop already knew.** `20cc5b8`'s own commit message
records `gstem .96546->.96589`. It measured the move, wrote the denominator ruling, re-baselined
every *non-corpus* pinned test it moved — and left this one, because nothing ever runs it. R174 is
therefore **not** an unnoticed regression. It is a known, intended, recorded score move whose
pinned test went stale purely through the CI invisibility that [[R173]] owns.

## 1. The arithmetic that decides it

```
$ python3 -c "print(2152/2229, 2152/2228, 586/613, 586/612)"
0.9654553611484971 0.9658886894075404 0.9559543230016313 0.9575163398692811
   ^ the pinned test value    ^ what the tree reads today
```

| | `5743af3` (before) | `20cc5b8` (after) |
| --- | --- | --- |
| document score | `0.9654553611484971` | `0.9658886894075404` |
| **numerator** — Σ `page.asserted` | **2152** | **2152** — unchanged |
| **denominator** — asserted + escalated | **2229** | **2228** |
| Σ `page.escalated` | 77 | 76 |
| `tab:EntryCell` nodes | 2047 | 2047 |
| `tab:cellText` triples | 2104 | 2104 |
| `adopted` / `repaired_bands` / `refused_licences` / `notes` | `()` | identical |
| `chains` | 1 of 3 (`p0#htable2 → p1#htable1 → p2#htable1`) | identical |

Per page — only page 0 moves, and only its escalated leg:

| page | before | after |
| --- | --- | --- |
| 0 | `0.9559543230016313`, a=586, e=**27** | `0.9575163398692811`, a=586, e=**26** |
| 1 | `0.9705882352941176`, a=825, e=25 | identical |
| 2 | `0.9673629242819843`, a=741, e=25 | identical |

## 2. The formula — read, not assumed

`src/iladub/etkl/document.py:1757-1760`:

```python
asserted = sum(rep.asserted for rep in pages)
escalated = sum(rep.escalated for rep in pages)
denom = asserted + escalated
score = 1.0 if denom == 0 else asserted / denom
```

`CompilationReport.asserted`/`.escalated` are **word counts, not cell counts**. For a ruled band the
escalated leg is literally the band's unread words — `src/iladub/etkl/compile.py:1044-1046`:

```python
tokens = sum(len(ln.words) for ln in band.lines)
asserted_total += n
escalated_total += max(0, tokens - n)
```

So stem page 0's denominator **is** band 2's word count: 586 asserted cells + (613 − 586) escalated
= 613 before, 612 after. That is why one word moves the document score at all.

## 3. The weld, in full

The entire diff of `page_bands(STEM, p)` across all three pages, both commits, is one line:

```
-- band 2: lines=61 words=613          →   -- band 2: lines=61 words=612
   L0 n=2 ['Friday, 31', 'July 2026']  →      L0 n=1 ['Friday, 31 July 2026']
```

Page 0, band 2, line 0 — the date banner above the shipping stem. R154's `_row_dividers` change
declined an interior boundary that was chopping it, so two word fragments became one word.

**That line is not a cell at either commit** (`grep "July 2026"` over the graph's `cellText`
literals returns 0 hits at both), i.e. it is unread ink counted in the escalated leg. Welding it
removed one token from the denominator and nothing from the numerator.

**Cell text changed nowhere.** A diff of all 2047 `(cell URI, cellText)` pairs is 0 lines; a diff of
all 2104 `cellText` literals sorted is 0 lines. Pages 1 and 2 are word-for-word identical, which is
why only one weld example exists — there are no others on this document.

This is the same mechanism `20cc5b8` itself ruled on for apple page 0 in
`tests/etkl/test_decisionlog.py` (`0.1170 → 0.1198`, *"welding two fragments into one cell removes
an ink token from the count … a smaller denominator is not better reading"*).

## 4. The R154 loop recorded it

```
$ git log -1 --format=%B 20cc5b8 | grep -n "gstem"
34:    Document scope, both modes: gstem .96546->.96589, gcap 1.0, cbh .90466->.90919,
37:    WHAT THIS DOES NOT LICENSE. The score rises are partly a DENOMINATOR effect (welding
```

The move was measured, published in the commit message, and correctly characterised — one line
below, that same message warns the rises are *"partly a DENOMINATOR effect."* The loop then
re-baselined `tests/etkl/test_decisionlog.py`, `tests/etkl/test_kind_gate_is_load_bearing.py` and
`tests/etkl/test_typing_equiv.py`, each with a written ruling. **All three are non-corpus.** The one
test that pins this exact number is corpus-gated, skips in CI, and was never touched.

**What that reframes.** The earlier reading — recorded in R174's row as *"the loop that moved it
re-baselined every OTHER pinned score it touched"* — implied the loop may not have seen it. It saw
it. The gap is not attention; it is that **a test nothing runs cannot be re-baselined by a careful
author**, which is precisely [[R173]]'s CI-visibility half. R174 is the worked instance of it.

## 5. Method, and what it cost

Delegated to a subagent in its own `git worktree` (separate context), running the two compiles
directly rather than the suite. Both probes verified `iladub.__file__` resolved **inside the
worktree** before any number was trusted — the venv's `_editable_impl_iladub.pth` otherwise points
at the main checkout's `src` and every probe silently measures `main`. Corpus symlinked, since
`corpus/` is gitignored. ~10 minutes, 50 tool calls.

The four ratios in § 1 and the two code citations in § 2 were re-verified in the controlling
session against the working tree, not taken from the agent's report.

## 6. What is NOT measured

- **Graph-wide triple equality.** Every `tab:EntryCell` node, every `(cell, cellText)` pair and
  every `cellText` literal is identical. The full merged graph was **not** compared triple by
  triple, so "the graph is byte-identical" is *not* claimed — only that every cell and its text is.
- **Whether the welded banner ink is emitted as an escalation candidate node.** It is inferred to be
  escalated ink from the arithmetic (`escalated = band words − asserted cells`) and from its absence
  among `cellText` literals. No `CandidateConcept` carrying the string was located.
- **Any other document.** stem only. `20cc5b8`'s other figures (cbh `.90466→.90919`, apple
  `.35560→.35870`, bfs `.34384→.34644`) are **quoted from its commit message, not re-run here.**
