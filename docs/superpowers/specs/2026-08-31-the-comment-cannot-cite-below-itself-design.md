# The comment cannot cite below itself — building `R139`'s instrument half

**Date:** 2026-08-31 · **Residue:** `R139`, disjunct (a) · **Branch:** `r139-downward-citation-lint`

**Doc impact: none.** No published surface changes: no owned term is added or re-commented, no
`owl:versionInfo` moves, nothing enters `mkdocs.yml`'s nav. The loop adds one test module, one
extractor, one shape, and edits four source comments. `CLAUDE.md` plan-rule 7 already states the
convention this enforces and is **cited, not re-derived**.

**Evidence this spec is written from:** the `R139` row in `docs/superpowers/residues-open.md` (the
2026-08-31 census, run at `794f518`), and the re-measurement at HEAD `9198300` recorded in §3 below.
The census is **cited, never restated** — §3 measures only what changed since it ran.

---

## 1. What this closes, and what it does not

`R139` has two disjuncts. **(b) — the convention** shipped 2026-08-25 as `CLAUDE.md` § Plan authoring
discipline rule 7. **(a) — the instrument** is unbuilt, and rule 7's own text says so: nothing in the
suite catches the next instance. This loop builds (a), in the one scope the census proved it can hold,
and **strikes `R139`**.

The maintainer ruled on 2026-08-31 to build rather than refuse. The case, in one line: the class has
now bitten **three times in a fortnight**, and twice the author knew rule 7 and was applying it at
that moment.

## 2. The rule — stated once

> **In a tracked `.py`, `.ttl` or `.rq` COMMENT line, a `:NNN` token whose referent is the file the
> comment is in, and whose `NNN` is greater than the comment line's own number and not greater than
> that file's line count, is REFUSED.**

Everything below is that sentence's terms, its extraction, and its oracles. It is derived here and
**cited** elsewhere (plan-rule 6).

Three terms need definitions, and each is a *reading convention* — not a tolerance:

- **Comment line** — a line whose first non-whitespace character is `#`. True of all three
  extensions. **Why the restriction:** in *code*, `:NNN` is a slice, a format spec or a dict value,
  never a citation — `{"weight": 200}` is not a pointer to line 200.
- **Referent** — the file a `:NNN` points into. It is **this** file unless an explicit
  `basename.ext:MMM` anchor appears earlier in the same comment **paragraph**, in which case every
  later bare `:NNN` in that paragraph inherits that anchor. This is how a human reads the passage.
  **The unit is the paragraph — a code line or a contentless `#` line ends it — and not the
  contiguous block**, because the longest `#` block here is 122 lines and a block-scoped referent
  was measured leaking across one (§3).
- **Downward** — `NNN` strictly greater than the comment line's own number. An upward citation is
  outside the class: an edit *at* the comment cannot move a line above it.

The `NNN <= line-count` clause is the **EOF filter**: a bare number past this file's end cannot be a
line of this file, so it is a cross-file citation whose anchor the paragraph scope did not carry.

**The refusal names the remedy rule 7 already prefers** — cite the symbol, or the `grep` that finds
it — and never an allowlist. There is **no exemption mechanism**, deliberately; §4 is why that is
affordable.

## 3. Measurement at HEAD `9198300` — what the census's ladder yields today

The census ran at `794f518`, before its own `compile.py` repair landed. Re-run at HEAD, over all
**462** tracked `.py`+`.ttl`+`.rq` files, the ladder is:

| tier | hits |
|---|---|
| `:NNN` tokens on comment lines (slices/format-specs excluded by the token regex) | **76** |
| …downward | **10** |
| …within the citing file's own EOF | **7** |

