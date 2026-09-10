# Handoff — the donated reading tiles, and the membrane cannot tell a right donor from a wrong one

**Date:** 2026-09-10. **Loop shape:** a MEASUREMENT loop against the R201 handoff's § 5b, run before
the donation plan it gates. No compiler behaviour changes. One instrument committed.
**Doc impact: none.**

Authored at roughly the 50K originating floor — part 5 was written first and is graded per action.

## 5. The next concrete action

### 5a. ASSERTED — write the donation plan, fresh session, against spec § 4; § 5b's gate is passed

`docs/superpowers/2026-09-10-the-grid-the-author-drew-handoff.md` § 5b said: *run the donated reading
on bfs p6 band 4 alone, past `region_tiles`, before writing task 1.* It ran, on all five bands
(§ 2 below): the membrane accepts every donated reading and every word is carried. The plan's
decisions 1-3 (where the AXIOM lives, what the donated reading is, what disposes it) stand as that
handoff states them. The before/after instrument is `scripts/grid_donation_spike.py`; its counts are
the plan's oracle numbers (222 → 267 asserted entries on the page, 45 false labels → 0).

### 5b. ASSERTED — decision 4 ([[R203]]) has ONE arm left, and it is not the one the spec offered

R203's row offers two closures: *a derivation of the donor's header row, or a demonstration that a
donor whose line 0 is data cannot pass the tiling membrane.* **The second is refuted by construction**
(§ 2, control): a three-word wrapped continuation line donated as the header of a nine-column table
tiles, because no tiling or physical shape binds a `tab:LabelCell` to a `tab:HeaderNode` — `tab:hasLabel`
appears in exactly one shape, `DerivedRowGroupShape` (`vocab/shapes/tab-shapes.ttl:337`). The membrane
is blind to header content, which is [[R166]] stated as a shape fact. So the plan **must** carry a
derivation of the donor's header, or ship donation with the header explicitly assumed and R203
inherited at five-band scope — and say which.

### 5c. PROPOSED — the derivation already exists: the datagrid's refusal record names the header lines

