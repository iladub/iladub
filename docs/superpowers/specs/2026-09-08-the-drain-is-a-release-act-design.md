# Spec — the drain is a release act: R185's fork, ruled

**Status:** design, ruled — implemented in this loop.
**Residue:** [[R185]] (`docs/superpowers/residues-open.md`) — read the row first; it states the
fork and its three measurements. This spec rules it and corrects two of the row's own framings.
**Prior:** `docs/superpowers/specs/2026-07-31-documentation-governance-design.md` §5.1, §7 (the
`Doc impact:` declaration and the release gate), `docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md`
(the one document that has ever declared `contradiction`).

**Doc impact: increment.** One new owned term family in the `dg:` namespace
(`dg:ContradictionDrain`, `dg:drains`, `dg:drainedOn`, `dg:drainedBy`, `dg:drainEvidence`), one new
shape, one new register file, and one `RELEASE.md` step. No published Assertion page changes; no
site page is contradicted. **`CLAUDE.md` § Documentation governance gains a sentence naming the
drain register** — flagged for the maintainer, NOT edited here (the Contract is edited only on
explicit request).

---

## 0. The claim, in one line

**A contradiction is drained by the release that fixes the page, so the drain is a release-time,
releaser-attributed act — and it cannot be recorded inside a document written a month before the
fix existed.**

## 1. What is actually broken

`scripts/release_gate.py` exits 1 and has done since 2026-08-10. MEASURED 2026-09-08:

```
$ PYTHONPATH=src python3 scripts/release_gate.py ; echo "EXIT=$?"
RELEASE BLOCKED — undrained contradiction(s) since 2026-08-02:
  - docs/superpowers/plans/2026-08-10-the-decision-membrane.md
  - docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md
EXIT=1
```

**The contradiction is genuinely drained.** It named two sentences —
`docs/wiki/concepts/promotion-decision.md` and `decision-holon.md` claiming the membrane enforces
the promotion invariant — and both are now true and name their call sites. MEASURED:

```
$ grep -n "compile._validate\|validate_shapes" docs/wiki/concepts/{promotion-decision,decision-holon}.md
docs/wiki/concepts/decision-holon.md:29:enforced at `compile._validate` (`src/iladub/etkl/compile.py`) and at
docs/wiki/concepts/promotion-decision.md:62:- `src/iladub/etkl/compile.py`'s `_validate` — the compile membrane, which now
docs/wiki/concepts/promotion-decision.md:64:- `src/iladub/feed.py`'s `ground_document(..., validate_shapes=True)` — the
$ grep -n "def _validate" src/iladub/etkl/compile.py ; grep -n "validate_shapes" src/iladub/feed.py | head -1
668:def _validate(graph: Graph,
619:                    validate_shapes: bool = False) -> FeedResult:
$ git log --format='%h %ad %s' --date=short --since=2026-08-10 --until=2026-08-13 \
    -- docs/wiki/concepts/promotion-decision.md docs/wiki/concepts/decision-holon.md
3251d5f 2026-08-11 docs: close R69, R81, R82 — the decision membrane is enforced, and says where
```

So the gate is a **false block**, and it is a **deadlock, not a delay**. `_since_date`
(`scripts/release_gate.py:30-41`) advances only at the *next* tag, so the block clears one release
after the one that fixed the page — i.e. it blocks precisely the release that drains it. Nothing a
human can do to a wiki page changes any triple the query reads. The gate has never been released
through: the last tag, `v0.0.3`, is dated 2026-08-02, eight days before the declaration.

## 2. How rare this is (it changes what machinery is justified)

MEASURED with the extractor the membrane and the gate both use — **not** with a grep over the
prose, which does not reproduce (a `grep -c contradiction` over `Doc impact` lines returns 13,
because the word appears in declarations that are not `contradiction`):

```
$ python3 -c "…Counter(extract(Path('.')).objects(None, DG.docImpact))…"
  increment       50
  none            29
  contradiction    2      # the 2026-08-10 spec, and the plan that inherits from it
  total dated specs/plans carrying a declaration: 81
```

**2 declarations of 81, and they are one contradiction** — the plan's says so in its own words
("inherited from the spec"). This is a rare, deliberate act, which argues for a *correct and
legible* mechanism over a cheap one, and against anything elaborate.

