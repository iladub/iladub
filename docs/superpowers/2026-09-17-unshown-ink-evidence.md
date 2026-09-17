# Evidence — the ink the page does not show (R213's term)

**Serves:** prog:criterion:etkl:02 — graincorp-capacity.

**Date:** 2026-09-17. **Doc impact: none.**

Every measurement below was run on branch `the-ink-the-page-does-not-show`, cut from `main` at
`96009f5`, with `./.venv/bin/python` (the interpreter `tests/test_corpus.py` names). The probe is
`scripts/ink_contrast_probe.py`; it reads nothing the shipped pipeline reads and writes nothing.

The probe's containment rule, stated because it differs from R213's and the difference shows in
E1: a char sits on the **topmost filled rect whose box contains the char's centre**
(`page.rects` filtered to `fill`, later rects painting over earlier ones); a char on no filled
rect is scored against **white**. Colours are normalised from pdfplumber's 1-, 3- and 4-component
forms; WCAG 2.2 relative luminance and contrast ratio `(L1+0.05)/(L2+0.05)`.

---

## E1 — replication: the luminance-gap band is empty, and the 110 are the same 110

```
$ ./.venv/bin/python scripts/ink_contrast_probe.py --gap 'corpus/*/*.pdf'
chars on a filled rect: 25925   all chars: 59705
min gap 0.00648 max 1.0
largest empty band: 0.42174 (0.00648, 0.42822)
gap<=0.0065: 110 docs: [('graincorp-capacity-2026-08-04.pdf', 0)]
their glyphs: [('0', 110)]
next 5 sorted gaps above that: [0.4282, 0.4282, 0.4282, 0.4282, 0.4282]
off-rect gap min 0.7704 count under 0.2: 0
```

R213's amendment is **replicated by an independent implementation**: 110 chars, all `0`, all on
graincorp-capacity page 0, separated from every other char in the corpus by an empty band. The
band this probe measures is **0.42174 wide** where R213 recorded 0.1935, and the visible cluster
starts at **0.4282** where R213 recorded 0.2000; the containment rule above is the likely cause and
the disagreement is recorded rather than resolved — it does not bear on anything below, because
§ E2 refutes the whole instrument class.

## E2 — REFUTATION: the cited-standard threshold fires on 858 visible glyphs

WCAG 2.2's published minimum contrast for large text is **3:1**. It is the one constant here that
would not be tuned — an external normative source, cited rather than chosen, which is the move this
repo makes everywhere else. It is refuted on the corpus:

```
$ ./.venv/bin/python scripts/ink_contrast_probe.py 'corpus/*/*.pdf'

== cbh-stem-2026-08-03.pdf  pages=1 chars=7518
   on a filled rect: 2039  | ratio<3: 780  ratio<4.5: 780
   on-rect ratio min=1.6887 max=16.0091
   glyphs under 3:1 -> [('e', 100), ('m', 64), ('t', 60), ('o', 52), ('i', 52), ('T', 48), …]
   their fg/bg sample: (1.0, 1.0, 1.0) on (0.6, 0.8, 1.0)  ratio=1.6887

== graincorp-capacity-2026-08-04.pdf  pages=1 chars=1560
   on a filled rect: 1449  | ratio<3: 188  ratio<4.5: 188
   on-rect ratio min=1.0856 max=16.1908
   largest on-rect gap: (10.9966, (2.8773, 13.8739))
   glyphs under 3:1 -> [('0', 110), ('Y', 78)]
   their fg/bg sample: (0.062745, 0.2, 0.352941) on (0.113725, 0.168627, 0.313726)  ratio=1.0856

== graincorp-stem  on-rect 7840 | ratio<3: 0     == apple  on-rect 3987 | ratio<3: 0
== bfs            on-rect 4615 | ratio<3: 0      == ons    on-rect 5731 | ratio<3: 0
== who            on-rect  264 | ratio<3: 0      (all 264 at ratio 3.2241)
```

**858 glyphs fall under WCAG's 3:1 line and every one of them is ordinary visible ink:**

- **78 on graincorp-capacity** — a green `Y` (`(0.255, 0.678, 0.286)`) on **white**, ratio
  **2.8773**. A tick in a "yes/no" column, printed, legible, and 0.12 below the line.
- **780 on cbh-stem** — **white text on pale blue** `(0.6, 0.8, 1.0)`, ratio **1.6887**, lower than
  some of the invisible navy-on-navy would be against a different backdrop. It is the document's
  heading band; it reads fine on screen.

Same probe, same corpus, the other instrument:

| glyph population | WCAG ratio | luminance gap | a reader sees it |
| --- | --- | --- | --- |
| gcap navy-on-navy (110 × `0`) | 1.0856 | 0.00648 | **no** |
| cbh white-on-pale-blue (780) | 1.6887 | 0.4282 | yes |
| gcap green `Y`-on-white (78) | 2.8773 | 0.686 | yes |