`derive_data_grid` on bfs p6 (§ 2) reads the page as one 9-column, 32-row table and refuses page
lines 3 and 4 as `HeterogeneousColumn/every-measure` — line 3 **is** band 2's line 0 (the true header)
and line 4 its first wrap. That refusal is a shipped AXIOM (`tab:ColumnHomogeneity`) and evidence-
positive: it reads present non-numeric cells in measure columns. The proposition: *a donor's line 0
is its header iff the page datagrid refuses that line `every-measure`.* **Why proposed:** it is one
page, the datagrid's line indexing is page-level while donation's is band-level ([[R202]]'s hazard),
and nobody has run it on the six other corpus documents. Falsify it in one command per document
before the plan depends on it.

### 5d. PROPOSED — the datagrid ALREADY reads the whole page correctly, and [[R160]] is why it never ships

The same run shows the datagrid's body (rows 7-38) includes the grand-total row and the Zurich row
that [[R205]] declared unreachable, read from page-level words rather than the bands' ruled cut. 288
entries under derived headers, against the band path's 222 under false ones and donation's 267. The
plan session should weigh, before task 1, whether donation is the right arm at all or whether
[[R160]]'s adoption gate — pre-empted here exactly as on apple p1 — is the cheaper repair. **Why
proposed:** this loop did not measure adoption on bfs p6, the datagrid has no band provenance, and
R201's ruling in favour of donation was made without this figure. It is not a refutation of the
ruling; it is a fact the ruling did not have.

### 5e. ASSERTED, and the maintainer's — the GLiNER2 branch is already pushed; 5c of the R208 handoff is stale

`only-a-refusal-admits-the-model` exists on `origin` (checked 2026-09-10). Its disposition — merge
as a refuted record, or delete — is still the owner's; nothing depends on it.

## 1. Where the primaries are

| what | where | what to establish there |
| --- | --- | --- |
| the instrument | `scripts/grid_donation_spike.py` | one run prints baseline / donated / control per band |
| the ruling this serves | `docs/superpowers/specs/2026-09-10-the-grid-the-author-drew-design.md` § 4 | grid donation as specified; § 5 what it does not do |
| the plan's four decisions | `docs/superpowers/2026-09-10-the-grid-the-author-drew-handoff.md` § 5a | decisions 1-3 unchanged; decision 4 re-read with § 5b-5c above |
| the shape fact | `vocab/shapes/tab-shapes.ttl` (`grep -n hasLabel`) | one hit, `DerivedRowGroupShape`; none on `HeaderNode` |
| the datagrid derivation | `src/iladub/etkl/datagrid.py`, `derive_data_grid` | `refusals` keyed by page line; `rows` the body |
| the register | `docs/superpowers/residues-open.md` R203, R205 | the measured notes appended this loop |

## 2. What was measured (2026-09-10, at `0133362`, bfs p6, `scripts/grid_donation_spike.py`)

Donor band 2: `_rule_boundaries` = `[71.47, 139.7, 187.29, 234.87, 282.46, 330.05, 377.63, 425.22,
472.81, 523.84]`, 9 columns, 4 lines; line 0 `Grandes régions | Total | 0-19 ans | … | Rapport de`.

| band | lines / words | baseline entries (label row = line 0) | DONATED (band 2 line 0 as header) | CONTROL (band 2 line 1 as header) |
| --- | --- | --- | --- | --- |
| 4 | 4 / 36 | 27, tiles, labels `Région lémanique, 1 736 124, …` | 36, **tiles**, ink 36/36, rt_fail 0 | 36, **tiles**, 3 labels over 9 columns |
| 5 | 6 / 54 | 45, tiles | 54, tiles, 54/54 | 54, tiles |
| 6 | 4 / 36 | 27, tiles | 36, tiles, 36/36 | 36, tiles |
| 8 | 8 / 72 | 63, tiles | 72, tiles, 72/72 | 72, tiles |
| 9 | 7 / 63 | 54, tiles | 63, tiles, 63/63 | 63, tiles |

Sum: 216 → 261 entries on the five bands; with band 2's own 6, the page goes 222 → 267 — the 45
predicted by the R201 handoff's § 5b, exactly. The control ties the donated reading on every band.

`derive_data_grid(bfs, 6)`: 9 columns (`alignment` universe, `x0` 72.6 … 522.2), `rows` = 32 page
lines 7-38, conforms `ColumnHomogeneity, NonDegeneracy, RowAddressability, ColumnAlignment,
SeedFollowsUniverse, AggregateWitness`. Refusals: lines 1, 3, 4 `HeterogeneousColumn/every-measure`;
5, 42 `RowAddressability/no-key`; 0, 2, 6, 39-41 `unplaceable`. Page line 3 = band 2 line 0 (top
95.3); line 4 = its `Cantons | dépendance | dépendance des` wrap; line 7 = band 3, the grand-total
row `Total 8 962 258 …` (top 136.4); line 8 = band 4 line 0. Band 10's line 0 is also a joined cell
(`Tessin 357 720 62 877 78 804`), a third instance of [[R205]]'s shape not on its row.

## 3. What was decided, and where that decision is recorded

- **Nothing about the compiler.** No arm of the R201 fork is re-ruled here; § 5d is a fact handed to
  the plan session, recorded nowhere but this file.
- **R203's membrane arm is struck as a closure path** — appended to its row in `residues-open.md`
  with the shape citation. The row stays open.
- **R205's "raw words unrecoverable" arm is refuted** — the datagrid reads both rows from page-level
  words. Appended to its row; the row stays open because the band path still loses them.

## 4. Unverified or assumed

- The spike constructs the donated `Band` by prepending the donor's header `Line` to the continuation
  band's lines and passing the donor's boundaries as `column_xs`. A plan's AXIOM would build the
  reading from the evidence graph instead; the membrane verdict should be the same, and is not shown
  to be.
- The datagrid-refusal criterion in § 5c is measured on ONE page. Not run on apple, cbh, graincorp,
  ons or who.
- Whether adoption (§ 5d) would actually ship the datagrid on bfs p6 was not run; R160's mechanism
  (`adopted (1,) → ()` under one asserting band) is inferred to apply from its description.
- No score, no suite run. The instrument is corpus-gated ([[R173]]) and has no CI test.
- The figure "roughly the 50K originating floor" is an estimate; no status-line reading was taken.