Those 7 tokens sit on **4 comment sites**, and every one is re-measured by hand in §4. The census's
headline — *5 flagged, 4 real, 20% FP* — is reproduced modulo its own repair: the site it fixed
(`compile.py`'s `escalation-shapes.ttl` wiring) no longer carries a number at all.

**CORRECTED 2026-08-31, by the implementation's own falsification pass.** The first draft of this
section recorded *two* honest negatives — that neither the referent rule nor the comment restriction
fired on anything at HEAD. **The first is FALSE, and the measurement that produced it was made with a
defective instrument.** The probe's regex put its slice-exclusion lookbehind after an optional anchor
group, so the anchored branch could never match: `compile.py:878` was silently skipped rather than
resolved, and `datagrid.py`'s bare `:949` was suppressed by the EOF clause alone. With the shipped
two-branch lexicon:

1. **The referent rule IS load-bearing — 10 tree false positives depend on it.** Deleting the anchor
   inheritance turns the whole-tree oracle RED with ten hits, every one an explicit cross-file
   citation: `compile.py:42` (`regions.py:88-98`), `:402` (`feed.py:586`), `:469`/`:476`
   (`datagrid.py:622-623`, `:626`), `document.py:131` (`feed.py:586-587`), and both anchors on
   `tests/arc-m19-false-edge-leak.ttl:13-14`. **O3 is therefore tree-scoped, not fixture-only** —
   §7 is corrected to match.
2. **The comment restriction fires on nothing at HEAD** — scanning every line yields the same 7.
   It is kept for the reason stated in §2, not for a count. This negative stands, re-measured.

**The referent unit is the PARAGRAPH, not the contiguous comment block** — and the correction came
from the same pass. A block-scoped referent leaked across a contentless `#` line in `compile.py`:
the anchor `feed.py:586` at `:402` was inherited by `:1083` eight lines later, **hiding a real
instance**. The longest contiguous `#` block in this tree is **122 lines**
(`tests/arc-manifest.ttl:644`), so block scope is not a near-miss but the wrong unit. A paragraph —
ended by a code line or a contentless `#` — is what a reader resolves against.

Both corrections are recorded here rather than quietly applied: the census this spec was written
from was run with the same defective anchor branch, so its "paragraph-scoped referent" was never
actually exercised, and a reader of `R139`'s row should know that.

## 4. The four sites, and what the loop does to each

Every one is re-measured at HEAD. **None is a wrong citation today** — the class is a *hazard*, and
three of the four are correct-and-fragile. That is exactly why prose has not held.

| site | token(s) | measured at HEAD | disposition |
|---|---|---|---|
| `src/iladub/etkl/document.py:138` | `:1324` | `grep -n MEMBRANE_HEALTH_RQ` → `139`, `1324`. **Correct** | **Repair** — cite the grep, drop the number |
| `src/iladub/etkl/document.py:1206-1207` | `:1536`, `:1740` | `grep -n "DEC.supersedes"` → `1536`, `1740`. **Correct** | **Repair** — the comment *already carries that grep in the same sentence*; promote it and drop the numbers |
| `src/iladub/etkl/compile.py:410-411` | `:1083`, `:1124` | Neither is a citation: they are the *quoted historical values* that rotted, in the record R139's census wrote | **Re-word** — write `line 1083` / `line 1124`. They were never pointers, so the pointer syntax was wrong for them |
| `tests/arc-m19-false-edge-leak.ttl:13` | `:17`, `:48` | **Both ARE line citations — into other files.** They are the suffixes on two `prog:oracleArtifact` values, `vocab/shapes/dec-shapes.ttl:48` (`:41`) and `vocab/shapes/risk-shapes.ttl:17` (`:55`). The anchor naming them sits on the *previous* comment line as the extension-less stems `dec-shapes` / `risk-shapes` | **Re-word** — write the two anchors in full (`dec-shapes.ttl:48`, `risk-shapes.ttl:17`), which is both *more* accurate and resolvable by §2's referent rule |

**This is why no allowlist is needed, and it is the load-bearing design choice of the loop.** A
suppression rule for the last two — "past tense", "the word *suffix* nearby", an extension-less stem
matcher — would be a tuned lexical constant, which `CLAUDE.md` §8 calls prima facie evidence of a
misclassified decision. The alternative is better on its own terms: in a source comment `:NNN` means
*line NNN of the file last named*, so a comment that uses it for a quoted historical value, or that
leaves its anchor un-spellable, is **saying less than it means** — and correcting it costs four edits
once. Both re-wordings make the comment more accurate, not merely lint-clean; that is the test of
whether a refusal without an escape hatch is honest.

**One of these four was mis-classified in this spec's own first draft**, from reading the comment
instead of measuring what it referred to (`:41` and `:55` of that file settle it). Recorded rather
than silently corrected: plan-rule 2 is the rule it broke, and the spec is the artefact it was caught
in — which is where it is cheapest.

**Rule 7's own trap applies to two of these edits.** `document.py:138` and `:1206-1207` cite lines
below themselves; the edits that repair them must be **re-measured after the write**, and the
repaired form must contain no number to invalidate. The lint itself is the check, which is the point.

## 5. Classification under the neurosymbolic gate (`CLAUDE.md` §8)

The decision splits, and the split follows the house pattern already shipped for documentation
governance (a procedural extractor feeding a declarative membrane):

- **PROCEDURAL — the extractor.** Turning arbitrary source text into typed facts
  `(file, comment-line, cited-line, referent, file-length)` is **raw extraction**, §8's first named
  irreducible case. There is no RDF to be declarative over until it has run, and no lexical scan of
  free text is expressible as a query over a graph that does not yet exist. **It decides nothing** —
  it carries no threshold, no tolerance, and no comparison; it reports what a token *is* and where it
  sits. Each such statement is asserted in the module docstring, as §8 requires of every PROCEDURAL
  instance.
- **AXIOM, constraint form — the refusal.** "Referent is this file **and** cited > citing **and**
  cited ≤ length" is a **membrane**: it validates what may cross into the tracked tree. Closed world,
  therefore **SHACL**, per §8's split. It never derives; it refuses.

**No NEURAL component.** Nothing here is perceptual or underdetermined: every term in §2 is decidable
by exact integer comparison and string equality over extracted facts.

**The one argument that could have sent this to PROCEDURAL wholly — and why it fails, measured.**
§8's PROCEDURAL class names *decidable exact arithmetic*, and two integer comparisons qualify; the
repo's most recent sibling in this genre, `tests/test_residue_register_integrity.py` (`R137`,
2026-08-30), is pure Python + regex on exactly that ground. The objection to going semantic is that a
SHACL membrane needs a vocabulary, and minting published ontology terms for *"a line-number token in a
comment"* would put a non-domain on a published surface to serve one test.

