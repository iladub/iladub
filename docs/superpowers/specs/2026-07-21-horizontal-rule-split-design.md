# Horizontal-Rule Header/Body Split — capture all-text hierarchical tables

**Date:** 2026-07-21
**Status:** Design — approved (brainstorm 2026-07-21).
**Scope:** the second real-PDF-robustness slice, the horizontal-rule sibling of the vertical
border-aware-grid slice. When the type-homogeneity header/body split fails (all-text tables), use a
horizontal rule the author drew between header and body as the split. Fixes a real 0.00 data-loss.
Purely additive; engages *only* when the type split returns `None`.

## The failure (measured, 2026-07-21)

An **all-text hierarchical table** (a spanning header over text leaf columns — e.g. `Name` +
`Contact` spanning `Email`/`Phone`, all-text body) escalates with **score 0.00, UNSUPPORTED /
KIND_NOT_SUPPORTED** — data completely lost. Cause: `header_body_split` (the shipped B2a AXIOM,
`header-body-split.rq`) marks the header→body boundary as "the first row at/after which some column is
homogeneous *non-Text*." An all-text table has no non-Text column, so it returns `None`,
`classify_hierarchical` returns `None`, and the whole table escalates. Flat all-text *record* tables
are unaffected (they don't use the split); the gap is specifically the **hierarchical** (spanning- /
multi-level-header) path.

## The fix — the author's horizontal rule *is* the header/body boundary (§0)

Real reports draw a horizontal rule under the header. That rule is the author's explicit header/body
boundary — recover it (PROCEDURAL extraction) rather than perceive it from cell types. Verified: for
the failing fixture, the horizontal rule at `y=108` yields split = the first line below it (index 2),
and `infer_header_tree` + `logical_rows` then both succeed where the type split gave `None`.

## Conservative disposition (targets exactly the gap, cannot regress)

`header_body_split(band, grid)`:
1. Compute the **type-based split** (the existing `header-body-split.rq` derivation).
2. If it is **not `None`** → return it unchanged (typed tables — numeric/date/currency — are
   untouched; the rule is never consulted).
3. If it is **`None`** and the band has horizontal rules → return the **rule-derived split**: the
   first line index whose `top` is below the **topmost *interior* horizontal rule** (a rule strictly
   below the first line's top and strictly above the last line's top), provided that split leaves ≥1
   header line and ≥1 body line. Otherwise `None`.
4. Downstream disposes: `classify_hierarchical` proceeds with the rule split and returns a region only
   if `infer_header_tree` + `logical_rows` succeed (the compile pipeline is the oracle); otherwise it
   returns `None` → escalate, exactly as today. So a *wrong* horizontal rule (e.g. a stray row
   separator) can at worst leave the table escalated — never assert a mis-split.

Because step 3 runs **only** on the `None` branch, no typed table's split can change → the slice is a
strict superset of today's captures.

## Pipeline

1. **`geometry.extract_hrules(pdf_path, page) -> list[HRule]`** — `HRule(y, x0, x1)` per near-
   horizontal segment (`page.lines`/`page.edges`, `|top-bottom| < 1pt`, `x1-x0 > 2pt`), deduped.
   PROCEDURAL, mirrors `extract_rules`.
2. **`Band.hrules: tuple[HRule, ...] = ()`** (defaulted → every existing construction/fixture
   unchanged). `compile_tables` attaches to each final band the horizontal rules whose y lies within
   `[band.top, band.bottom]`.
3. **`header_body_split`** consults `band.hrules` on the `None` branch (the conservative disposition
   above).

## Why sound / anti-overfit

- **Cannot regress typed tables** — the rule split runs only when the type split is `None`.
- **Purely additive** — no horizontal rules (every shipped borderless fixture) → `header_body_split`
  byte-identical → all existing tests green.
- **§8:** `extract_hrules` (raw extraction) and "first line below the interior rule y" (decidable
  geometry) are PROCEDURAL, **no tuned constant**. It supplies the split the type-homogeneity AXIOM
  structurally cannot produce for all-text; the AXIOM remains the path for typed tables.
- **First implementation step (the last loop's lesson):** verify empirically that (a) shipped fixtures
  yield `extract_hrules == []` and a byte-identical `header_body_split`, and (b) the all-text
  hierarchical fixture now captures — before wiring.

## Definition of done (closes on the real blocker)

- An **all-text hierarchical fixture** (spanning header, text body, a horizontal rule under the
  header) — score **0.00 today** — compiles with the region captured (a hierarchical/record region
  asserted, not escalated).
- A **borderless twin** (same layout, no horizontal rule) still returns the type-based `None` and
  escalates — the honest demonstration that the rule is what fixes it.
- A **direct check** that `header_body_split` returns the type-based split unchanged when a numeric
  column exists *even if a horizontal rule is present* (typed tables never consult the rule).
- **Every existing test green** via `./.venv/bin/python -m pytest` (baseline 427 passed / 5 skipped);
  a shipped-fixtures-have-no-hrules guard for the additive guarantee.
- **§8 gate:** `extract_hrules` and the rule→split-row mapping are PROCEDURAL (raw extraction +
  decidable geometry, no tuned constant); the type-based `header-body-split.rq` AXIOM is unchanged.

## File structure (for the plan)

- **Modify** `src/iladub/etkl/geometry.py` — `HRule` dataclass + `extract_hrules(pdf_path, page)`.
- **Modify** `src/iladub/etkl/bands.py` — `Band` gains `hrules: tuple[HRule, ...] = ()`.
- **Modify** `src/iladub/etkl/headers.py` — `header_body_split` rule-derived fallback on the `None`
  branch (a `_hrule_split(band)` helper).
- **Modify** `src/iladub/etkl/compile.py` — extract page hrules; attach band-overlapping hrules.
- **Modify** `tests/etkl/fixtures.py` — `all_text_hier_ruled_pdf(path)` + a borderless twin.
- **Create** `tests/etkl/test_hrule_split.py` — extraction, rule-split derivation, type-split-takes-
  precedence, end-to-end capture, borderless escalation, no-hrules additive guard.

## Scope boundary (YAGNI)

- **Horizontal rule → header/body split only.** Using horizontal rules for *row-group* separation
  (multiple interior rules delimiting body row groups) is out of scope — a future slice.
- The rule split engages **only** when the type split is `None` (all-text). Reconciling a rule that
  *disagrees* with a present type split is out of scope (the type split wins; the rule is ignored).
- Picking among many interior horizontal rules: this slice uses the **topmost** interior rule
  (under-header); a table whose header/body rule is not the topmost interior rule falls to the
  downstream oracle (region fails to form → escalate), not a mis-split.