**The two instruments disagree about 858 glyphs, and only one of them is right.** Which one is
"right" is settled by looking at the page — that is, by a reading judgement, not by either
formula. So the choice of instrument is itself the tuned parameter, one level above the constant
CLAUDE.md § 8 forbids, and no amount of care in picking the number removes it. This is a stronger
result than "the threshold is tuned": it says the class of colour-distance rules cannot be made
safe by citing a standard.

## E3 — no palette rule separates them either

```
$ ./.venv/bin/python scripts/ink_contrast_probe.py --palette corpus/ag-trade/graincorp-capacity-2026-08-04.pdf
filled rect fills: [((1.0,1.0,1.0), 208), ((0.113725,0.168627,0.313726), 108),
                    ((0.345098,0.34902,0.356863), 78), ((0.768627,0.913725,0.917647), 75),
                    ((0.258824,0.262745,0.266667), 27), ((0.0,0.0,0.0), 16)]

backdrop (0.113725,0.168627,0.313726) -> glyph colours [((1.0,1.0,1.0), 130),
                                                        ((0.062745,0.2,0.352941), 110)]
backdrop (1.0,1.0,1.0)               -> glyph colours [((0.113725,0.168627,0.313726), 560),
                                                       ((0.254902,0.678431,0.286275), 78),
                                                       ((0.082353,0.27451,0.478431), 37)]
backdrop (0.768627,0.913725,0.917647)-> glyph colours [((0.0,0.0,0.0), 645)]

H1 per ink colour — is it also a rect FILL / a rect STROKE?
   ink (1.0,1.0,1.0)                x130 on navy:      fill=True  stroke=False
   ink (0.062745,0.2,0.352941)      x110 on navy:      fill=False stroke=False   <- the hidden ink
   ink (0.113725,0.168627,0.313726) x560 on white:     fill=True  stroke=False
   ink (0.254902,0.678431,0.286275)  x78 on white:     fill=False stroke=False
   ink (0.082353,0.27451,0.478431)   x37 on white:     fill=False stroke=False
   ink (0.0,0.0,0.0)                x645 on pale blue: fill=True  stroke=True
rect stroke colours: [((0.0,0.0,0.0), 512)]
```

Three structural hypotheses, all refuted on the page they were invented for:

1. *"The hidden glyph is painted in a colour the author uses to PAINT, not to WRITE."* — refuted in
   **both directions** on one page. The hidden navy `(0.063, 0.2, 0.353)` is **not** any rect fill
   and **not** any stroke colour; meanwhile the three ink colours that ARE also rect fills — white,
   the darker navy, and black — account for **1335 perfectly visible glyphs**. Painting with a
   colour and writing with it are the same act to this author.
2. *"A backdrop that carries hidden ink carries no other ink."* — the navy backdrop carries **130
   white glyphs** (visible labels) beside the 110 hidden ones.
3. *"A glyph is hidden when it is nearer its backdrop than to any other ink colour used on that
   backdrop."* — arithmetic over the census above, not a separate run: it classifies gcap's four
   populations correctly, but separates the 130 white-on-navy glyphs from the hidden ones by
   **0.003** in RGB distance (1.392 to the nearest ink against 1.395 to the backdrop), and it is
   **undefined** on cbh's pale-blue backdrop, which carries exactly one ink colour. A rule that is
   undefined on one corpus document and decides another by 0.003 is not a rule.

Recorded and stopped there: CLAUDE.md § 8 as amended 2026-09-17 allows a reading judgement **one**
geometric attempt, and R213's own colour discriminator was it.

## E4 — the extraction seam the handoff prescribes moves the reading

The handoff's § 5c says carrying each glyph's colour "is the loop's real work". The obvious route —
pdfplumber's `extra_attrs` — **changes word segmentation**, because a word is split wherever an
extra attribute changes:

```
word-seg differs (plain vs extra_attrs=['non_stroking_color']), per page, whole corpus:
  bfs-population-bilan-2023.pdf   page 2:  310 -> 312
  ons-index-of-services-2026-02.pdf page 1: 388 -> 390
  ons-index-of-services-2026-02.pdf page 2: 290 -> 297
  ons-index-of-services-2026-02.pdf page 5: 429 -> 430
  every other page (23 of 27): unchanged
```

`geometry.extract_words` (`src/iladub/etkl/geometry.py:41-50`) is the single seam every reader goes
through — `compile.py:424`, `donation.py:130`, `datagrid.py:321,808` and nine `scripts/` — so
those 11 extra words would reach every downstream judgement on two of the seven documents, neither
of which has a single hidden glyph. **Any colour carriage must therefore be a separate reader**
(the `extract_rules` / `extract_hrules` pattern, `geometry.py:74,101`) and never a parameter on
`extract_words`. § 3 of the spec retires the requirement instead.

## E5 — the seam a per-cell fact must cross, measured

A band cell already carries its `Word` objects and loses them at one place:

- `regions.Cell` holds `words: tuple[Word, ...]` and derives `.text` from them
  (`src/iladub/etkl/regions.py:34-41`).
