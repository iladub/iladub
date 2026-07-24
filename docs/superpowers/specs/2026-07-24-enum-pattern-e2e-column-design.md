# Enum/Pattern E2E Column — demonstration slice

**Date:** 2026-07-24
**Status:** Design — approved (brainstorm 2026-07-24). Short spec (proportionate to a test-only slice).
**Slice:** Prove that `sh:pattern` and `sh:in` value-constrained fields ground **end-to-end from a PDF**
through the concept feed — not just at the `ground_concept` unit level (PR#57) or the range case (LVEF,
PR#56). Third of the four "deepen" slices.

**Nature (be honest):** **pure demonstration + coverage — NO production code.** Probe (2026-07-24)
confirmed pattern/enum already flow through `ground_document` unchanged: a 2-column table
(`Size`/`Sero`) with in-memory augmented shapes grounds `78kg`/`negative` and quarantines
`big`/`unknown` → `FeedResult(records=2, grounded=2, proposed=2)`. The capability is fully composed
(feed + value-constraint oracle + `sh:in`/`sh:pattern`, all shipped); this slice pins the combination.

**Gate context (§8):** no code, no decision — a fixture + a test. The oracle is the shipped SHACL
membrane; legality gates admission (rejection assertions are the guard).

---

## 1. Components

1. **Fixture `pattern_enum_table_pdf(path)`** (`tests/etkl/fixtures.py`) — a 2-column record table:
   a **pattern** column `Size` (`78kg` / `big`) + an **enum** column `Sero` (`negative` / `unknown`),
   2 data rows. Pure reportlab, single-token cells, wide gaps (compiles `RECORD_TABLE`).

2. **E2E test** (`tests/test_concept_feed.py`): compile → `table_records` → `ground_document` with
   **in-memory augmented shapes** — `offer-shapes.ttl` parsed then augmented with
   `sizeMetric sh:pattern "^[0-9]+(kg|cm)$"` and `serology sh:in ("positive" "negative")` (M4-safe: the
   committed file is never modified) — and a `MappingGroundingProposer` mapping `Size→sizeMetric`,
   `Sero→serology`.

## 2. Definition of done

- The pattern/enum PDF grounds end-to-end: `FeedResult(records=2, grounded=2, proposed=2)`; the grounded
  graph carries `tx:sizeMetric "78kg"` and `tx:serology "negative"` (row 1); row 2 (`big`, `unknown`)
  quarantines — the **rejection** is the load-bearing guard that the oracle still gates through the feed
  for the tight oracles.
- No production code changed; no shared shape/contract file changed; full suite green.

## 3. Scope (YAGNI)

- Test + fixture only. No changes to `feed.py`, `ground.py`, shapes, or the compiler.
- Augmented shapes are built in the test (in-memory); demonstrates the machinery is contract-agnostic.
- Typed-enum `sh:in` cast and multi-word cells remain separate later slices.

---

*Code Apache-2.0. Vocabulary/spec CC-BY-4.0. © 2026 François Rosselet.*
