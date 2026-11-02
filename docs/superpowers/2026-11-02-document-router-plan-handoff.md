# Handoff 2026-11-02: the document router plan is written; execute it subagent-driven

**Serves:** maintenance — project 2 of the contract:01 rescope (router).

Authored at ~103K working tokens (2.1× the 50K originating floor). Part 5 was written first; the plan
itself was authored at ~60–100K, so its design calls are graded in part 4.

## 5. Next concrete action (typed)

1. **Asserted** (mechanical): confirm PR #387 (the spec) is merged; it was green and CLEAN at
   handoff, waiting for the owner. Then `git rebase --onto origin/main de711c42 document-router-plan`
   (the branch has only the plan + this handoff on top of the spec's head), push, and open the plan PR.
2. **Asserted** (mechanical): in a fresh session, run superpowers:subagent-driven-development on
   `docs/superpowers/plans/2026-11-02-document-router.md` **on that same branch** (one PR = plan +
   execution, the #384 precedent). Task 1 first.
3. **Proposed** (may fail in minutes): Task 1 Step 1. TypeSafe may expose no OpenAI-compatible
   endpoint, and then Jev is out of this loop and Haiku decides alone. The plan budgets for that.
4. **Proposed** (may fail; costs a model pass): Task 9 Step 6, the boundary-oracle falsifier. If any
   forced page-top split is admitted, the loop stops before the live run and the next loop strengthens
   the oracle.

## 1. Goal

Execute the router plan: split a text PDF into documents and type each one (contract / not a contract
/ refused), traced, scored against bar B1–B6 on 27 text PDFs + m4.

## 2. Where the primaries are

- Plan: `docs/superpowers/plans/2026-11-02-document-router.md` (branch `document-router-plan`,
  commit after 5d32f8f3). Its "Measured" lines carry their own evidence.
- Spec: `docs/superpowers/specs/2026-11-02-document-router-design.md` (PR #387, head de711c42).
- Readings-cache pattern the plan reuses: `src/iladub/etkl/caption.py:199-245`.
- Leak guard that fixes where the scorer lives: `tests/test_synthetic_contracts_leak.py`.
- Population pins: `tests/test_artifact_declarations.py:76-77` (254 `.ttl`, 59 `.rq` on this base).
- Local PDFs: `synthetic/out/` (gitignored); rebuild with `python -m scripts.synthetic_contracts build`.
- Worktree trap: a fresh worktree lacks `.venv`, `baml_client/`, `corpus/`, `held-out/` (this
  worktree has none of them; the main checkout's `.venv` was used for measuring).

## 3. What was decided, and where

- Execution method **subagent-driven**: owner, in chat; recorded in the plan header.
- Every design call in the plan (no HDC rung, two holons per document, the exact boundary oracle,
  refused-tail, B4 over asserted pairs only, hashed rule cues, m4 composition): **recorded only in the
  plan**, not yet reviewed by the owner beyond choosing the method. They are reversible.

## 4. Unverified or assumed

- That pdfium's generated line-break chars count in `count_chars()` with an empty box (Task 3 measures).
- The gist IRI `https://w3id.org/semanticarts/ns/ontology/gist/Content` (Task 2 measures).
- That the boundary oracle refuses false page-top splits (Task 9 Step 6 is its falsifier).
- That hashed cue rules fire on held-out fill 3 at all (B5): cues from fill-specific lines never will.
- That the corpus-baseline regenerate moves only `inputs.json` (Task 10 Step 1 stops otherwise).
- That a 2–3-word model `proposed_type` label stored in readings is not "template text".
- Graded design calls (authored past the floor): the boundary oracle's "disjoint party lines" clause is
  the weakest piece; the plan's own falsifier exists for that reason.