- `headers._grid_cells` (`src/iladub/etkl/headers.py:66-81`) flattens each cell to
  `(r, c, " ".join(texts))` — line 80 appends `w.text` with the `Word` itself in scope one line
  above.
- `celltype.grid_evidence` (`celltype.py:138-150`) consumes those 3-tuples, and
  `celltype._cell_datatype` (`celltype.py:81-93`) sees **only the text**.
- Four sites construct a `Word`: `geometry.py:52` (the text layer), `:357` (the ruled-cell
  regrouping), `:498` (the column merge), `ocr.py:44`.
- The same 3-tuple shape is consumed by `unitmarker.py:59`, and `grid_evidence` has six callers
  (`matrix.py:134`, `rowheaders.py:33`, `orientation.py:36,59`, `headers.py:111`, plus
  `gridregion.py`'s own same-named function at `:34`, which is a different function).

So a per-cell fact that is not derivable from the text has exactly one narrow place to cross:
`headers._grid_cells`'s tuple, and the `grid_evidence` signature that reads it.

## E6 — no colour is read anywhere in the shipped reader

```
$ grep -rn "non_stroking_color\|stroking_color" src --include='*.py'
(no output)
```

Confirms the handoff's § 5c. `page.rects` is used once, for geometry (`datagrid.py:184`).

## E7 — the rendered pages, looked at, and a second witness on gcap

The only ground truth this thread has ever had is a person looking at the page. Both contested
populations were rendered at 220 dpi (`page.crop(...).to_image(...)`) and read:

- **cbh-stem's pale-blue band** — the white-on-pale-blue glyphs are the port codes `ALB`, `ESP`,
  `GER`, `KWI` in the row-label column of the stock table, beside tonnages of 129,183 / 25,013 /
  160,198 / 170,878. **Low contrast and plainly legible.** They are load-bearing data, and WCAG's
  3:1 line would have typed all 780 of them as unshown (E2).
- **graincorp-capacity's dark cells** — **visually empty**, exactly as R213 records. The green `Y`
  and black `N` in the flag sub-column beside them are crisp.

Reading the render also exposes a signal that is on the page and needs no colour at all. Every port
occupies two sub-columns — a tonnage and a `Y`/`N` availability flag — and:

```
hidden: 110   Y/N glyphs: 195
hidden cell -> nearest Y/N to its right: {'N': 110}   no Y/N found: 0
Y/N glyph -> a hidden glyph within 120pt to its left: {('Y', False): 80, ('N', True): 110, ('N', False): 5}
```

**110 of 110** hidden glyphs sit immediately left of an `N`, **0 of 80** `Y` flags have a hidden
glyph beside them, and the implication runs **one way only**: 5 `N` flags have no hidden glyph
beside them — the genuinely empty cells, of which R213 already names one (Fisherman Islands,
2025/26, September 1st Half).

This is a **second witness for the O2 set identity on this document, and it is not the general
rule.** It is contract knowledge about one table's shape: cbh has no flag column, and neither does
any other corpus document. Recorded because a reviewer will think of it, and because it makes gcap's
110 checkable without running a worker at all — *hidden ⟹ N* is measured; *N ⟹ hidden* is false.

---

## What this evidence does NOT establish

- **That a vision worker reads these pages correctly.** § 4 of the spec rests on it and nothing
  here tests it. cbh's 780 white-on-pale-blue glyphs are the named falsification.
- **That a render read by this session is a reader's judgement.** E7 is the closest thing here to
  ground truth and it is still an agent looking at a raster. R213's own rendering check
  (`2026-09-11-etkl-02-waits-on-r166-handoff.md` § 2) is the maintainer's, and it agrees.
- **The cost of rendering pages.** Not measured; § 5 names it as the plan's first measurement.
- **How many regions the corpus has**, and therefore the size of any per-region ask. Not measured
  here deliberately — the plan measures it at the call site (plan rule 3).

---

## Correction, appended 2026-09-17 by the review (RF4)

**E2's and E7's description of the cbh population is wrong**, and the review measured it:
`2026-09-17-unshown-ink-spec-review.md` § RF4.

```
cbh low-contrast chars by (ink, backdrop, ratio):
   ink=(1.0, 1.0, 1.0) on (0.588, 0.588, 0.588)  ratio=2.9601  ->  828 chars
   ink=(1.0, 1.0, 1.0) on (0.6, 0.8, 1.0)        ratio=1.6887  ->   24 chars
```

**828 of 852 are white on GREY at ratio 2.9601** — the four vessel tables' column-heading rows
(`VNA #`, `Vessel Name`, `Time Nominated`, …). Only **24** are the pale-blue port codes
`ALB`/`ESP`/`GER`/`KWI` at **1.6887**. E2 printed a one-row *sample* — the pale-blue one — beside the
count of the whole set, and E7 then narrated the whole set as the port codes.

The arithmetic of E2 is unaffected: 858 glyphs still fall under WCAG's 3:1 line and every one is
ordinary visible ink, so § 1.1's refutation of the colour-instrument class stands unchanged. What
changes is which glyphs O1 actually tests, and at what contrast.
