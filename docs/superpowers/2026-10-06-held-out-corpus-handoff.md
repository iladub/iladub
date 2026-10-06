# Handoff: a held-out corpus, then contracts (2026-10-06)

**Serves:** maintenance — the maintainer's direction once the corpus reached 7/7 (PR #311).

**Topic:** strategy · **Date:** 2026-10-06

**Doc impact: none.**

The parts are in the order this format requires. Part 5 was written at about 67K working tokens,
past the 50K originating floor, so each action carries its own grade.

## 1. Goal

Find out whether the 7/7 generalises. Compile documents the compiler has never been tuned on, with
**no `src/` change**. Then, as a separate loop, move the benchmark from *read* to *grounded under a
contract*.

## 2. Where the primaries are

- `tests/corpus-manifest.ttl`: the seven documents, their verdicts and floors. Establish there the
  fields a document entry needs (`cor:file`, `cor:url`, `cor:family`, `cor:sha256`, `cor:pages`,
  `cor:producer`, `cor:fetched`).
- `scripts/fetch_corpus.py`: fetches every manifest entry. On a first fetch it prints the values
  to pin and writes none of them back.
- `scripts/corpus_verdict_snapshot.py`: score, triples and hash per document. It is the
  measurement instrument.
- `tests/test_arc_manifest.py::test_etkl_criteria_agree_with_the_corpus_manifest`: requires the
  manifest's documents to map one-to-one onto the `etkl` criteria (`set(asserted) == set(computed)`),
  and pins the accepted count at 7. Establish what adding a document there would force.
- `docs/superpowers/2026-10-05-accept-bfs.md` § 5: the proposal this direction answers.

## 3. What was decided, and where it is recorded

- **Maintainer, 2026-10-06, in conversation:** direction (a), a held-out corpus, comes first,
  then direction (b), contracts and grounding, each in a fresh session. It is recorded **only in
  this file** and in the session's memory, so it is not yet settled anywhere else.
- **Deprioritised in the same exchange, recorded nowhere else:** R289, R294 and R44 as loop
  subjects, and raising the floors.

## 4. Unverified or assumed

- **Where held-out readings should live is unmeasured.** Adding a document to
  `corpus-manifest.ttl` looks like it forces an `etkl` criterion per document: the agreement test
  above requires the mapping to be one-to-one, and arc-shapes M6 forbids a sixth rung. That would
  turn a measurement into new benchmark rows. A separate held-out register may be the right home.
  That is a design question for the loop, not settled here.
- **Licensing and domain neutrality** of any new PDF have not been checked. CLAUDE.md requires
  domain-neutral public examples, and `corpus/` is gitignored.
- **Contract coverage**, measured 2026-10-05 by grep: only 3 of 7 documents carry a
  `cor:contract` (all ag-trade). It is measured, but whether a contract can be authored for a
  gov-stats or financial document without new vocabulary has not been examined.
- **Wall time is assumed** from past loops: about 150 s per document offline, and documents run
  serially (concurrent corpus runs have killed the process on memory four times).

## 5. Next concrete action

1. **PROPOSED (the prediction is that the held-out scores fall well below the seven).** Choose 3–5
   public PDFs whose layouts differ from the seven (not ag-trade, not ONS or BFS releases). Choose
   them **before** compiling any of them, and write down why each was chosen. Then fetch, pin and
   compile each one offline at `main`, and record the score and the escalation reasons. **Do not
   change `src/`.** The first decision the loop makes is where the readings live (§ 4, first
   bullet). Settle it before writing to `corpus-manifest.ttl`, because writing there may move the
   etkl bijection. If the prediction fails and the scores land near the seven, the 7/7
   generalises, and that is the finding.
2. **PROPOSED, a later fresh session:** direction (b). Author a contract for one accepted document
   that is not ag-trade, and measure what grounds and what is proposed. Which document depends on
   what item 1 finds.
