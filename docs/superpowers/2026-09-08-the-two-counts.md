# The two counts — [[R186]] and [[R187]] measured, and what they do to their own forks

**Loop:** `the-two-counts`, 2026-09-08. Ran action **5a** of
`docs/superpowers/2026-09-08-release-v0-0-4-handoff.md` (typed ASSERTED there), which said both
open forks are blocked on the same missing thing: a count.

**This document records MEASUREMENTS and nothing else.** No arm is chosen, no lint is designed, no
page or test is repaired. Both forks stay open, and the session that takes them starts fresh — the
counts were taken at 1.9× the originating floor, which is exactly why the design is not here
(CLAUDE.md § Loop & context hygiene).

**Doc impact: none.**

---

## 1. [[R186]] — how often has Evidence been edited after loop close?

**Population** 331 tracked files under `docs/superpowers/**`; **327** after excluding the register
(`residues.md`, `residues-open.md`, `residues-closed.md` — the 2026-08-12 split inherits the named
exception) and one gated generated cache (`arc-dependency-landscape.md`,
`tests/test_arc_landscape.py`).

**Definition used.** Introducing commit = earliest commit touching the path. Post-close edit = a
later commit that is neither the same PR nor the same calendar day. **The date is the real
separator, and it is a proxy**: 485 of 487 later-commit events have no `(#NNN)` on at least one
side, because most of this tree predates the 2026-08-31 branch-protection ruling and was pushed
straight to `main`.

**The count is almost entirely a function of where the line is drawn, so it is reported as a
curve, not a number:**

| threshold | files | events |
| --- | --- | --- |
| ≥1 day | **20** (6.1%) | 26 — 6 APPEND, 20 REWRITE |
| ≥2 days | **5** | 6 |
| ≥3 days | 2 | — |
| ≥7 days | **0** | **0** |
| any later commit, same day included | 123 (37.6%) | — |

The collapse from 20 to 5 has one cause: **the dominant "post-close edit" is a `**Status:** … →
SHIPPED` stamp landing the next day**, which is arguably the loop *closing* rather than an edit
after it. Trailing-newline artifacts were checked and there are none — every diff with ≤3
deletions was read, and all are real modified lines.

**Rewriting, not appending, is what has actually happened**: 20 of 26 events delete or modify an
existing line.

### Two corrections to [[R186]]'s own framing

1. **R185's single known case is confirmed present — and R185 saw half of it.**
   `specs/2026-08-10-the-decision-membrane-design.md` at `3251d5f` (2026-08-11) is **+10/−1, a
   REWRITE**: the "Doc impact — RESOLVED" block was appended *and* the `**Status:**` header was
   rewritten from "awaiting review" to "implemented". R185's argument that *appending is not
   mutation* rested on this case being an append. It is not purely one.
2. **The strongest case admits the offence in its own commit subject.** `265275d` (2026-08-31, six
   days after introduction): *"close(register): R137, R152, R138 — three guards, and the rule
   broken while applying it"*. It rewrote a dated spec's §4.5 pointers from line numbers to symbols
   under [[R138]], and its inserted note reasons in prose about how far it may go. **The norm is not
   being violated in ignorance; it is being negotiated case by case** — which is what an unenforced
   norm looks like.

### What the measurement cannot see

Squash merges make *within-loop* edits invisible: a file rewritten inside its own PR, after that
loop's review closed, does not appear here at all. And a pre-PR multi-day loop is indistinguishable
from a post-close edit by date alone. **6.1% is a floor on "edited after the introducing commit"
and a proxy for "edited after close".** Confidence: medium at ≥1 day, high at ≥2.

## 2. [[R187]] — how many wiki decimals are corpus measurements, and how many still hold?

**Sweep** `git ls-files docs/wiki` (12 files) × `grep -noE '[0-9]+\.[0-9]+'` → **44 decimals**.
Nothing excluded: the wiki carries no version strings, no decimal dates, no numeric frontmatter.

| bucket | count |
| --- | --- |
| **CORPUS MEASUREMENT** | **26** |
| THRESHOLD / PARAMETER | 9 |
| VERSION / IDENTIFIER | 8 (spec section refs, one exemplar id) |
| OTHER | 1 (an `xsd:decimal` lexical form) |

