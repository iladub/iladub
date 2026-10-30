# Handoff 2026-10-30: finish the contract:01 spec under the HDC-first design

**Serves:** maintenance — contract:01 is not yet in `tests/arc-manifest.ttl`; this finishes the spec that adds it.

## 5. Next concrete action (written first; typed)

**Asserted:** in a fresh session on branch `contract-rung-spec`, update
`docs/superpowers/specs/2026-10-30-contract-rung-design.md` § 2 rulings 1, 2, 4 and 5 to the
HDC-first design's decisions 1, 5, 8, 13 and 16, and remove every step that edits hdc-contract
(§ 6.3 "a label fix happens in hdc-contract", § 6.5 "what hdc-contract reads", § 11 Q3). Then work
the open review items 4–9 and put the § 5 segmenter rewrite to the owner.

**Proposed** (may fail): that § 6.5's seam can simply be deleted. It may instead need restating as
"what contract:02 reads", because contract:02 consumes the same graph. Check § 4.1 and § 7 of the
HDC-first design before deleting.

## 1. Goal

Get contract:01's spec to a state the owner approves, so its plan can be written and it can merge
before contract:02 is planned.

## 2. Where the primaries are

- `docs/superpowers/specs/2026-10-30-hdc-first-contract-compiler-design.md` § 2: the 16 owner
  decisions. Decision 11 (sequence) and 16 (hdc-contract paused) bind contract:01.
- `docs/superpowers/specs/2026-10-30-contract-rung-design.md`: the spec to finish.
- `docs/superpowers/2026-10-30-contract-rung-spec-review-handoff.md` § 4b: review items 4–9.
- `docs/superpowers/2026-10-30-contract-semantic-model-first-handoff.md` and
  `2026-10-30-handoff-hdc-first-contract-compiler.md`: the two handoffs this session reconciled.

## 3. What was decided, and where

- All 16 decisions: the HDC-first design § 2, committed on this branch. Decision 16 (hdc-contract
  paused, out of scope) is also in memory `hdc-first-contract-compiler`.
- That contract:01 lands as drafted, before contract:02: decision 11.

## 4. Unverified or assumed

- Whether 48 cl.7 (contract-rung spec Q6) can be disposed without hdc-contract. Decision 16
  forbids a scheme edit, which leaves a dated adjudication or the trader. Nobody has asked the
  trader.
- The `gco` snapshot is still vendored from hdc-contract. Reading it is consumption, which I take
  to be allowed under decision 16. The owner did not say so explicitly.
- This session ended about 1.4× past the 50K originating floor (logged override). The design's
  edits after the builder check were made past the floor.