## 3. The ruling

**Arm 2 wins: the drain is recorded OUTSIDE the evidence file, in a register the gate's query joins
against.** Arms 1 and 3 are refused, on grounds that are partly the row's and partly this spec's.

### 3.1 Arm 3 is refused — MEASURED, and the row's stated objection understates it

R185 refuses arm 3 for "[[R26]]'s day-granularity hole made load-bearing". That is true and it is
not the fatal defect. Making `?since` inclusive of the tag being built makes the gate **vacuous**:
every spec in the repo is dated before the release that is being tagged, so nothing can ever block.

```
$ python3 -c "…blocking_docs(extract(Path('.')), since)…"
2026-08-02 -> ['docs/superpowers/plans/2026-08-10-the-decision-membrane.md',
               'docs/superpowers/specs/2026-08-10-the-decision-membrane-design.md']
2026-09-08 -> []
```

`2026-09-08` is what `?since` becomes under arm 3 during a release run on that date. The gate
returns no blockers — **not for these two docs, but for any document that could ever exist.** A
gate that cannot fire during the run it gates is not a gate. Refused.

### 3.2 Arm 1 is refused — but NOT for the reason R185 gives

R185 refuses arm 1 because it "makes Evidence mutable in the one field the gate reads, which is the
property the class exists to forbid." **That argument does not hold, and this spec withdraws it.**
MEASURED: nothing enforces Evidence immutability. `tests/test_doc_governance.py` runs a SHACL
membrane and two staleness derivations; there is no immutability check, and the 2026-08-10 spec was
in fact edited on 2026-08-11, after loop close, with nothing complaining. Appending is also not
mutation: the original `**Doc impact:** contradiction` line survives verbatim either way.

Arm 1 is refused for three other reasons, in decreasing order of force:

1. **It puts a release-time fact inside a document authored before the fix existed.** The
   2026-08-10 spec's appended note ends *"No contradiction remains, so the release gate
   (`scripts/release_gate.py`) is unblocked by this spec."* That sentence is **false**, and was
   false when written: the spec cannot reach the gate, and the gate blocked on it for a further
   four weeks. Arm 1 does not merely permit that claim — it is the claim, legalised.
2. **It lets the blocked document certify its own release.** The raise and the drain would be
   authored by the same file. The asymmetry matters: a self-declared *block* is conservative and
   costs nothing, a self-declared *unblock* is permissive and is exactly what § Core design
   principles 3 forbids — a proposition passing as an assertion.
3. **It buys procedural code where arm 2 buys none** (CLAUDE.md §8). Arm 1 needs a second regex in
   `docgov_extract.py` plus supersession logic over declaration order. Arm 2 adds a `.ttl` the
   graph already knows how to read and one `FILTER NOT EXISTS` in the existing AXIOM. Procedural
   code must be earned; here it is not.

**The residues-register precedent supports arm 2, not arm 1.** CLAUDE.md § Deferred residues rules
that a closure is recorded *in place*, next to the raise — but the thing it rules that about is a
**dedicated mutable register**, which is what arm 2 builds. The precedent is "record repairs in a
register", not "record repairs in the evidence they repair".

### 3.3 What arm 2 does NOT fix, stated plainly

The drain register is still a **human judgment, self-recorded**. Nothing mechanically verifies that
the named page was actually fixed — SHACL cannot read prose. What changes is that the judgment is
**separated from the claim, dated, attributed, and enumerable in one file**, instead of being a
sentence inside the document it exonerates. That is the same trade `dec:DecisionHolon` makes
everywhere else in this repo: accountability, not proof.

## 4. The design

### 4.1 The register

`tests/docgov-drains.ttl` — a tracked, hand-authored register, alongside the precedents
`tests/corpus-manifest.ttl` and `tests/arc-manifest.ttl`, and alongside `tests/docgov_extract.py`,
which is where this machinery already lives (`scripts/release_gate.py` imports it from there).

**It is deliberately NOT under `docs/superpowers/`.** That directory is Evidence, whose mutable
exceptions CLAUDE.md enumerates as exactly two (`residues.md`, and a gated generated cache). Adding
a third would require editing the Contract. A `.ttl` under `tests/` needs no exception: the doc
extractor walks `git ls-files *.md` and never sees it.