**That objection is refuted by an existing artefact.** `vocab/shapes/doc-governance-shapes.ttl:8-9`
states its own namespace's status in the file: *"The dg: namespace is repo-internal governance
vocabulary. It is NOT part of the published iladub/etkl/dec/risk ontologies and is NOT registered at
w3id."* `grep -rln docgov vocab/ontology/` returns **nothing** — it is declared in no ontology. So a
repo-internal membrane vocabulary is an established, zero-published-cost move here, and with the cost
gone the §8 default stands unopposed. This loop mints a sibling, `sc:`, on the same terms and with the
same disclaimer in its own header.

**Recorded so a reviewer can attack it:** if the maintainer rules that repo-internal SHACL namespaces
should not proliferate, the fallback is `R137`'s form and the extractor is unchanged — only §6's shape
is replaced by an assertion in the test module.

## 6. Interfaces — signatures and invariants, not bodies

**Extractor** — `tests/source_citations.py`, with `sc:`'s terms declared in
`vocab/internal/srccite.ttl`. **That siting was MEASURED, not chosen**: a shapes file naming
`sc:Citation` with the class declared nowhere is refused by `etkl:VocabularyArtifactShape`
(*"names https://w3id.org/iladub/srccite#Citation, which no owned vocabulary declares"*), and
`vocab/internal/` is where this repo already puts unregistered vocabularies — `docgov.ttl` states
the rule in its own header. See §6's seam note for the four other pinned counts this moves. The house convention, measured across all seven
tree-integrity modules: the enumerator lives in a **non-`test_`-prefixed module under `tests/`** (so
pytest does not collect it) and the `test_*.py` module imports it (`pythonpath = ["."]` plus an empty
`tests/__init__.py` make `from tests.source_citations import …` the import form). **There is no
reusable `.py` enumerator** — `artifact_files()` is `.ttl`-only, `tracked_markdown()` is `.md`-only,
`query_files()` is a `vocab/queries` glob — so this module writes its own `git ls-files -z`, copying
the form at `tests/artifact_terms.py:62-67` rather than inventing one.

```
citations(paths: Iterable[Path]) -> Graph
```

- **Invariant E1** — emits exactly one node per `:NNN` token found on a comment line, carrying the
  citing file, the citing line, the cited line, the resolved referent, and the citing file's line
  count. **Never filters.** Selection is the shape's job, and an extractor that pre-filters cannot be
  falsified independently of the constraint it feeds.