**Of the 26: STALE 6 · LIVE 11 · UNKNOWN 9.**

**The six stale reduce to exactly TWO distinct quantities** — the stem document score and the apple
document score — **which are the two [[R187]] already named. The whole-wiki sweep found zero new
stale quantities.**

| file:line | figure | evidence it is stale |
| --- | --- | --- |
| `data-grid.md:174,188,206` | `0.9654553611484971` | [[R174]]; `tests/test_corpus_stem.py:377` asserts `== 0.9658886894075404` |
| `table-holon-compilation.md:119,177` | `0.9655` | same quantity at 4 dp; current value rounds to `0.9659` |
| `data-grid.md:205` | `0.35560344827586204` | `tests/etkl/test_adoption_document.py:376`, `tests/corpus-manifest.ttl:120` |

**Present tense vs dated: 21 / 5.** All six stale figures are in the present-tense 21, and three
assert currency in words — *"unchanged at"*, *"the **live** stem"*, *"the **live** 3-page GrainCorp
stem"*. That is R187's claim, measured.

**Concentration: 2 of 12 pages carry all of it; 8 pages carry no corpus measurement at all.**
`data-grid.md` is 4/12 stale per occurrence, `table-holon-compilation.md` 2/6 — the same rate.
**An outlier in concentration, typical in kind:** the predictor is not the page, it is the
quantity. Every wiki mention of a **document-level score** for a corpus document whose score has
moved is stale; no other class is.

### Four findings that bear on the fork more than the count does

1. **The staleness is not confined to `docs/wiki/**`** — `tests/etkl/test_datagrid.py:1085` still
   says *"the whole stem is one chain of 3, 2152 cells, at `0.9654553611484971`"*, post-[[R174]],
   outside R187's stated scope. **R187's scope is wrong**: the class is document-level score
   mentions repo-wide, not decimals in the wiki.
2. **[[R174]]'s re-baseline was half-applied.** `tests/test_corpus_stem.py:377` moved to the new
   figure; **`:421` still uses `assert standalone.score < 0.9654553611484971`** as a live
   comparator bound. Not a broken test — it is a floor — but the superseded number is executing.
3. **Precision defeats naive matching.** `0.9655` and `0.9654553611484971` are the same quantity. A
   lint grepping R187's own full-precision literal finds 3 of the 6 and misses
   `table-holon-compilation.md` entirely.
4. **`updated:` — R187's own stated fallback — is itself wrong on one of the two offending pages.**
   `table-holon-compilation.md` declares `updated: 2026-08-03` while its line 32 cites a
   2026-09-07 spec. A reader trusting the frontmatter would date that page five weeks early.

Two further notes on method: **"a test carries the figure" ≠ "a test pins it"** —
`tests/test_corpus_stem.py:406` carries `0.9706` and explicitly disclaims pinning it, so it is
UNKNOWN, not LIVE. And **UNKNOWN is not evenly ignorant**: `88.6` / `70.6` (apple x-coordinates,
`data-grid.md`) appear **nowhere else in the tree** — no test, no register row, no source comment.
Those are the figures no future loop can check at all.

## 3. What this does to 5b, stated as weakly as the evidence supports

The handoff's 5b proposed that [[R186]] and [[R187]] are **one loop**, and named its own falsifier:
it fails if the counts come back with opposite shapes — Evidence rewrites near-zero while wiki
staleness is widespread.

**The falsifier did not fire.** Neither is widespread: 5 files at a two-day threshold, 2 distinct
stale quantities.

**But it did not confirm, either, and the reason is in the remedies rather than the counts.** R186's
instrument is a git-history rule with a grace window — and at ≥7 days it would fire on **zero**
historical cases, which makes it cheap and also makes it prove little. R187's cannot be a git rule
or a grep: the predictor is a quantity class at any precision, `1.0` is unclassifiable without its
sentence, and the population leaks into `tests/`. Same question — *is a claim's provenance carried
in the file, or in an instrument?* — pointing at two different instruments.

**Whether that makes them one loop or two is a design judgement, and it is deliberately not taken
here.** Both rows stay open with their arms intact. CLAUDE.md § Plan authoring discipline rule 6
says a spec that argues one invariant in three places was never finished; this document records
what was measured and stops.