Each drain is a node, not a property on the doc — it is an accountable record with its own identity:

```turtle
dg:ContradictionDrain      # a released fix for a declared contradiction
    dg:drains        →  the dg:Document IRI that declared it   (exactly 1)
    dg:drainedOn     →  xsd:date the affected page was fixed   (exactly 1)
    dg:drainedBy     →  who ruled it drained                   (exactly 1)
    dg:drainEvidence →  the page(s) fixed and what makes the
                        claim true — commit, call site, page    (≥ 1)
```

The doc IRIs use the extractor's own `_DOC` scheme (`https://w3id.org/iladub/docgov/doc/<path>`) so
the register joins the extracted facts with no glue.

### 4.2 The gate

`scripts/release_gate.py` parses the register into the facts graph before running the query. The
rule stays entirely in the `.rq` (the file's own docstring requires this: *"nothing here decides
what blocks"*), so the runner gains a `Graph().parse(...)` and nothing else.

`vocab/queries/docgov-release-gate.rq` gains one clause:

```sparql
FILTER NOT EXISTS { [] a dg:ContradictionDrain ; dg:drains ?doc . }
```

Open-world and evidence-positive (CLAUDE.md §8): a doc stops blocking only when a drain record is
*present*. Absence of a drain blocks, which is the conservative direction.

### 4.3 The membrane

`vocab/shapes/doc-governance-shapes.ttl` gains `dg:ContradictionDrainShape`, targeting
`dg:ContradictionDrain`, requiring:

- **cardinality** — `dg:drains`, `dg:drainedOn`, `dg:drainedBy` exactly 1; `dg:drainEvidence` ≥ 1
  with a non-empty string;
- **the drain must drain something real** — its `dg:drains` target must be a `dg:Document` that
  declares `dg:docImpact "contradiction"`. A drain naming a doc that never declared one is a
  record of nothing, and would silently keep working if the declaration were later removed;
- **the drain cannot predate the declaration** — `dg:drainedOn >= dg:docDate` of the drained doc.
  Without this, a drain can be back-dated to before the contradiction was raised.

The last two are the reason the register is loaded into the *same* graph the membrane validates:
both are joins against extracted facts, expressible only there.

### 4.4 `RELEASE.md`

Step 2 gains the drain instruction: what to record, in which file, and that recording a drain
without fixing the page is the one thing this gate cannot catch.

## 5. The falsifying oracle

Three checks, and the first is R185's own stated closure condition:

- **O1 (the closure condition)** — `scripts/release_gate.py` exits **0**, with the two 2026-08-10
  docs still declaring `contradiction` verbatim. No Evidence file is edited.
- **O2 (the gate still fires)** — delete the register, or the drain record for either doc, and the
  gate returns to exit 1 naming that doc. This is the falsification O1 alone cannot supply: a gate
  that passes because the query broke is indistinguishable from one that passes because the drain
  was recorded.
- **O3 (the membrane refuses a bad drain)** — a leak fixture per §4.3 clause: a drain missing its
  evidence, a drain naming a doc that declares `increment`, and a drain dated before its doc.
  Each must fail `test_membrane`; the register as shipped must pass it.

## 6. What is NOT done in this loop

- **No `dec:DecisionHolon` modelling of the drain.** Principle 4 would justify it — a drain is a
  membrane crossing — but `contradiction` has been declared twice in the repo's life (§2) and
  `dg:` already has its own vocabulary and membrane. Recorded as the upgrade path, not built.
- **No repair of [[R26]]'s day-granularity hole.** A contradiction dated the same day as the
  previous tag is still missed; `RELEASE.md` step 2 still carries the manual eyeball. Arm 3 was the
  arm that would have made it load-bearing, and arm 3 is refused, so the hole stays exactly as
  wide as it was.
- **No enforcement of Evidence immutability.** §3.2 measures that nothing enforces it. That is a
  real finding and a separate loop; this spec relies on it only to withdraw an argument, never to
  license an edit.
- **No `CLAUDE.md` edit.** The Contract is edited on explicit request only. § Documentation
  governance should gain a sentence naming `tests/docgov-drains.ttl`; raised for the maintainer.
