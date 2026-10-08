# Handoff: R301's seam, measured: one post-hoc withdrawal can find the refused table's ink (2026-10-08)

**Serves:** maintenance. This is [[R301]], the deferred half of loop 3 in the order the maintainer
gave on 2026-10-06 (`2026-10-06-r295-grid-scope-handoff.md` § 3).

**Topic:** compile · **Date:** 2026-10-08

**Doc impact: none.** This loop added one probe script and this handoff. No vocabulary, shape or
compile path changed.

## 5. Next concrete action (written first, at about 49K working tokens, just under the 50K floor)

1. **ASSERTED.** Write R301's spec in a fresh session. The seam is a single post-hoc step in
   `compile_tables`. It runs after `carry_from_pdf` (it needs the glyph facts) and before the
   page-scope `_validate`. For each table that owns a cell the rule-separated-ink predicate selects,
   it does four things. It removes the table from the page graph. It escalates the region's ink
   through `holon.escalate_region` with a new reason. It moves the report that names the table by
   `table_uri` from asserted to escalated, which means `tokens_escalated += tokens_asserted`,
   `tokens_asserted = 0`, `cells = 0` and `table_uri = None`. Finally it applies the same move to
   `asserted_total` and `escalated_total`. Because the move is a transfer between one report's two
   fields, the ink is booked once and `sum(r.tokens_*) == totals` still holds (§ 1). The membrane
   shape stays as the backstop. If a refused table is named by anything other than exactly one
   report, the guard withdraws nothing and the membrane raises as it does today (R89).
2. **PROPOSED: the document-scope effect on p5 is unknown.** Withdrawal leaves p5 asserting 0 of
   251 tokens. That may make p5 an adoption candidate (`adoption.is_adoption_candidate`), and the
   `p5/adopt` re-compile is where [[R300]]'s broken join lives. If adoption then asserts on p5, the
   question is whether that reading is right. The spec has to run the guard through
   `compile_document` on fed-h41 before it can say. That costs about 3 minutes (195 s, § 1). It may
   turn out that R301 cannot close without R300.
3. **PROPOSED: the classification needs ruling in the spec.** The guard asks the shape's own
   question, but at the producer. There are two candidates. (a) Run the SPARQL select from
   `tab:RuleSeparatedInkShape` as an open-world derivation. It is evidence-positive, because the
   rule and both glyph extents must be present. Read the query from `tab-shapes.ttl` so the guard
   and the membrane cannot drift apart. (b) Treat it as an oracle disposal, refuse then escalate,
   which is the pattern NEURAL proposals already use. Either way, no new predicate is authored.
   CLAUDE.md § 8 forbids using the closed-world form to *derive*. The spec has to show that this is
   a refusal of admission, not a derivation by absence.
4. **PROPOSED: the extent of a table's subgraph is unmeasured.** It is not yet known which triples a
   withdrawal must remove: cells, bboxes, header nodes, row groups, any promotion decisions. Before
   writing the withdrawal, measure what `document.py`'s existing withdrawals remove and reuse that
   idiom (`_retract_orphaned_groups`, the § 1g superseded-band withdrawal). Do not hand-roll a
   walk.

## 1. What was measured

`scripts/r301_seam_probe.py held-out/fed-h41-2025-01-02.pdf` was run at `32df3b7` (branch
`r301-producer-guard`). The probe spies on every `compile_tables` call that `compile_document` makes
with `validate_shapes=False`. It runs the shape's select on each returned page graph, and then maps
each refused cell to its owning table and that table to the reports naming it. The run took 195 s
and made 20 page compiles. Only two of those compiles hold refused cells, and both are pass 1 (the
call that raises today):

```
== page 5 doc=…/doc/p5 adopt=False score=0.1036 A=26 E=225
  table …/p5#htable3 types=['HierarchicalTable'] refused_cells=1 -> reports [3]
    region 3: verdict=asserted kind=UNSUPPORTED_TABLE cells=18 tA=26 tE=0
  graph tables not named by any report: []
== page 7 doc=…/doc/p7 adopt=False score=1.0000 A=137 E=0
  table …/p7#p7-datagrid types=['DataGrid', 'UniformGrid'] refused_cells=12 -> reports [3]
    region 3: verdict=asserted kind=RECORD_TABLE cells=126 tA=137 tE=0
  graph tables not named by any report: []
```

**The loop-3 handoff's § 5.2 prediction is CONFIRMED for the call that needs it.** On both pages,
each refused table is named by exactly one report, and that report's `tokens_asserted` is that
table's booked ink. The ten producer sites do not need a guard each. The per-band differencing
(`compile.py`, the `band_marks` block) already isolates each region's contribution before
validation runs.

**[[R300]] does not touch this seam.** Its broken join is in the `p5/adopt` re-compile, and that
graph holds no refused cell. The pass-1 report on p5 names `p5#htable3`, which resolves. R300 can
only reach this loop through item 5.2.

**p7 is not an adoption.** `p7-datagrid` is the `datagrid_fallback` region, which is appended after
the bands (index 3 on a page with 3 bands). So the region's text for escalation is the grid's rows,
not a band's lines. The spec has to handle both cases: a region that is a band, and an appended
region.

## 2. Where the primaries are

- Row: [[R301]] in `residues-open.md`. Loop 3: `2026-10-08-rule-separated-ink-handoff.md`, spec
  `specs/2026-10-08-rule-separated-ink-design.md`.
- The seam: `src/iladub/etkl/compile.py`, from `band_marks.append(...)` and the `_dc_replace`
  differencing, through the `datagrid_adopt` branch, `carry_from_pdf` and the page-scope raise.
- The probe: `scripts/r301_seam_probe.py`.

## 3. What was decided

Nothing new was decided. The 2026-10-08 ruling (membrane shape only for loop 3, producer guard
deferred to R301) stands.

## 4. Unverified

- "Every table in a page graph is named by exactly one report" is measured only on fed-h41 p5 and
  p7. It is not established corpus-wide. Item 5.1's fallback (otherwise, let the membrane raise)
  is what makes the guard safe without that census.
- None of the other 18 compiles of fed-h41 holds a refused cell (the probe prints only pages that do). That is under
  `validate_shapes=False`, and with the guard present it may change if 5.2 moves p5 into adoption.
