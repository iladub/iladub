# Ruling — B1, the compile-scope subject (`holon:05`)

**Date:** 2026-08-25 · **Decides:** finding **B1** of
`docs/superpowers/2026-08-25-holon-05-adversarial-review.md` · **`main` @ `81f7f71`** (merge of PR #118)
· **Shape: mechanical** — this file records a decision taken in conversation; it authors no design.

## The ruling

**Option (a): mint a new concrete term `etkl:CompiledDocumentHolon ⊑ etkl:DocumentHolon`, and type the
compile-scope document URI with it.** Chosen by the maintainer, 2026-08-25, from the three options the
review put with their costs. **Recorded here and nowhere else — therefore reversible.**

```
<doc> a etkl:CompiledDocumentHolon ;
      etkl:membraneHealth etkl:Compromised .
```

Not `etkl:CleanDocumentHolon` (B1: its published interior is *"the grounded graph + the promotion
decisions that produced it"*, and the compile graph measurably contains **neither** — 0
`iladub:PromotionDecision`, 0 `iladub:GroundedNode`; and it self-contradicts on the `Compromised`
path, where the value reads *"the holon is not clean"*).

## What the ruling settles, and what it does NOT

**Settles:** spec §4.1's subject; the contradiction on the refusing path, on all three health paths;
and §4.1's claim to close the instantiation half of `R126`, which option (b) would have forfeited.

**Does not settle — still open, and each needs its own ruling before the spec is revised:**

- **B7** — the subject IRI itself. `_DOC = "https://example.org/etkl/doc"` (`compile.py:22`) is one
  hard-coded constant shared by **every** document, carrying no other statement in either compiled
  graph. Typing it `CompiledDocumentHolon` does not change that. Whether `etkl:membraneHealth` gets
  `owl:FunctionalProperty` / `sh:maxCount 1`, and whether the subject is linked to the `…/doc/p0…`
  URIs that carry the content, are **open**.
- **B2** — whether the verdict fact stays a `sh:ValidationReport` or becomes an owned activity node.
  Independent of B1.
- **B3** — the `Weakened` amendment set, which after this ruling **loses one member**:
  `etkl:CleanDocumentHolon`'s comment no longer needs amending, because the loop no longer claims the
  compile graph is one. The other four stand (`Weakened`, `MembraneHealth`, `holonic-interaction.md:160-161`,
  and the criterion's own `prog:statement`).
- **B4, B5, B6, B8** and **P1–P3** — untouched by this ruling.

## Consequences the spec revision must carry

1. **A new term is minted**, so `etkl:CompiledDocumentHolon` needs an `rdfs:comment` that says what
   the compile-scope product *is* — and, per **B8**, it must not claim the graph is fully read.
   `score` and `membraneHealth` are two different signals.
2. **`etkl:membraneHealth`'s `rdfs:domain` is `etkl:DocumentHolon`** (`etkl-holons.ttl:88`), the
   abstract parent — the new subclass sits inside it, so the domain argument of §4.1 survives
   unchanged. **Re-measure rather than assume**: the domain is enforced by nothing today (no shape
   targets it, `inference="none"`), which is why §4.1's original argument was rhetorical.
3. **§4.3's CONSTRUCT changes by one token** — `?doc a etkl:CompiledDocumentHolon`. Everything else
   the review confirmed about that query (executes, discriminates, idempotent, empty without a verdict
   fact) is unaffected.
4. **The `owl:versionInfo` bump `0.1.0` → `0.2.0`** (`:33`) was already planned for §4.6 and now
   carries a new class as well as an amended comment.

## The next concrete action

In a **fresh session, in its first third**: revise the spec from the review's closing list, items 2
onward — item 1 is this file. Rule **B7**, **B2** and **B3** before writing §4.
