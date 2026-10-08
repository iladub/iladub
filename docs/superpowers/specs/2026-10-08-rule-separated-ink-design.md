# Spec — the membrane refuses a cell whose ink an author's rule separates

**Serves:** maintenance — loop 3 of the four the maintainer ordered on 2026-10-06
(`docs/superpowers/2026-10-06-r295-grid-scope-handoff.md` § 3): a membrane guard so an asserted
table cannot merge columns the author separated with rules.

**Date:** 2026-10-08. **Branch:** `rule-separated-ink`, cut from `main` at `b421ad8`.

**Doc impact: increment.** § 3 adds two datatype properties to `tab.ttl` (`tab:firstGlyphEnd`,
`tab:lastGlyphStart`, domain `tab:Cell`), widens `tab:RuleSpan`'s comment from grid evidence to
page evidence, and adds one SPARQL-based constraint to `tab-shapes.ttl`. No published term changes
meaning.

**Provenance.** The predicate was proposed in `docs/superpowers/2026-10-07-rule-crossing-census-handoff.md`
§ 5 action 1 and RUN in this session (§ 1). The site was ruled by the maintainer in chat on
2026-10-08, choosing **"membrane shape only"** over a producer-side oracle and over per-cell
withholding, after § 2's seam was measured and shown to them.

---

## 0. The concern, first

**This loop makes fed-h41 fail loudly. It does not make fed-h41 read correctly.** A page-scope
refusal raises `membrane.MembraneRefusal` and aborts the page (`compile.py:2165-2194`, RUN by
reading; the `raise` sits inside `if not conforms:`). It does not escalate the offending table, and
no helper in `compile.py` or `document.py` withdraws one asserted table while keeping the rest of
the page (grep for `withdraw` names only group retraction and the grid rebuild). fed-h41's two
merged tables therefore become a `MembraneRefusal` for the document, not two escalations. The
maintainer chose that on 2026-10-08. A silent misread becomes a loud refusal. The producer-side
guard that would turn the refusal into an escalation is § 7's first item, the next loop.

fed-h41 is a held-out document (`tests/held-out-manifest.ttl`). No test compiles it today
(`grep -rln fed-h41 tests/` names only the manifest, artifact and fetch tests), so the refusal
breaks nothing in CI. It changes what a held-out run of fed-h41 reports.

## 1. The predicate — measured, not proposed

> A rule **separates a cell's ink** when at least one of the cell's glyphs lies wholly left of the
> rule (`glyph.x1 ≤ rule.x`), at least one lies wholly right of it (`glyph.x0 ≥ rule.x`), and the
> rule's vertical extent overlaps the cell's box over a positive length.

Since a glyph wholly left exists iff `min(glyph.x1) ≤ rule.x`, and one wholly right exists iff
`max(glyph.x0) ≥ rule.x`, the predicate needs exactly two numbers per cell:

    firstGlyphEnd   = min over the cell's glyphs of glyph.x1
    lastGlyphStart  = max over the cell's glyphs of glyph.x0
    separated  ⇔  firstGlyphEnd ≤ rule.x ≤ lastGlyphStart  ∧  min(y1, rule.bottom) − max(y0, rule.top) > 0

There is no tolerance. A glyph that overruns a rule (`x0 < rule.x < x1`) counts on neither side,
which is precisely what distinguishes a last digit painted across a closing rule from a sign
painted beyond it.

**RUN 2026-10-08 at `b421ad8`.** `scripts/rule_crossing_probe.py` extended with the glyph-side test
(a cell's glyphs are the page's non-space `chars` whose centre lies inside the cell's 2dp bbox,
inclusive). One document per process, serially. The population is every cell the strict test
`x0 < rule.x < x1` crossed; a cell outside it cannot satisfy the predicate, since the predicate
implies the strict test.

| document | strict-crossed cells | glyph-side fires |
|---|---|---|
| fed-h41 (held out) | 13 | **13** |
| apple (accepted) | 19 | **0** |
| who-covid (held out) | 109 | **0** |
| who-wfa (accepted) | 18 | **0** |
| the other seven | 0 (2026-10-07 census) | 0 by construction |

