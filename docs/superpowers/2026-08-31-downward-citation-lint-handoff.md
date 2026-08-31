# Handoff — R139's instrument is built; the class is now machine-checked in source, and only there

**Topic:** what the downward-citation lint refuses, the four repairs it forced, the two things the
census got wrong that only the implementation could find, and the one gap it deliberately leaves

**This handoff supersedes nothing.** It follows `docs/superpowers/2026-08-31-r139-census-handoff.md`,
whose part 5 was a **fork statement, not a plan** — a design decision with two defensible answers and
no measurement able to settle it. The maintainer ruled **build**, so that fork is **discharged**.

Part 5 is written first, per CLAUDE.md § "The handoff's next action is TYPED".

## 5. The next concrete action — TYPED

### ASSERTED — mechanical, outcome known

Nothing is queued. `R139` is **struck**; the four sites it named are repaired; the register's
open/closed tally moves to **38/143**.

### PROPOSED — rests on a prediction that must be RUN before anything is built on it

**`R153`, the markdown half, is the natural successor and it is NOT a chore.** The row states a
plausible mechanism — *document*-scoped rather than paragraph-scoped referent tracking, on the theory
that a spec names its subject file once in a heading and then cites it for pages — and that theory is
**unmeasured**. Its falsification is cheap and must come first: take the census's 822 `.md` hits, bind
each to the nearest preceding filename **anywhere above it in the document** rather than in its
paragraph, and score precision. If it does not clear the census's 71–99% FP by a wide margin, the row
should be closed as REFUSED with that measurement rather than built. *Budget for refutation.*

### PROPOSED — blocked on rulings, unchanged and NOT re-derived

`R132` (identity/merge), `R127` (four coupled oracles), `R131`(b). Open
`docs/superpowers/2026-08-30-four-rows-closed-handoff.md` § 5 — that table is still the source.

## 1. Goal

Build `R139` disjunct (a) — the instrument half — in the one scope the census proved it can hold, and
strike the row. Done.

## 2. Where the primaries are

| primary | what to establish there |
|---|---|
| `docs/superpowers/specs/2026-08-31-the-comment-cannot-cite-below-itself-design.md` | The rule (§2, derived ONCE), the gate classification (§5), the four sites and why no allowlist ships (§4), and the two corrections the implementation forced (§3) |
| `tests/source_citations.py` | The PROCEDURAL extractor and its irreducibility argument. Read `_ends_paragraph` for the measurement that made the referent unit the paragraph |
| `vocab/shapes/source-citation-shapes.ttl` | The AXIOM half — three conjuncts, closed world, no exemption clause |
| `vocab/internal/srccite.ttl` | The declaration. It is under `vocab/internal/` because `vocab/ontology/` is the published surface and this namespace is unregistered — `docgov.ttl`'s header states the rule |
| `docs/superpowers/residues-closed.md`, `~~R139~~` | Closure evidence, including the two census defects and the F1–F4 falsifications |
| `docs/superpowers/residues-open.md`, `R153` | The markdown gap, with the numbers that make it a gap rather than a chore |

## 3. What was decided, and where that decision is recorded

- **Build, not refuse** — the maintainer's ruling on the census's fork. Recorded in `~~R139~~`'s
  closure text and in this handoff. **Nowhere else; reversible.**
- **No allowlist, no exemption mechanism.** Instead all four flagged sites were re-worded so that each
  says what it means. Recorded in spec §4 and `~~R139~~`.
- **The gate split is PROCEDURAL extractor → AXIOM (SHACL) membrane**, not pure Python. The objection
  (a membrane needs vocabulary, and vocabulary is a published surface) was **refuted by measurement**:
  `dg:` is repo-internal and unregistered, `grep -rln docgov vocab/ontology/` returns nothing. Spec §5
  records the argument *and* the fallback if the maintainer rules against proliferating internal
  namespaces.
- **`_pre_loop_artifacts()` was repaired, not re-pinned.** It reconstructed a fixed historical tree by
  a proxy (`artifact_files()` minus `vocab/internal/`) that every later loop silently corrupts; it had
  already drifted 136 → 141 and stayed green only by luck. It is now read from git at
  `72d0cffc` — `git ls-tree` reproduces 136 exactly. Recorded in that helper's docstring.
- **Five pinned counts were re-measured, never copied**: `artifact_files()` 144 → 146, internal
  vocabularies 3 → 4, the census 56 → 57, owned-prefixed literal occurrences 21 → 22 and distinct
  values 8 → 9. Each carries its re-measurement note in place.

## 4. Unverified or assumed

- **The full `-m "not corpus"` suite result is recorded in the PR body, not here** — this section was
  written while it was still running. If the PR body does not carry a green figure, it did not finish.
- **The corpus-marked suite was NOT run.** Unchanged for four loops now.
- **`R139`'s census numbers are NOT re-verified by this loop**, and two of them are now known to have
  been produced by a defective regex (the anchored branch could never match). The *filter-ladder*
  counts that survive are the ones this loop reproduced at HEAD: 76 comment-line tokens → 10 downward
  → 7 within EOF. **The 0.7% tree-wide precision figure and the `docs/**` 71–99% figures were NOT
  re-derived**, and `R153` rests on them — that is where to attack it.
- **The comment-line restriction is not load-bearing at HEAD** (scanning every line yields the same 7).
  It is kept on the argument in spec §2, not on a count.
- **Nothing checks that a repaired comment's grep still finds what it claims.** The lint refuses a
  line number; it cannot tell whether `grep -n MEMBRANE_HEALTH_RQ` still resolves. That is a strictly
  weaker guarantee than the one the four comments now assert, and no row covers it.
- The 150K executing floor is still labelled `NO SOURCE` in `tiers.py`.