- **Invariant E2** — the referent of a bare token is the citing file unless an explicit
  `basename.ext:MMM` anchor precedes it *within the same comment PARAGRAPH*; a code line or a
  contentless `#` line ends the paragraph and resets the referent (§2).
- **Invariant E3** — a token preceded by `[` (a slice) or matching a format spec is not a token.
  This is *lexical exclusion of non-citations*, not filtering of citations.

**Shape** — `vocab/shapes/source-citation-shapes.ttl`, prefix `sc:`
(`https://w3id.org/iladub/srccite#`), sited and disclaimed exactly as `doc-governance-shapes.ttl` is.
Validated with `inference="rdfs", advanced=True` (`sh:sparql` carries the arithmetic), matching
`tests/test_doc_governance.py:33-36`.

- **Invariant S1** — refuses exactly the nodes satisfying §2, and no others.
- **Invariant S2** — the refusal message names the offending `file:line -> :NNN` **and** the remedy
  (symbol or `grep`), because a lint whose message does not say what to do gets suppressed.

**Test module** (one new module under `tests/`):

- **Invariant T1** — runs over the **tracked tree**, and carries **no pytest marker**: none of the
  seven tree-integrity modules has one, and CI runs bare `pytest -q` (`.github/workflows/ci.yml:25-26`)
  with no `addopts`, so the genre is always-on.
- **Invariant T2** — green at HEAD **only after** §4's four edits land. It must be RED before them.

**THE SEAM THE IMPLEMENTER MUST MEASURE, before writing the shape file** (plan-rule 3 — the seam, not
the answer): adding a `.ttl` to `vocab/shapes/` puts it inside `artifact_files()`, the population
`tests/test_artifact_terms.py` and `tests/test_artifact_declarations.py` validate. **Measure whether
those two tolerate a new repo-internal namespace** — `doc-governance-shapes.ttl` is already in that
population and green, which is evidence but not proof, and `test_artifact_terms.py:56` pins the
population size as an **exact arithmetic identity (`== 144`)** that a new file changes. Expect to
re-measure that constant, and to say so in the commit.

## 7. Oracles — what falsifies each piece

Per plan-rule 4, each is inverted and shown failing.

| oracle | RED how | GREEN when |
|---|---|---|
| **O1 — the lint bites** | Add a throwaway comment to any tracked `.py` citing a line below itself and within EOF; the test fails naming it. Remove it; green | the four §4 edits have landed and no new instance exists |
| **O2 — the EOF filter is load-bearing** | Delete the `cited <= length` clause; `vocab/queries/arc-position.rq:65` (cites `:139-146`, file is **84 lines**) and `datagrid.py:733` re-appear as false positives | with the clause, both are silent |
| **O3 — the referent rule is load-bearing** | Delete `paragraph_referent = Path(anchor).name`: the whole-tree oracle goes RED with **10** cross-file citations (§3.1 names them), and two fixture oracles fail with it. **Tree-scoped — corrected from the draft, which called it fixture-only on a measurement taken with a defective regex** | with the rule, each anchored token is attributed to its anchor |
| **O4 — upward is out of scope** | A comment citing a line *above* itself must NOT flag. `document.py:1747-1752` carries six such tokens; if any flags, §2's "downward" clause is wrong | those six stay silent |

**O2, O3 and O4 all run against the real tree** and name their live subjects, so none can pass
vacuously. O2 and O3 additionally carry fixture arms, so that a future tree which happens to contain
no such citation cannot make them silently vacuous.

## 8. What this loop deliberately does NOT do

- **`docs/**` is out of scope, permanently as far as this instrument goes.** The census measured
  71–99% FP there: markdown in this repo is a citation *narrative* whose referents cross heading
  boundaries, which no bounded lexical window resolves. **The second of R139's three instances was in
  `.md` and this lint would not have caught it** — that is a stated limit, not an oversight, and it
  is the reason the row is struck on disjunct (a) only.
- **No `.md` prose form** (*"at lines 12, 133"*) is read. The census scored it **0/44**: it almost
  always names lines of a compiled PDF, not of a source file.
- **No exemption/allowlist mechanism** ships (§4).
- **No historical sweep.** Only the tree at HEAD is measured; git history is not scanned.

## 9. Residue raised by this spec

One, and it is the `.md` half above: **the class is not Python-specific, one of its three measured
instances was in markdown, and this instrument cannot see that instance.** It is recorded as the
successor to `R139` rather than left inside a struck row.
