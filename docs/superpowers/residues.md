# Residue register

Deferred items from the ET(K)L loops, in one tracked place. Each row records what the residue is,
where it was **measured** (never assumed), why it was deferred, and what would close it.

**This register is canonical.** Loops append rows here; a loop that closes a residue **strikes** its
number (`~~R92~~`), records the closure evidence in place, and moves the full row from
[`residues-open.md`](residues-open.md) to [`residues-closed.md`](residues-closed.md) — **it does not
delete the row.** Specs may describe a residue in prose, but the list of open residues lives here.

> ⚠️ **CORRECTED 2026-08-17** (E4, plan `plans/2026-08-17-the-gate-and-the-label.md` Task 3): this
> paragraph used to say a closing loop *"deletes its row in the same change."* CLAUDE.md § Deferred
> residues reverses that, and for a stated reason — a deleted row erases the proof of repair and
> silently shrinks the tally's denominator, which is the one number that shows the register is not
> pure degradation. The reversal was recorded in CLAUDE.md on 2026-08-12 and never propagated here.

Started 2026-07-29 (Loop D), collecting items previously scattered across four specs and the SDD
ledger.

## The tally (convention added 2026-08-12)

**Raising a residue is visible; closing one is not.** A register that only counts what it opens
reads as pure degradation — R92 sounds like ninety-two defects and nothing repaired. So every new
row records, in parentheses after its number, **the state of the register at the moment it was
raised**: `| R97 (17/87 closed) |` means that when R97 went in, 17 of the 87 rows then present
were closed.

The parenthetical is a **snapshot and is never updated afterwards**. That is the point — read
down the column and the ratio is a trend line: a register whose closed-fraction climbs is a
project paying its debts, one whose fraction falls is accumulating them, and neither fact is
legible from the highest number alone.

Two consequences for how rows are handled:

- **Closed rows are struck (`~~R4~~`), never deleted.** They are the other half of the
  denominator. A deleted row silently improves nothing and erases the evidence of repair.
- **A closing change records the closure evidence in the row it strikes** — what was measured,
  and what now prevents recurrence.

**As of 2026-08-17: 94 rows, 20 closed.** (Ten numbers between R1 and R96 were never issued as
rows; the denominator is rows that exist, not the highest number.) Was 18 closed at `e3f447a`; loop
`the-gate-and-the-label` closed ~~R102~~ and ~~R104~~, raising no new row. Verified, not asserted:
`awk -F'|' '/^\| R[0-9]/ {print $3}' docs/superpowers/residues.md | sort | uniq -c` → `20 closed`,
`74 open`.

| # | Residue | Measured | Why deferred | What would close it |
| --- | --- | --- | --- | --- |

## Why this file is an index (split 2026-08-12)

The register reached **146,716 characters — roughly 36.7k tokens**. CLAUDE.md tells every
contributor to *check the register*, and at that size doing so costs about **46% of the entire
40%-of-window budget** the context rule allows for design work. The instruction had become
impossible to follow, so nobody followed it: rows were grepped, not read, and stale rows
(R87, R88) were consumed as fact and cost real sessions.

So this file is now the **index**, readable in full for a few thousand tokens. The full text
of each row lives in two detail files, and you open only the rows you need:

- **[`residues-open.md`](residues-open.md)** — the open rows, in full.
- **[`residues-closed.md`](residues-closed.md)** — the closed rows, kept as evidence of repair.

**A row's one-line summary below is a POINTER, never the residue.** Do not act on it, quote it
in a spec, or plan against it without opening the full row — that shortcut is exactly how R87
and R88 propagated wrong. The index tells you *whether* to read; the detail file tells you *what*.

## Index

