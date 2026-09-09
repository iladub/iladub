# Handoff — the code-scope figure gate ships HARD, and [[R196]](a)'s own answer is refuted

**Topic:** action **5a** of `docs/superpowers/2026-09-09-a-figure-at-the-end-of-a-sentence-handoff.md`
is taken in full: [[R196]](a) settled as a design question, then the walk and the gate extended in ONE
change with the ten findings repaired in it. [[R189]] **CLOSED**. [[R196]] amended — (a) refuted, (b)
still deferred and now measured at 0 on a second corpus. [[R197]] raised.

**Written 2026-09-09**, part 5 first.

**Doc impact: none.**

---

## 5. The next concrete action

### 5a. ASSERTED — run [[R192]]'s census; it is now one filter and it has been carried unrun for four loops

*"How many Evidence documents restate a corpus figure they did not themselves measure?"* If the answer
is "the capability line and nothing else", R192 is one bad sentence, not a class — and `docs/superpowers/**`
is exempted from the figure derivation on the strength of that being true.

Mechanical, and the outcome is known to be a number rather than a judgement: one filter over
`dg:FigureOccurrence` + `dg:blockDated` restricted to `docClass "evidence"`. **Two things this loop
changed about it, both of which must be honoured or the count is wrong:**

1. **Exclude filename-dating.** [[R196]](b) measured **24** evidence occurrences whose block is dated
   ONLY by a date inside a letter-bearing token. Some are honestly dated (a file citing
   `2026-09-05-r173-5a-rebaseline.md`); the ones citing a corpus PDF carry the document's date, not
   the reading's. Counting them as dated under-counts R192.
2. **The population moved again.** The predecessor loop's `_DECIMAL` widening took tracked markdown
   from 497 to 514 occurrences, all `evidence`.

### 5b. PROPOSED — that [[R194]] arm (1) should be CLOSED as unnecessary, not built

Arm (1) is a mention-vs-report reader: distinguishing a *report* of a figure from a *mention* of one.
The predecessor loop supplied its population (11) and declared its stated blocker gone. **This loop
shrank that population to 4 and then repaired all four without the reader** — the prose restriction
removed 6 mentions mechanically (they were fixture literals in code, not prose at all), and the
remaining 4, in this gate's own docstrings, were repaired by *dating* them, which is true, cheap and
what [[R187]] prescribes anyway.

**Why proposed and not asserted:** the claim is that dating a mention is always available and always
honest, and it rests on four instances in one file. **It fails cheaply and visibly:** the first mention
somebody cannot honestly date is the counter-example, and it will arrive as a red gate naming its own
file and line, not as a silent wrong answer. If that never happens, the reader was never needed.

### 5c. Do NOT build [[R197]] or [[R196]](b) on today's evidence

Both are measured at essentially zero on every corpus the gate reaches — R197 at 1 false positive and
0 findings across 203 `.ttl`/`.rq` files, R196(b) at 0 across every `.py` prose block and 0 in
`docs/wiki/**`. Building either now is calibrating an instrument against a population of zero, which
is [[R188]]'s subject taken from the wrong end. Both rows say what evidence would change that.

---

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the design question and its refutation | `docs/superpowers/specs/2026-09-09-a-claim-lives-in-prose-design.md` | §1 why the candidate boundary loses a finding; §2 the region/boundary split, stated ONCE; §3 why `.py` only; §6 the licence for HARD |
| the loop record | `docs/superpowers/2026-09-09-a-claim-lives-in-prose.md` | §4 the RDFS entailment that had to be measured; §5 the ten repairs and the falsification transcript |
| the instrument | `tests/docgov_extract.py`, `prose_regions_py` / `prose_blocks_py` | that it is `tokenize` + `ast` and carries no constant; why the `#` is blanked rather than the line dropped |
| the gate | `tests/test_doc_governance.py::test_no_source_file_states_an_undated_reading` | the pre-repair census is in its docstring — that is the licence, not decoration |
| the pin against re-widening | `tests/test_docgov_extract.py::test_a_date_in_a_neighbouring_paragraph_does_not_date_a_docstrings_figure` | this is what goes RED if someone re-adopts R196(a)'s answer |
| the amended rows | [[R189]] in `residues-closed.md`, [[R196]] and [[R197]] in `residues-open.md` | read the rows, never the index lines |

