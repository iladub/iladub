# Handoff: holon:06 spec approved — write the plan (2026-10-15)

**Serves:** prog:criterion:holon:06 — the raw→clean traversal, compiler-produced.

**Doc impact: none.** A handoff; the spec it points at carries the increment.

Written at ~63K working tokens, over the 50K originating floor, which is why the plan is not in
this session. Part 5 was written first.

## 5. The next concrete action, typed

1. **ASSERTED: write the implementation plan** for
   `docs/superpowers/specs/2026-10-15-raw-to-clean-traversal-design.md` (approved by the maintainer,
   2026-10-15, in session), via `superpowers:writing-plans`, in a fresh session on a new
   branch from `main` (the spec and this handoff merge first). The spec is the contract; the plan cites it and does not re-derive it
   (CLAUDE.md plan rule 6).
2. **PROPOSED, and run before the plan fixes the query's input — minutes to refute:** spec § 3.3's
   scope seam. Grep every `ground_document(` call site for a `g` that is non-empty on entry
   (`tests/test_corpus*.py` first). If none, the CONSTRUCT may run over `g`; if any, it must run
   over the call's delta. The spec leaves this open on purpose; the plan must not assume it.
3. **PROPOSED:** spec § 5 item 4 predicts six reconciled regions on the offer fixture. It rests on
   § 8 item 3 (distinct region IRIs per grounded concept). One `ground_document` run on
   `_compiled_offer_graph()` counting distinct `iladub:fromRegion` objects of reviewed candidates
   settles it before the plan writes the number into a test.

## 1. Goal

Make `ground_document` derive a `GroundingPortal` and a `CleanDocumentHolon` from a Raw holon, so
holon:06 is met by compiler output, not a hand-authored file.

## 2. Where the primaries are

- **The spec:** `docs/superpowers/specs/2026-10-15-raw-to-clean-traversal-design.md` (commit
  `4e97712`). § 1 carries every measurement with `file:line`; § 3.3–3.5 name three seams the plan
  must measure (delta vs `g`; which shape file `_validate_grounding` loads; what
  `tests/test_arc_manifest.py` requires to flip `prog:met`).
- **The criterion:** `tests/arc-manifest.ttl:524-531` — the oracle test name is fixed there.
- **The input CI already grounds:** `tests/test_concept_feed.py:34-38, 128-150`.
- **HGA portal properties:** `w3c-cg/holon@3590f5e`,
  `architectures/hga/hga-pass-b-portals.databook.md:192-202`.

## 3. What was decided, and where it is recorded

- #342 merged as `e01384c` (2026-10-15) — git history.
- holon:06 chosen as the next loop; scope = compiler-produced; approach = open-world CONSTRUCT +
  closed-world shape, opt-in `traversal` parameter — spec § 2.
- `etkl:portalTarget` only `rdfs:seeAlso`s `holon:portalTarget` (kind mismatch) — spec § 3.2.
- Out of scope, owed as register rows when the loop ships: per-document compile identity; Clean
  holon membrane health — spec § 6–7. **Not yet raised** in `residues.md`.

## 4. Unverified or assumed

Spec § 8 in full (isomorphism stability, pySHACL SPARQL constraint, six regions), plus:

- That the corpus baseline regenerates byte-identical with `traversal=None` (spec § 5 item 6) —
  a prediction; ~24 min, run after the last input edit.
- That `tests/test_doc_governance.py` accepts a generated `examples/*.ttl` with an isomorphism
  gate — `examples/` is not an Evidence path, so expected unaffected; not checked.