In all 146 non-firing cells, one glyph straddles the rule and none lies wholly beyond it (apple
19/19, who-wfa 18/18, who-covid 109/109; 47 of who-covid's also have a glyph wholly left).

**The 13 are misreads, confirmed by rendering** (closing § 4's first unverified item of the
2026-10-07 handoff). fed-h41 p7: each `+`/`-` sits immediately right of a rule, at the left of the
next column, and the reader glued it to the value on the rule's left (`96,127+`). fed-h41 p5:
`Total assets │ (0) │ 6,852,491` spans three ruled columns and was read as one label cell.

## 2. The facts the membrane needs, and the one seam that adds them

The graph `_validate` sees holds no rule and no glyph (2026-10-07 census § 2: 0 of 68 calls). Two
fact families have to enter the page graph first. Both are PROCEDURAL raw extraction (§ 8):

- **Rules.** One `tab:RuleSpan` per entry of `geometry.extract_rules(pdf, page)`, carrying
  `tab:ruleX`, `tab:ruleTop`, `tab:ruleBottom` (2dp, the rounding `gridregion.py:58-61` already
  uses; no new precision is chosen) and `tab:onPage`.
- **Glyph extents.** On every cell reached by `tab:hasCell` or `tab:hasDataCell`, the two literals
  of § 1, 2dp, computed from `geometry.extract_chars` on the cell's own `tab:onPage`.

**One seam, not ten.** The ten cell-bbox emitters (`holon.py` ×8, `datagrid.py:752`,
`boxhead.py:327`) each emit `tab:onPage` beside `tab:hasBBox` (grep `TAB.onPage` in those files).
So one post-pass over the finished page graph, immediately before the page-scope `_validate` block
at `compile.py:2161`, reaches every cell without touching any producer. It runs **only on a page
with at least one rule**, so an unruled page's graph is byte-identical. It runs whether or not
`validate_shapes` is set, so the graph a caller gets does not depend on the flag.

**Hashes move on every ruled page.** That is the expected cost. Acceptance (§ 5) requires that only
hashes move: scores, verdicts and asserted/escalated counts stay identical on the seven.

## 3. Vocabulary and the shape

- `tab:firstGlyphEnd`, `tab:lastGlyphStart`: `owl:DatatypeProperty`, domain `tab:Cell`, range
  `xsd:decimal`, comments citing this spec.
- `tab:RuleSpan`'s comment: "evidence" now covers page evidence carried into the page graph.
- The shape (in `tab-shapes.ttl`) targets subjects of `tab:firstGlyphEnd`. Its SPARQL constraint
  selects a `tab:RuleSpan` with the same `tab:onPage`, `firstGlyphEnd ≤ ruleX ≤ lastGlyphStart`,
  and a positive overlap between `[ruleTop, ruleBottom]` and the cell bbox's `[y0, y1]`. The
  message names the cell's text and the rule's x.

**Engine parity is a seam to RUN, not assume.** The membrane prefers rudof and falls back to
pySHACL (`membrane.py:22-42`). The focus node is a cell URI and the bbox a blank node joined
inside the query, not a blank focus node, but the fixture must pass and fail identically under
`ILADUB_MEMBRANE=pyshacl` and `=rudof`.

## 4. Oracle and tests

- **Synthetic fixture** (no corpus): a minimal page graph with one table whose cell has
  `firstGlyphEnd ≤ ruleX ≤ lastGlyphStart` against a same-page rule with positive y-overlap. It is
  refused. Three controls conform: the overrun shape (`lastGlyphStart < ruleX`), the rule on another
  page, and the rule vertically disjoint from the cell.
- **Post-pass test:** given glyphs and rules, the two literals equal the min/max of § 1, and an
  unruled page adds zero triples.
- **`## FALSIFICATION`:** delete the shape's constraint and show the fixture test failing; restore
  it and show the suite green.

## 5. Acceptance

1. The seven accepted documents keep their scores and verdicts, with 0 verdicts moved, swept
   locally one test file per process, because CI skips the corpus.
2. fed-h41 raises `MembraneRefusal`, and its message names p5's or p7's cells.
3. apple, who-wfa and who-covid compile without refusal. These are the 146 overruns, now through
   the real 2dp facts rather than the probe's raw ones.

## 6. Seams measured

- Refusal raises, never escalates: `compile.py:2165-2194` (READ).
- `compile_document` validates both scopes by default: `validate_shapes: bool = True` at
  `document.py:1434` and `compile.py` `compile_tables` (READ).
- Cells carry `tab:onPage` beside every bbox: 12 `TAB.onPage` adds across `holon.py`, `datagrid.py`
  and `boxhead.py` (grep, READ).
- `tab:RuleSpan` vocabulary exists: `tab.ttl:412-416` (READ).
- Page chars are already extracted on ruled pages: `compile.py:519` (READ). The post-pass reuses
  `extract_chars` per cell page rather than threading that local through.

## 7. What is not done

- **The producer-side guard.** A refused table should escalate, not abort its page. That needs a
  per-table withdrawal at ten asserting sites plus grid adoption, and a ledger move from asserted
  to escalated: [[R73]]'s double-count class. It is the next loop.
- **Document-scope cells that no page graph minted** (for example `holon.py:770`, keyed by
  `n.page`) get no glyph extents and are unchecked at document scope.
- **[[R300]]**, the report URI with no triples, is not on this path.
- **The glyph-to-cell assignment is containment of the glyph centre in the 2dp bbox.** Two cells
  whose boxes overlap could share a glyph. The census found no case where that changes a verdict.
  No instrument checks it.

## 8. Classification (CLAUDE.md § 8)

- **Rule and glyph extraction, and the min/max:** PROCEDURAL. This is raw extraction (source to
  typed facts) plus decidable exact arithmetic. Nothing is judged and no constant is tuned.
- **The refusal:** AXIOM, Constraint → SHACL, closed world. The membrane decides what may cross.
  Nothing is derived from absence: a cell with no glyph facts is simply not a target.