## 2. What changed

One branch, `r196a-a-claim-lives-in-prose`, off `5cf1084`.

- **Extractor:** `prose_regions_py`, `prose_blocks_py`, `tracked_python`; `_figure_facts` takes
  **units** instead of text; `extract()` walks tracked `.py`. `is_dated`, `denotes`, `_DECIMAL`,
  `separating_precision`, `blocks` **untouched**.
- **Vocabulary:** `docgov:SourceFile` declared; `docgov:docClass`'s `rdfs:domain` removed (measured
  reason in the term's own comment).
- **Shape:** `dg:SourceFileShape` + 1 positive and 3 negative tests.
- **Query:** `docgov-undated-figure.rq` **unchanged** — the AXIOM already reached the new class.
- **Gate:** `code` is HARD; the old non-wiki warning narrowed to the classes neither gate covers.
- **Ten repairs**, all by dating; **no figure's value edited**; **no exemption list introduced**.
- **Census chain:** `test_artifact_terms.py` 66→67 and 71→72, both moved by the one new term, surplus
  set unchanged (the third assertion holds it — measured, not reasoned).

Governance suite: `test_doc_governance.py` + `test_docgov_extract.py` + `test_docgov_queries.py` +
`test_docgov_shapes.py` **59 passed**; `test_artifact_terms.py` 18 passed;
`test_residue_register_integrity.py` 6 passed.

## 3. What was decided, and where that decision is recorded

- **The block stays the closure boundary in code; the prose REGION is what changes.** Spec §1-§2 and
  [[R196]]'s amended row. Ground: the candidate loses `test_datagrid.py:1085`, a real finding.
- **`test_adoption_document.py:369` is a finding, not a false positive.** Spec §1.1 and the loop
  record §1.1. Ground: the dates two paragraphs down date *later* readings, and the phrase that dates
  these two is "before this loop". **This is a judgement overturning the predecessor loop's hand
  census, not a measurement** — it is argued from the rule the shipped gate enforces.
- **HARD, not a warning.** Spec §6. Ground: the pre-repair census, plus the fact that the honest
  repair (dating) was available for all ten, so no exemption was needed.
- **`.py` only.** Spec §3, [[R197]]'s row. Ground: 0 findings across 203 `.ttl`/`.rq` files.
- **`docgov:docClass` loses its `rdfs:domain`.** The term's own `rdfs:comment` and
  `test_a_source_file_is_not_entailed_into_a_document`. Ground: measured entailment failure.

## 4. Unverified or assumed

- **The full suite is running at the time of writing and has not reported.** The governance, terms,
  shapes and register files are green; the whole-suite run and CI are the checks that have not. It
  takes roughly 45-60 minutes here.
- **The reclassification in §3 bullet 2 is a judgement.** It changes the census's headline from
  4 findings / 13 false positives to 6 / 11, and therefore the ratio the HARD disposition is argued
  against. The disposition does not *depend* on it — all ten were repaired either way — but a reader
  who rejects the reclassification should read the licence as 4/6, not 6/4.
- **`prose_regions_py` is verified on the live tree and three fixtures, not proved.** Docstrings are
  taken for Module / FunctionDef / AsyncFunctionDef / ClassDef only; a string literal that is prose by
  intention but not in a docstring position (a module-level constant holding documentation, say) is
  invisible to the walk. No instance was measured; none was looked for exhaustively.
- **An unparseable `.py` file yields no claims.** `prose_regions_py` returns `[]` on `TokenError` /
  `SyntaxError` rather than raising. Honest failure by the module's convention, but it means a file
  that stops parsing silently leaves the gate — nothing reports that today.
- **The `#`-blanking gives a comment run markdown's paragraph structure**, and that is a design choice
  made in this loop, pinned by one test on one fixture. It was not measured against the live tree as a
  separate variable: the census figures quoted everywhere include it.
- **`docs/wiki/concepts/doc-governance.md` says nothing about the figure gate** — it did not before
  this loop either ([[R187]] shipped the gate without touching it). Not repaired here; not a
  regression this loop caused.
