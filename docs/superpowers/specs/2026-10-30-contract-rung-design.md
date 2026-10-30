# A contract is compiled — the `contract` rung and its first criterion, contract:01 (design, 2026-10-30)

**Serves:** a new sixth rung, `contract` (the contract compiler), and its first criterion
`prog:criterion:contract:01`. Neither exists at `bbac3de` (`tests/arc-manifest.ttl:75-97`
declares five rungs; `tests/arc-shapes.ttl:59-60` admits only those five keys).

**Topic:** contract · **Date:** 2026-10-30

**Doc impact: increment.** The arc gains a sixth rung, so `docs/narrative/scope-evolution.md`
gains a `### contract` section. `vocab/ontology/` gains a new owned namespace (`ctr:`, § 6.2) and
a gUFO alignment module. `vocab/shapes/` gains one shapes file, and `vocab/queries/` gains one
derivation. Nothing the released vocabulary already says changes meaning. The narrative never
**does** state the rung count once: `scope-evolution.md:23` ("Four of the five are entitled…"),
which § 6.1 item 5 must also edit. Otherwise the "five" appears in dated records and in the sites
§ 6.1 edits.

**Status: DRAFT for the maintainer.** It writes up the 2026-10-30 rulings (§ 2). § 11 lists what
this spec does not decide. A companion spec in hdc-contract (the contract arbitration engine)
consumes this rung's output and comes after this one.

## 1. Goal

Four real GAFTA contract forms (Nos. 48, 49, 64, 100) compile, with no model, into contract holon
graphs. Every clause in them is a `ctr:Clause`, typed at the domain level where the domain module
can type it and at the gUFO level in every case. Every graph passes a SHACL membrane, and the
result is scored against a curated truth that iladub did not author.

## 2. Rulings this spec records (maintainer, 2026-10-30)

These were given in conversation and recorded in the hdc-contract handoff
`docs/superpowers/2026-10-30-handoff-rescope-specs.md` § 3 (hdc-contract repo). This spec is where
they first enter iladub.

1. **Principle.** If the domain is expressed formally and explicitly, the answer is on our side.
   Needing an LLM to sort it out means compilation failed at that step.
2. **Two repos.** iladub owns the **contract compiler**. hdc-contract owns the **contract
   arbitration engine** (HDC vectors, prototypes, the SME loop). Arbitration may later become an
   iladub feature, but not now.
3. **A sixth rung, `contract`, beside `tab`.** This is the decision that M6
   (`tests/arc-shapes.ttl:60`, *"A sixth rung is a decision, not an edit"*) requires, and this
   ruling is it.
4. **No residues.** When the domain module cannot type a clause, the compiler still asserts it at
   a coarser type from an **upper ontology, gUFO**. Nothing is left unasserted for a model to
   pick up inside iladub.
5. **Split of code.** The ingest that hdc-contract runs today (PDF → text → clause segmentation,
   `src/hdcc/ingest/extract.py`) moves into this compiler. HDC (torchhd, codebook, prototypes,
   vectors) stays in hdc-contract. **Item 5 is the session's reading of the ruling, not the
   maintainer's verbatim words. The maintainer should confirm it on review.**

## 3. Measured ground

