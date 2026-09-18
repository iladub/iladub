# Handoff — R213 executed, and the two things that block its end-to-end close

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] was blocked on [[R213]].

**Date:** 2026-09-18.

---

## 5. The next concrete action — **PROPOSED**, and it rests on a prediction that must be RUN

*(Part 5 first, per CLAUDE.md § "The handoff's next action is TYPED". Parts 1–4 are pointers and
records and follow below; they do not degrade.)*

**The subject: derive the `spanned` set for BODY cells, so [[R253]] closes and the live disposal
types on graincorp-capacity.**

**The prediction, and it is falsifiable in minutes:** *supplying the spanned set is the ONLY thing
between the shipped code and a live end-to-end disposal on gcap.* Measured support — with
`spanned` = the 25 column-0 text-layer-empty positions, a live reading disposes to **109** of the
110; with `spanned = ()`, to **0**. Everything downstream of the disposal is already proven with
the addresses supplied (+110 `tab:unshownText`, 110 emptied `cellText`, 406 EntryCells intact,
membrane green).

**Why it is PROPOSED and not asserted.** The prediction assumes the *only* obstacle is the scope of
refusal 3. It may not be: [[R252]] measured the address spaces disagreeing on six of seven
documents, and while gcap is the silent one **under the maximal probe**, a real disposal has never
been carried through `assert_hier_region` on that page end-to-end with a live reading. **RUN THE
PREDICTION FIRST** — hand `region_unshown` a `FakeRegionReader` returning the known 110 ∪ the 26
empty positions, with a hand-supplied spanned set, and compile. If the compile refuses, the subject
is [[R252]], not [[R253]], and the loop this handoff imagines is not the loop to run.

**What NOT to do, and it is the trap this thread is closest to.** Do not write a geometric rule for
*"is this position inside a spanning cell"* — a bbox-covers-row test with a tolerance is exactly the
shape CLAUDE.md § "One geometric attempt, then NEURAL" governs, and this thread has spent no
geometric attempt yet. Do not ask the reader which positions it considers spanned either: a reader
could call everything spanned and evade the null control entirely, which makes the control
circular. The honest candidates are (a) extend R211's span reading from headers to body columns, or
(b) a separate oracle for the span itself. Both are spec work, not a patch.

---

## 1. Where the primaries are

| | |
| --- | --- |
| spec | `docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md` — **§ 8 governs**, the body above it is superseded in place |
| plan | `docs/superpowers/plans/2026-09-17-the-ink-the-page-does-not-show.md` |
| evidence | `docs/superpowers/2026-09-18-unshown-ink-executed.md` — every figure below, with its command |
| terms | `vocab/ontology/tab.ttl` — `tab:UnshownInk`, `tab:unshownText` |
| shapes | `vocab/shapes/tab-physical-shapes.ttl` (widened `tab:WrappedCellShape`), `vocab/shapes/tab-shapes.ttl` (`tab:UnshownInkCellShape`) |
| carriage | `src/iladub/etkl/celltype.py` (crossing A), `src/iladub/etkl/holon.py` (`_UnshownCarriage`, crossing B), `src/iladub/feed.py` (clause 2's guard) |
| worker | `baml_src/unshown_ink.baml`, `src/iladub/etkl/unshownink.py` |
| wiring | `src/iladub/etkl/compile.py`, end of `page_bands`, gated on `BAML_LIVE` |
| instruments | `scripts/unshown_ink_address_control.py` (O7), `scripts/unshown_ink_seam_census.py`, `scripts/unshown_ink_prov_probe.py` |
| tests | `tests/etkl/test_unshown_ink.py` (23), `tests/test_tab.py` (the vocabulary half) |

## 2. What was decided, and where it is recorded

- **Clause 2 is a producer-side guard, not SHACL** — the grounded graph holds 0 `tab:` triples, so
  a shape there would have zero focus nodes forever. Recorded in `tab-shapes.ttl`'s comment and in
  `feed.py`'s guard. The two graphs are deliberately **not** unioned.
- **`tab:cellText` is EMPTIED, not kept** — fail-safe: nine enumerated consumers get the truthful
  answer by default, eight of them want it. Recorded in `tab.ttl`'s `tab:unshownText` comment.
- **The guard is a DISJUNCT, never an exemption** — an exemption would pass a cell whose
  `tab:unshownText` is empty. `tests/tab-unshown-empty-leak.ttl` is the arm that separates them.
- **Readings are NEVER merged across runs** — no union, no intersection, no vote; there is
  deliberately no API for it. Recorded in `unshownink.py`'s module docstring (§ 8.9 item 2, which
  the spec left unanswered).
- **The reader's client is pinned to `claude-sonnet-5`** with the O2 figures beside it in
  `baml_src/clients.baml`. Do not downgrade without re-running O2.

## 3. What is UNVERIFIED, and must not be asserted

- **O5 was NOT taken.** gcap's score movement under a live carriage is unmeasured, and recorded as
  not taken rather than as a null. Do not quote a movement.
- **O3 holds BY CONSTRUCTION**, not by prediction — with the gate off nothing is emptied. It is a
  weaker control than spec § 5 assumed.
- **The enhancement prohibition is unenforceable from the answer alone** (§ 8.9 item 1), and
  [[R254]] is the same hole with a cheaper trigger: Haiku's wrong answer was well-formed, in-grid,
  and undetectable by the shape.
- **`datagrid.py`'s emitter is unwired.** gcap mints 0 cells of that shape; other documents are
  unmeasured for it.
- **RF5's grain problem** (a cell mixing unshown and ordinary ink — cbh has 8) is untouched.

## 4. Raised

[[R252]] (the address spaces disagree on 6 of 7), [[R253]] (no `spanned` set ⇒ live disposal types
0), [[R254]] (the reader is model-sensitive and the shape cannot catch it).

---

*Author: François Rosselet. © 2026. Evidence — CC-BY-4.0 with the rest of `docs/`.*