| # | Status | Summary — a pointer only; open the detail file before acting |
| --- | --- | --- |
| R1 | closed | CLOSED with R13 (Loop G attempt 2, 2026-07-30) |
| R2 | closed | CLOSED for the ruled path (Loop F, 2026-07-29) |
| R3 | open | Nested-subset vote |
| R4 | closed | CLOSED for the ruled hierarchical path (Loop H, 2026-07-30) |
| R5 | open | Proposal inputs not recorded |
| R6 | open | Centre-only merge candidate |
| R7 | open | Live BAML path unreachable |
| R8 | open | `ProposeHeaderSpan` missing |
| R9 | open | Conservation shape unreachable |
| R10 | open | `detect_bands` cuts one line too high |
| R11 | open | Mixed header rows |
| R12 | open | Split-table recurrence |
| R13 | closed | CLOSED for the ruled path (Loop G attempt 2, 2026-07-30) |
| R14 | open | The collapse can delete an author-drawn boundary |
| R15 | open | NEURAL residual: a wide label over blank/unclaimed columns |
| R16 | open | The UNRULED path keeps the split-number defect |
| R18 | open | Groups without a confirmed total stay ungrouped — and an unconfirmed total POLLUTES the next group |
| R19 | closed | CLOSED (Loop R41 Task 5, 2026-08-05) |
| R20 | open | Unconstrained contract fields stay propositions |
| R23 | open | `dg:AssertionInNavShape` unreachable from live extractor output |
| R24 | open | A wiki page citing an untracked/gitignored path is permanently exempt from staleness with a green membrane |
| R25 | open | The ≥2-references wiki admission rule is unenforced |
| R26 | open | The release gate fails OPEN on a same-day or backdated contradiction |
| R27 | open | `_IMPACT` scans the whole file unanchored |
| R28 | open | The promotion queue is one-shot |
| R29 | closed | CLOSED (Loop M Task 3, 2026-08-02) |
| R30 | open | The parent-vs-wrap-fragment residual fires INSIDE the engaged header block, not outside it |
| R31 | open | A double-drawn header-block border disengages the law |
| R32 | open | Loop L amplifies a pre-existing Loop G defect: header-confirmed boundary refinement can fabricate a column boundary the author never drew |
| R33 | closed | CLOSED FOR MARKED DOCUMENTS (Loop O, 2026-08-03) — the continuation LICENCE |
| R34 | open | The carried-header MATCHING law is Python control flow, not an AXIOM — and its `carried_header_roles` entry point is public and unguarded |
| R35 | closed | CLOSED (Loop N, 2026-08-03) |
| R36 | open | The feed's pass-3 identity guarantee is enforced on the `row_id` STRING, not the minted record subject |
| R37 | open | The document-level arithmetic pass's retraction semantics are a MODELLING CHOICE, not a derived fact |
| R38 | open | `feed._header_path` DOES read a `tab:DerivedRowGroup`'s `tab:headerLevel` |
| R39 | open | `vocab/queries/row-group-nesting.rq` (loop I's AXIOM, unchanged) is now the dominant cost in a chained document's compile |
| R40 | open | The document's outermost total (`Grand Total`) reads as an unconfirmed, ungrouped row |
| R42 | closed | CLOSED (Loop Q Task 7, 2026-08-04) |
| R43 | open | ONS gov-stats document: 1× `REGION_TILING_FAILED` plus an unnamed oddity — an `UNSUPPORTED_TABLE` kind carrying verdict `asserted` |
| R44 | open | BFS gov-stats document: 2× `KIND_NOT_SUPPORTED`, 2× `REGION_TILING_FAILED`, 5× `ROUND_TRIP_FAIL` |
| R45 | open | WHO health document: 3× `MATRIX_AMBIGUOUS` on the dense age × z-score matrix |
| R46 | open | Fetcher hardening — `_pdf_facts` crashes uncaught on non-PDF bytes at BOTH call sites |
| R47 | open | Both the grid-region peel and the hrule-box weld are scoped LEADING-only — a trailing full-width strip is neither peeled nor welded |
| R48 | open | `sectiongraph._leading_box_y`'s header-box-candidate selection can, on a document shape the interior-crossing test does not discriminate, locate a… |
| R49 | open | Spec §4.2's GRAPH-level key form (`tab:DerivedRowGroup` covering a section's rows, `tab:hasLabel` → the source heading cell, `prov:wasDerivedFrom`… |
| R50 | open | `document._confirm_section_total`'s totals oracle reads only the table's LAST row as the total candidate — several STACKED trailing lines below a s… |
| R51 | open | `document._band_subgraph`'s subject-collection licence leans on the `_index_suffix` URI-prefix minting convention holding everywhere a new subject… |
| R52 | open | Class-level documentation debt: `tab:DetectedAggregationRow` (loop H), `tab:continuesTable` (loop M), and `tab:SectionTotal` (loop Q) ship with NO… |
| R53 | open | `iladub:GroundedNodeShape` validates `groundsTo`'s PRESENCE only (`sh:minCount 1`), never its RESOLUTION — a `GroundedNode` whose `groundsTo` IRI r… |
| R54 | open | `feed.table_records`'s identity-prefix and the loop-Q E2E's cascade marker-set both assume the section HEADING is drawn ABOVE its notices — a posit… |
| R55 | closed | CLOSED (loop-quantity, 2026-08-06) — WITH ITS ATTRIBUTION CORRECTED |
| R56 | open | The hierarchical `n == 0` ROUND_TRIP_FAIL branch does not carry absorbed unit markers |
| R57 | open | Membrane redundancy — 8.2 s of the final pass's 12.6 s re-checks shapes the region gate already checked |
| R58 | closed | CLOSED (loop-subclass, 2026-08-06) |
| R59 | open | Real-document agreement is necessary but NOT sufficient evidence for an engine swap |
| R60 | open | rudof's n-triples parse is now the membrane's dominant cost |
| R61 | open | Emitter-typing is now an unenforced invariant — **0 instances measured 2026-08-18; the 14 live are emitter/ontology disagreement, and the probe is renamed** |
| R62 | open | Apple page 0 is unlocked by one band, not compiled |
| R63 | open | `unit-marker-column.rq`'s OWN-COLUMN purity check treats only `tab:Blank` as a wildcard, not `tab:ParenthesizedNumber` |
| R64 | open | Abstention (`tab:ParenthesizedNumber`/`tab:datatypeAbstains`) weakens the header-boundary scan |
| R65 | open | `celltype._CURRENCY`'s `[\d,]+` admits a comma-only numeric body |
| R66 | open | The reader's `optionSpace` is thin — `kind`'s three-value enum is the only judgement in the recorded chain with more than two options; every other… |
| R67 | open | The recorded chain is complete at compile-path granularity, not at query granularity |
| R68 | open | No real corpus document exercises the transposed path — the R55 ordering (`looks_transposed` before `transpose_is_coherent`) is proven only on synt… |
| R71 | open | The kind gate is load-bearing |
| R72 | closed | CLOSED (loop-data-grid, 2026-08-08) |
| R74 | open | The cbh data grid leaks one row from a SECOND table on the same page |
| R76 | open | Spec-writing discipline: proposal and disposal must come from DIFFERENT sources |
| R77 | open | cbh's four panel totals are missed on the SCORE path too, for the identical no-label reason |
| R78 | open | An unparseable member cell is summed as zero by `confirms_aggregate` |
| R79 | open | An adopted page's unread structure is escalated as ONE page-level residue candidate |
| R80 | open | apple p1's indent hierarchy is read by nobody |
| R83 | open | At PAGE scope an adopted page's `rep.graph` escalates nothing for a band the grid never TOUCHED, while the report still books its tokens |
| R84 | open | `adoption.build_ledger` counts every admitted line's tokens as asserted, whether or not any band was scoring that ink |
| R85 | open | `transpose-coherent.rq` is quadratic in row count |
| R86 | open | A quarantined concept mints NO decision holon, so the proposition half of the epistemics is unattributed |
| R87 | closed | CLOSED 2026-08-16 — wired into `compile._DEC_SHAPE_FILES` AND furnished by `escalation-furnish.rq`; the wiring alone was measured insufficient |
| R88 | closed | CLOSED 2026-08-13 — skolemized at the payload seam; `compile._DEC_ENGINE` deleted |
| R89 | open | `BandRecorder.record`'s Python guard now duplicates two constraints the membrane enforces — **rule adopted 2026-08-17 (in CLAUDE.md); application to that guard still open** |
| R90 | open | The bbox is dropped from every `ROUND_TRIP_FAIL` proposition |
| R91 | closed | `document.py:1498` and `datagrid.emit_data_grid` now both emit `dec:decidedBy` on the same admission holon |
| R92 | closed | CLOSED 2026-08-12 — the 39 float-valued `xsd:decimal` emitters are converted, and a tripwire prevents the 40th |
| R93 | closed | CLOSED 2026-08-12 with R92 |
| R94 | closed | CLOSED 2026-08-13 — one N-Triples artifact, both legs; own prescribed remedy REFUTED (parser is inside the engine boundary) |
| R95 | open | `_payload`/`_payload_nt`'s `audit=False` escape hatch is a standing hazard, fenced by a substring-scan test |
| R96 | open | `audit_literals`'s LEXICAL half is a silent no-op if rdflib's `NORMALIZE_LITERALS` global is ever `False` |
| R97 | open | Four wired `tab:` shapes the corpus does not exercise — 0 focus nodes each |
| R98 | open | `tab:LicenceRefusalShape` is idle BY DESIGN; spec §3's reason for it is wrong |
| R99 | open | `iladub:NoLeakShape` can never fire at compile — 11 focus nodes, unreachable term |
| R100 | open | `dec:EscalationShape` live at document scope, idle at page scope; registry cannot say so |
| R101 | open | A green CI tick can cover less than it looks — a module-level skip guard hides a whole module behind one skip line |
| R102 | closed | CLOSED 2026-08-17 (`b09dbd1`) — the `dec` leg is unconditional at document scope; re-measured 769/769, 0 never (was 316) |
| R103 | closed | CLOSED 2026-08-20 — NO: admitting `tab-datagrid.ttl` to `_FULL_ONT` is a provable no-op (27 pages, closure delta **0**); no ontology subject reaches an engine, so `ONT_VISIBLE` and `OUTSIDE_MEMBRANE` were the same case all along |
| R104 | closed | CLOSED 2026-08-17 (`742e862`) — `_validate` returns the refusing legs; `_refusal_message` names them |