All measurements were taken 2026-10-30 against hdc-contract `4b576f0` and its local compiled store
(`data/hdcc.sqlite`, table `clause_spans`, produced by today's segmenter). The scripts are under
the session scratchpad and are reproduced inline where they are short.

| # | claim | measurement |
| --- | --- | --- |
| M-a | the hero truth covers 4 forms | `grep -E '^"[0-9]+"' corrections/hero.yaml` → `"48" "49" "64" "100"` |
| M-b | hero.yaml has 49 `clause_type` rows: **40 primary**, 6 `also: true`, 3 `absent: true` | `grep -c clause_type:` → 49. The `also` and `absent` rows were listed with `grep -B3 'also: true\|absent: true'`. Their semantics are in `src/hdcc/compile/corrections.py:36-55` |
| M-c | the gold set cites **28 distinct clause refs**, all in forms 48/49/100 (none in 64) | `grep -o '"[0-9]* cl\.[0-9a-z]*"' eval/gold.yaml \| sort -u` |
| M-d | **all 28 refs resolve to exactly one segmented clause** | a per-ref `select count(*) from clause_spans where form_no=? and clause_no=?` loop printed no `unresolved` line |
| M-e | today's segmenter yields 30 / 26 / 27 / 30 clauses for 48 / 49 / 64 / 100 (113 in total) | `heading_match.py`: `form 48: 30 clauses` … |
| M-f | **an exact heading-to-label match** (casefold, whitespace collapsed, against the English `skos:prefLabel`/`altLabel` of the 37 `gco:ClauseType` concepts in hdc-contract `ontology/gco-concepts.ttl`) **types 39 of the 40 primary hero rows correctly** | `heading_match.py`. The one miss is 48 cl.7, heading `SALES BY NAMED VESSELS`: hero says `LoadingTerms`, the label match says `VesselNomination`, and the hero row is `needs_trader_check: true` |
| M-g | the 6 `also` rows (WarRisk ×2, Prohibition ×2, Demurrage, VesselNomination) **are not reachable from headings**. Each clause's heading names only its primary type | same run: each `also` clause got its heading type only |
| M-h | **111 of the 113 hero clauses** match some label. The 2 that don't are `EXPORT LICENCE -` and `SHIP'S CLASSIFICATION.` (stray trailing punctuation) | `coverage.py` |
| M-i | across **all 80 compiled forms, 1,770 of 2,011 clauses** match some label. **But 15 of those 80 forms fail the § 5 membrane (M-o), so 241 is not what would fall back.** Over the forms the membrane admits, with the § 5 segmenter: **67 forms, 1,723 clauses, 1,503 match a label, 220 fall back to gUFO only.** With today's segmenter ported verbatim, the figures are 65 forms, 1,672 clauses, 1,485 matches and 187 fallbacks | `coverage.py` and `variants.py`. **This is coverage, not correctness.** No truth exists beyond the 4 hero forms |
| M-o | **today's segmentation is not contiguous on 15 of the 80 forms.** 3 forms start above clause 1: 120 and 202 at 2, and 129 at 3. 14 forms, holding 311 clauses, have gaps. **The gaps are the segmenter's misses, not gaps in the forms.** For every missing number checked, the PDF text has the clause, written in a shape `_CLAUSE`/`_HEAD_TOKEN` do not take: <br>- no period after the number: `26 INSOLVENCY` (103), `12 PAYMENT` (62), `17 FUMIGATION` (202); <br>- a curly apostrophe: `SHIP’S` (62), `TRIBUNAL’S` (125); <br>- a colon: `GOODS: BIOMASS` (202), `GOODS: Rice` (120); <br>- sentence case: `Issues of Substantive Jurisdiction` (126), and all of 129. <br>**A missed clause is folded into the previous clause's body**, so today's output for those forms asserts wrong clause text | a `select form_no, clause_no from clause_spans` contiguity check, then a search of the `pdftotext -layout` text for each missing number (`gaps.py`). Re-measured 2026-10-30. The reviewer's "3 above 1, 14 forms / 311 clauses" holds, but the reviewer named only 120 and 129 |
| M-p | **the truth is mostly unconfirmed: 42 of the 49 hero rows are `needs_trader_check: true`.** That is 34 of the 40 primary rows, all 6 `also` rows, and 2 of the 3 `absent` rows. The 6 confirmed primary rows are 48 cl.5, 16, 17, 18 and 49 cl.5, 16 | a yaml count over `corrections/hero.yaml`. The handoff's "43" counted the header comment at `hero.yaml:4` |
| M-q | **the source does not mark where the text around the clauses begins and ends.** The last clause of each of the 4 hero forms runs to the end of the text, so its body includes the signature block and the `Printed in England and issued by GAFTA …` footer. The lines before clause 1 (title, contract number, parties block) are discarded by today's segmenter (`cur is None`, `extract.py:112`) | `clause_spans` rows for each form's highest clause number, read |
| M-r | **untuned restatements of the segmenter's enumerated patterns, compared over the 80 forms** (`variants.py`): <br>- `\d+` for `\d{1,2}`: 0 forms change; <br>- `[….]{2,}` for `[….]{3,}`: 0 forms change; <br>- a heading carried over all following uppercase lines, instead of exactly one: 0 forms change (the corpus has 1 or 2 carry-overs, none over one line); <br>- a heading token defined as "no lowercase letter and no digit", instead of `[A-Z,&/()\-.']+`: 12 forms change, **no hero heading changes**, M-d holds 28/28, and 120 and 125 become contiguous. It brings in some new noise as well: `BROKERAGE %` (3), `PRICE US$ (US` (1), `OPTIONAL CLAUSES \| METHOD OF …` (1). <br>Dropping the digit condition too ("no lowercase letter") changes 39 forms and lowers matches to 1,480 | `variants.py`, in the hdc-contract session scratchpad |
| M-j | **circularity:** the uppercase `altLabel`s (`"QUALITY"`, `"SAMPLING, ANALYSIS AND CERTIFICATES OF ANALYSIS"`, `"PERIOD FOR PRESENTATION OF THE VESSEL"`) are GAFTA headings, added to the scheme by people who read these forms | `ontology/gco-concepts.ttl:21,58,76`. M-f therefore measures label coverage on the forms the labels were written from. It does not show that the labels generalise |
| M-k | gUFO is absent from both repos | `git grep -il gufo main` in iladub: empty. `grep -ri gufo ontology/` in hdc-contract: empty |
| M-l | iladub's PDF reader is pdfminer (`src/iladub/readers.py:44-49`). hdc-contract's segmenter is written against **`pdftotext -layout`** output (`extract.py:35-43`), including its line-number margin (`_MARGIN`, `extract.py:12`) | read. **Not measured: whether pdfminer text segments the same way.** See § 9 seam S1 |
| M-m | today's segmenter carries one constant: `MIN_CHARS = 200` (`extract.py:11`), a refusal floor for image-only PDFs | read |
| M-n | the word "contract" already means something in iladub: the etkl **role contract** (`ground.py:180` `load_contract`, `cor:contract` in `tests/corpus-manifest.ttl`, the "contract membrane" of CLAUDE.md § 8), **and the module `src/iladub/contract.py` exists** (a "semantic data contract" module) | read. Hence a distinct vocabulary prefix (§ 6.2), and **§ 6.4's package path collides with that module (open: § 11 Q7)** |

## 4. Scope

**In:** the rung added at all six sites (§ 6.1); `ctr:` vocabulary and its gUFO alignment; the
contract compiler for text-layer PDFs with numbered clauses; the membrane; contract:01 and its
oracle tests; and a contract-corpus manifest for the 4 forms.

**Out (named so a plan does not drift into them):**

- Parties, roles, modality (obligation/permission), fillers such as `finalAt` or `noticeBy`.
  These are later contract-rung criteria.
- The `also` types (M-g). They are body-level and belong to hdc-contract's arbitration in the
  companion spec. contract:01 **reports** them and does not score them.
- Any BAML/LLM call. contract:01 is model-free by ruling.
- Riders, amendments and multi-document contracts.
- Releasing or redistributing any GAFTA text (§ 6.6).

## 5. Classification gate (CLAUDE.md § 8)

| decision | class | why |
| --- | --- | --- |
| PDF → page text | PROCEDURAL, raw extraction | the source's text layer, read and not judged |
| a form feed (`\f`) becomes a space | PROCEDURAL, raw extraction | `\f` is the reader's page-break control character, not text. Replacing it keeps the line count, so line spans still point into the reader's output |
| strip the line-number margin (`^\s*\d{1,4}\s{2,}`) | PROCEDURAL, raw extraction | print furniture with an exact lexical form. Nothing is measured against a tolerance. `\d{1,4}` and `\s{2,}` are the furniture's literal shape: line numbers on these forms run to 4 digits and are set off by a gutter of at least two spaces. They are not fitted thresholds. **A plan must keep this justification in the code, at the regex.** This rule is also why a clause number with no period (`26 INSOLVENCY`, M-o) is **not** taken as a boundary. `3        PRICE` and a margin line `12   text` have the same shape, so admitting the period-less form would make extraction ambiguous. Those forms are refused instead (the contiguity row) |
| a line that is only a number (`^\s*\d{1,4}\s*$`) becomes empty | PROCEDURAL, raw extraction | the same furniture as the margin, on a line with no text after it (a margin number or a page number). The emptied line keeps its index |
| drop `page N of M` lines (`^\s*page\s+\d+\s+of\s+\d+\s*$`, case-insensitive) | PROCEDURAL, raw extraction | print furniture with an exact lexical form |
| **a clause start is a line `^\s*(\d+)\.\s+` followed by a non-empty heading** | PROCEDURAL, raw extraction | the source declares the boundary typographically: a number with a period, then a heading. `\d+` replaces today's `\d{1,2}`, which was an unexplained cap. On the 80 forms the change alters nothing (M-r). A line whose remainder has no heading (`7 or 8 days …`) is not a start |
| **the heading is the maximal leading run of tokens with no lowercase letter and no digit**, after runs of two or more dot characters (`[….]{2,}`) become spaces | PROCEDURAL, raw extraction | "set in capitals" is the typographic declaration, stated by letter case and not by a list of allowed characters. Today's `[A-Z,&/()\-.']+` is an enumerated list, and that list is why `SHIP’S`, `TRIBUNAL’S` and `GOODS:` were missed (M-o). Digits are excluded because a number is not a heading word, and adding them back is measured to lower matches (M-r). A dot run of two or more is a leader: a single dot is punctuation (`ETC.`), and no heading uses two in a row. `[….]{2,}` replaces today's `{3,}` and alters nothing on the corpus (M-r). **Measured effect:** 12 forms change, no hero heading changes, 28/28 refs still resolve, and new noise enters a few headings (M-r). That noise only costs a label match. It never moves a boundary, so the clause is typed at gUFO and arbitrated |
| **a heading with no run-in body continues over the following non-empty lines while each is entirely heading tokens and is not a clause start** | PROCEDURAL, raw extraction | a heading wrapped over several lines is still one heading. "Maximal" replaces today's "exactly one line", which was a cap with no reason. On the corpus they differ nowhere (M-r) |
| **a candidate start is taken only if its number is greater than the previous start's** | PROCEDURAL, decidable exact arithmetic, **and a filter, paired with the membrane** | this row is a judgement about which lines are clauses, and is classed as one. It drops a numbered line whose number is ≤ the last start, such as a cross-reference or a numbered sub-list inside a clause body. In a document numbered in ascending order, a line like that cannot open a new clause. The membrane catches the filter's mistakes: a wrongly taken line with a number above the next expected one leaves a gap, and the compile is refused. **Two failures it cannot catch** (§ 10): <br>- a non-clause line numbered exactly next-expected that has a heading; <br>- a missing final clause, absorbed into the clause before it. <br>Emitting every candidate and letting a declared rule pick was considered. The pick would still need the ascending rule, so it moves the filter without removing it. An earlier version of this design made segmentation a SPARQL derivation, which was rejected: "the previous chosen start" is recursive, and SPARQL 1.1 cannot express it without an iteration driver, which would be procedural again |
| **the lines before the first start are the contract's `ctr:preamble`; the last clause's body runs to the end of the text** | PROCEDURAL, raw extraction | the source declares no end for the clause sequence (M-q). Any trim, such as cutting at a signature block, would be a judgement about what a signature block looks like, so none is made. The last clause's `ctr:text` therefore includes the signature block and the printer's footer, and the consumer is told so (§ 6.5). The preamble is kept, where today's segmenter drops it, so no source text is lost. Parsing it (parties, dates) is a later criterion |
| **clause numbers contiguous from 1**, one heading per clause, spans non-overlapping and in line order | AXIOM, constraint → SHACL | closed-world over one holon (the contract): `sh:minCount`/`sh:maxCount 1` plus a holon-scoped `sh:sparql` constraint for contiguity and overlap. **The first clause must be 1.** Every start above 1 and every gap measured on the 80 forms is a missed clause, not a feature of the form (M-o). A missed clause is folded into the previous clause's body, so admitting gaps would assert wrong `ctr:text`. **Measured consequence:** with the rows above, 67 of the 80 forms compile and 13 are refused (101, 103, 104, 114, 122, 126, 129, 201, 202, 62, 79b, 83, 94a), mostly for period-less numbers and sentence-case headings. All 4 hero forms compile. A refusal names the form and its missing numbers, and is the finding a later criterion works from |
| **domain type of a clause** = the scheme concept whose label equals the clause heading (casefold, collapsed whitespace) | AXIOM, derivation → SPARQL `CONSTRUCT` | open-world and evidence-positive. The type is derived only when a label equal to the heading is **present**. Equality is exact, and no similarity score or cut-off is involved |
| **the gUFO type of every clause** | AXIOM, by alignment (no derivation step) | `ctr:Clause rdfs:subClassOf <gUFO class>` in `ctr-gufo-align.ttl`. Every clause is asserted `a ctr:Clause` on the positive evidence that it is a numbered clause of the contract. So the coarse type is never inferred from the **absence** of a domain type, and § 7 holds. "Fallback-typed" means a clause that carries the gUFO type and no domain type. That is a holon-scoped closed **read** by the consumer (hdc-contract), not a fact derived into the graph |
| a heading that matches two concepts' labels | AXIOM, constraint → SHACL | `sh:maxCount 1` on `ctr:clauseType`. If the scheme gives two concepts the same label, the compile is refused and the fault is reported against the **scheme**, not resolved here |
| refuse a PDF with no text layer | PROCEDURAL, decidable | **`MIN_CHARS = 200` is a tuned constant (M-m) and is not carried over.** The refusal is "zero non-whitespace characters". See seam S2 for what to measure before that replaces the floor |

**No tuned constant appears in this loop.** A plan that introduces one, or carries `MIN_CHARS`
over, fails review.

## 6. Design

### 6.1 The rung (ruling 3): five edits and one measurement, landed together

1. `tests/arc-manifest.ttl` after `:97`: `prog:rung:contract a prog:Rung ; prog:rungKey
   "contract" ; rdfs:label "the contract compiler" .` Also correct the comments at `:3`, `:21` and `:76`
   ("five settled rungs") so it cites this spec as the sixth rung's ruling.
2. `tests/arc-shapes.ttl:59-60` (M6) and `:94-95` (M1): add `"contract"` to both `sh:in` lists,
   and change both messages from "five" to "six", naming this spec.
3. `scripts/cockpit.py:117`: `RUNGS` gains `"contract"`. Its position is a display choice only
   (the comment at `:112-116` says so). This spec suggests directly after `"tab"`, because the
   ruling places the rung "beside `tab`".
4. `tests/test_arc_manifest.py:890`: the expected rung-key set gains `"contract"`.
5. `docs/narrative/scope-evolution.md`: add a `### contract — the contract compiler` section after
   `### tab` (`:59`). The section heading must match the `rdfs:label`, as the comment at
   `arc-manifest.ttl:76-77` requires.
6. **MEASURE before the plan is written:** run `git grep -n '"substrate"'` (the earlier `'"substrate")'` missed
   `test_arc_manifest.py:890`, which ends `"substrate"}`) and
   `git grep -n -i 'five'` over `tests/` and `docs/narrative/` to find any other closed list of rung keys. The
   six sites above come from the handoff's reading, not from an exhaustive search.
   (enumerating-before-claiming)

contract:01 is declared `prog:met false`, `prog:retrospective false`, with
`prog:declaredOn "2026-10-30"`. Its statement is in § 7.

### 6.2 Vocabulary: `ctr:` and its gUFO alignment (ruling 4)

- **Namespace `ctr:` = `https://w3id.org/iladub/contract#`**, under the owned root (CLAUDE.md
  § Source ownership). It is not `contract:`, because of M-n.
- `vocab/ontology/ctr.ttl` is standalone, with zero gUFO IRIs:
  - `ctr:Contract`: one compiled contract document.
  - `ctr:Clause`.
  - `ctr:clauseOf` (Clause → Contract).
  - `ctr:clauseNumber`: `xsd:positiveInteger` if seam S6 shows every clause number is an integer
    (today's segmenter only matches `\d{1,2}`, `extract.py:13`), otherwise `xsd:string`.
  - `ctr:heading` (`xsd:string`).
  - `ctr:text` (`xsd:string`, the clause body).
  - `ctr:lineStart`/`ctr:lineEnd` (`xsd:positiveInteger`).
  - `ctr:preamble` (Contract → `xsd:string`, at most one): the text before clause 1 (§ 5).
  - `ctr:clauseType` (Clause → `skos:Concept`, **no `rdfs:range` narrower than `skos:Concept`**,
    because the domain module is external).
  - How each `ctr:Contract`/`ctr:Clause` relates to the etkl holon classes
    (`etkl-holons.ttl`): **MEASURE** which existing holon class a compiled document is, and
    subclass it rather than duplicate it.
- `vocab/ontology/ctr-gufo-align.ttl` (the `*-align.ttl` form). gUFO IRIs appear **only as
  objects** (the same invariant as HGA). The proposed mapping:
  - `ctr:Contract rdfs:subClassOf gufo:Relator`. In UFO a contract is the canonical relator.
  - `ctr:Clause rdfs:subClassOf gufo:ExtrinsicMode`. A clause is read as a bundle of commitments
    and claims that inheres in one party and depends on the other.

  **This mapping is a proposal (§ 11 Q2).** A pure definitions clause is a weak fit for
  `ExtrinsicMode`. The more conservative alternative is `gufo:Aspect`. Whichever is chosen,
  **MEASURE the class IRIs against the published gUFO Turtle (pin its version and sha256)**
  rather than against the names in this paragraph.
- gUFO is consumed and never vendored into `vocab/`. If a test needs it, it is fetched or kept
  under a `vendor/gufo/` snapshot marked "NOT OURS", by analogy with rule 3 for HGA.

### 6.3 Inputs: the domain module and the corpus

- **The domain module is input, not iladub vocabulary.** The GAFTA clause scheme (`gco:`) is
  hdc-contract's. The compiler takes `scheme_path` + `scheme_iri` (a `skos:ConceptScheme`) as
  parameters, the way `compile_offer` takes `terms_path` (`src/iladub/m4.py:92-96`). For tests,
  a read-only snapshot of `ontology/gco-concepts.ttl` is kept at
  `vendor/gco/gco-concepts.ttl`. Its header records the hdc-contract commit sha and "NOT OURS".
  iladub never edits that file. A label fix (for example the 48 cl.7 disagreement) happens in
  hdc-contract, and the snapshot is re-pinned afterwards.
- **A new manifest `tests/contract-corpus-manifest.ttl`**, using the `cor:` terms. There is one
  `cor:Document` per form, with `cor:url` and `cor:sha256`, fetched by `scripts/fetch_corpus.py`
  and never committed. **It is a separate manifest, not `tests/corpus-manifest.ttl`.** Seam S3:
  measure how `tests/test_corpus.py` selects documents before choosing. If it iterates every
  `cor:Document` through `compile_document`, a table compiler would be run on legal text.
- **The truth fixture is `tests/fixtures/contract/hero-truth.ttl`**, converted once from hero.yaml
  and gold.yaml at a pinned hdc-contract sha. It holds clause numbers, gco concept local names and
  the `also`/`absent` flags, and **no GAFTA text** (hero.yaml's own rule, line 2). Its provenance
  header names the source files and their sha.

### 6.4 The compiler

`src/iladub/contract/compile.py`, `compile_contract(pdf_path, scheme_path, scheme_iri) ->
ContractResult`, in six steps:

1. **Read.** Get the text layer (seam S1 decides pdfminer or `pdftotext -layout`). Refuse when
   there is zero non-whitespace text.
2. **Extract (PROCEDURAL).** Port `segment_clauses` and its helpers from hdc-contract
   `extract.py:48-116` **as § 5 restates them**, not verbatim. Four changes:
   - `\d+`;
   - `[….]{2,}`;
   - the letter-case heading token;
   - the maximal carry-over.

   Put the § 5 justification at each regex. A port test pins the M-r figures (hero counts
   30/26/27/30, 28/28 refs, 67 admitted forms) so that a later drift is caught. Emit RDF directly:
   - one `ctr:Contract`, with its `ctr:preamble`;
   - one `ctr:Clause` per segment, with number, heading (whitespace collapsed, and **nothing
     else normalised**, see § 11 Q4), text and line span.
3. **Derive (AXIOM).** Run `vocab/queries/contract-clause-type.rq` as a `CONSTRUCT ?clause
   ctr:clauseType ?concept`. It matches `LCASE(STR(?heading)) = LCASE(STR(?label))` over
   `skos:prefLabel|skos:altLabel` with `lang(?label) = "en"` and `?concept skos:inScheme
   $scheme`. Register the query in the query-declaration register if one governs `vocab/queries/`
   (seam S4).
4. **Membrane (SHACL).** Run `vocab/shapes/ctr-shapes.ttl` through `etkl/membrane.py:45
   validate`. It checks:
   - each clause: exactly one number, heading, text and contract;
   - at most one `ctr:clauseType`;
   - per contract (holon-scoped `sh:sparql`): numbers contiguous from the first, and spans
     non-overlapping and in number order.

   If the graph does not conform, `compile_contract` raises with the report. Nothing is returned
   half-compiled.
5. **Output.** A CleanDocument DataBook with an `asserted` block and a provenance stamp, following
   `compile_offer_databook` (`m4.py:105-145`; frontmatter and stamp from `:132`). There is **no `propositions` block**, because the
   compiler emits none (ruling 4). The serialisation is the seam the hdc-contract spec consumes.
   § 11 Q1 holds the alternative (plain Turtle).
6. **CLI.** `iladub contract compile <pdf> --scheme <ttl> --scheme-iri <iri> -o <databook>`.
   **MEASURE** the existing CLI's subcommand form before adding to it.

### 6.5 What hdc-contract reads (the seam, stated from this side)

The only contract between the repos is the `asserted` graph:

- `ctr:Clause` nodes with number, heading, text and span;
- an optional `ctr:clauseType` to a concept of the scheme that was passed in;
- the gUFO type through the alignment module.

A clause without `ctr:clauseType` is what hdc-contract arbitrates. On the hero forms that is 2
clauses (M-h). Across the 67 forms the membrane admits, it would be 220 (M-i). The 13 refused
forms produce no graph, so hdc-contract has nothing of theirs to read. The companion spec owns everything
downstream.

Two properties of the text that the consumer must not mistake for clause content (M-q):

- the last clause's `ctr:text` includes the signature block and the printer's footer;
- the preamble is on `ctr:Contract`, not on any clause.

### 6.6 GAFTA text

The forms are copyrighted. They are fetched and pinned like every corpus document, and never
committed. Unit tests run on a **synthetic** three-clause contract (`examples/contract/` — CLAUDE.md
:751, keep examples synthetic). Corpus tests skip, naming the fetch command, when the PDFs are
absent, following the existing corpus tests' skip rule (seam S3).

## 7. contract:01

> **prog:statement:** "The four GAFTA hero forms (Nos. 48, 49, 64, 100; tests/contract-corpus-manifest.ttl)
> compile through compile_contract with no model call, and each compiled graph conforms to
> ctr-shapes. Against tests/fixtures/contract/hero-truth.ttl: every primary row's clause carries
> that row's ctr:clauseType, or the form carries a dated cor:adjudication naming the row and
> disposing of it; no clause of a form carries a type the truth marks absent for that form; and
> every gold clause ref resolves to exactly one ctr:Clause. The also-rows are reported, not
> scored."

**prog:oracleTest** (names fixed by the plan):

1. `test_hero_forms_compile_and_conform`: four graphs, all conforming.
2. `test_primary_rows_agree_or_are_adjudicated`. Expected at today's measurement (M-f): 39 agree
   and 48 cl.7 is open. **contract:01 is therefore not met on landing** unless 48 cl.7 is
   disposed. Either hdc-contract's scheme moves the label, the trader confirms the hero row, or
   an adjudication records the disagreement. **The matcher is not adjusted to make the row pass.**
3. `test_absent_types_are_absent`: 3 rows.
4. `test_gold_refs_resolve`: 28 refs (M-c, M-d).
5. `test_no_model_call`: the compile runs with BAML's client entry point patched to raise.
   **MEASURE** the entry point (`extract_baml.py`) the patch must cover.

The also-row report is printed by the test run and recorded in the adjudication note. It should
read 0 of 6 by heading (M-g), and that number is expected rather than a failure.

## 8. Tests and falsification (CLAUDE.md :481)

Each oracle test above, and each unit test on the synthetic contract, ships with a
`## FALSIFICATION` block. The minimum inversions are:

| test | inversion that must turn it red |
| --- | --- |
| hero forms conform | drop `sh:maxCount 1` from `ctr:clauseType`, then give two concepts the same label in a test scheme: the shape must be what refuses |
| contiguity constraint | delete clause 3's start line from the synthetic contract |
| contiguity starts at 1 | delete clause 1's start line from the synthetic contract: numbering 2..3 is contiguous but must still be refused |
| letter-case heading token | put `SHIP’S` (curly apostrophe) in a synthetic heading: reverting to today's enumerated class must lose the clause and turn the port test red |
| primary rows agree | change the `CONSTRUCT`'s equality to always-false: 0 rows agree |
| absent types | inject a `ctr:clauseType gco:Deficiency` on a 49 clause |
| gold refs resolve | renumber one clause in the extractor's output |
| no model call | call `extract_offer` from inside `compile_contract`: the patched client must raise |
| gUFO by alignment, not by derivation | remove `ctr-gufo-align.ttl` from the load: no clause may then carry a gUFO type. This is what proves the compiler does not assert gUFO itself |

## 9. Seams the implementer must measure (CLAUDE.md :474-480)

- **S1: the reader.** Run pdfminer and `pdftotext -layout` over the 4 forms, then run the ported
  segmenter on each. Report the per-form clause counts against M-e (30/26/27/30) and the
  28-ref resolution. If pdfminer differs, the compiler takes `pdftotext` as an optional reader
  (poppler is a binary dependency, which the plan must declare). **Do not adapt the segmenter's
  regexes to pdfminer output.** That would be tuning extraction to a reader.
- **S2: the text-layer refusal.** Before replacing `MIN_CHARS` with "zero non-whitespace", measure
  what `pdftotext` returns for one image-only PDF. If it returns stray characters, the refusal
  needs a stated rule, not a number.
- **S3: corpus selection.** How `tests/test_corpus.py` and `scripts/fetch_corpus.py` pick
  documents and skip when they are absent.
- **S4: query registration.** Whether `vocab/queries/*.rq` must be declared
  (`query-declaration-shapes.ttl`), and how.
- **S5: rung-key sites.** § 6.1 item 6.
- **S6: `clause_no` lexical forms.** § 6.2.

## 10. Risks

- **M-f flatters.** 39/40 is measured on the forms the labels were written from (M-j). The first
  form outside the hero set will type fewer clauses. That is by design: they fall back to gUFO and
  go to hdc-contract, which is the arbitration loop's job. Do not read 39/40 as accuracy on
  GAFTA as a whole.
- **Segmentation is the one PROCEDURAL step that a reviewer could call a heuristic** (the
  letter-case heading run and the ascending-number filter). § 5 argues that each construct is
  typographic raw extraction or exact arithmetic, with the membrane as the oracle. If review
  rejects that argument, the § 8 route is NEURAL, which ruling 1 rules out for this slice.
  **That conflict goes to the maintainer and is not resolved in the plan.**
- **The membrane does not see two segmentation failures** (§ 5, the filter row):
  - a non-clause line that is numbered exactly next-expected and has a heading;
  - a final clause that was missed.

  Both leave the numbering contiguous. None was found on the 4 hero forms: M-d resolves 28/28
  refs, and each last clause is `METHODS OF ANALYSIS`, the true final heading. The 63 other
  admitted forms were not checked for them.
- **Scheme drift.** The vendored gco snapshot can diverge from hdc-contract. The pin, and a test
  that fails when the snapshot's sha header doesn't match its content hash, keep that visible.

## 11. Not decided here

- **Q1: serialisation of the seam.** This spec proposes a DataBook (§ 6.4.5). The alternative is
  one Turtle file per contract. The hdc-contract spec should confirm it can read either before the
  plan fixes one.
- **Q2: the gUFO classes** (§ 6.2). `Relator`/`ExtrinsicMode` is proposed, against
  `Aspect`, and the mapping needs checking against the pinned gUFO release.
- **Q3: ruling 5's reading.** hdc-contract's ingest moves here. Does hdc-contract then delete
  `extract.py`, or keep it until the companion spec's slice lands? That is the companion spec's
  call.
- **Q4: heading normalisation beyond whitespace.** Stripping trailing punctuation would type the
  2 stragglers in M-h. It is exact and untuned, but it changes which labels match, so it should
  be its own decision with its own falsification. It is not folded into this slice.
- **Q5: licence.** GAFTA's terms for fetching and processing the forms in a public repo's CI were
  not checked.
- **Q7: package name.** `src/iladub/contract.py` exists, so `src/iladub/contract/` cannot sit beside
  it. Use another package name (e.g. `src/iladub/ctr/`) or rename the module: the maintainer's call.
- **Q6: 48 cl.7.** Is it a label fault (hdc-contract scheme) or a hero fault (trader)? It is the
  maintainer's or trader's call, and contract:01 cannot be met until it is made.
