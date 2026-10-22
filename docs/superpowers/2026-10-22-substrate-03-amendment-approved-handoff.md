# Handoff: substrate:03, spec amendment approved and not yet written (2026-10-22)

**Serves:** prog:criterion:substrate:03 — verify it is still `prog:met false` before starting.

**Topic:** substrate · **Date:** 2026-10-22

**Doc impact: none.** This is a handoff, plus measurement evidence.

Part 5 was written first. The session handed off at about 61K working tokens, 1.2× the 50K
originating floor. It stopped because the amendment and the plan are both originating work. Every
claim below is a measurement committed under
`docs/superpowers/evidence/2026-10-21-substrate-03-seams/`, so nothing in part 5 is graded down for
fatigue.

## 5. The next concrete action, typed

1. **ASSERTED: write the spec amendment** as its own PR against
   `docs/superpowers/specs/2026-10-21-substrate-03-in-engine-policy-design.md`. The maintainer
   approved its substance on 2026-10-22 ("approved"). The approved spec is Evidence on `main` since
   #363, so the amendment **appends** a dated `## Amendment (2026-10-22)` section and edits no
   existing line (CLAUDE.md § Documentation governance). The section carries:
   - **§ 4.1:** two more steward-only required `f:modify` guards. One is `f:onClass f:AccessPolicy`.
     The other is `f:onProperty` over `f:action`, `f:required`, `f:query`, `f:onClass`,
     `f:onProperty` and `f:allow`.
   - **§ 4.3:** a fourth part of the closure set, every predicate on the bundle's own policy nodes.
     Also a class rule: every class whose instances the membrane depends on (`sh:NodeShape` and
     `f:AccessPolicy`) must carry an `onClass` guard, and `closure_violations` names a missing one.
     `rdf:type` stays excluded from the predicate set. The class rule is what covers type retraction.
   - **§ 4.5:** a new oracle, `test_engine_refuses_policy_tampering`. W retracts a guard's
     `a f:AccessPolicy` and gets 403 with t unchanged. W's blank-node `sh:minCount` retraction is
     then still 403, and W's ungoverned commit is still 400. The control: S retracting the same
     triple is accepted.
   - **§ 4.6:** a default-suite case. Drop the `onClass f:AccessPolicy` guard, and the closure check
     names `f:AccessPolicy`.
   - **§ 5:** a new falsification arm. Drop the `onClass f:AccessPolicy` guard, and `policy_tampering`
     fails.
   - **§ 8:** both seams and the composite are now measured. Cite `seams.out`.
2. **ASSERTED: then write the plan** at `docs/superpowers/plans/2026-10-22-substrate-03-in-engine-policy.md`
   with superpowers:writing-plans, from the spec plus its amendment, in a fresh session. Do it inside
   the first third of that session. **The plan needs no seam-measuring task any more.** It can cite
   `seams.out` and `remedy.out` for the engine behaviour each oracle relies on.

## 1. Goal

Unchanged: meet substrate:03 and close R328 (spec § 1).

## 2. Where the primaries are

- The spec is on `main` (#363). The design handoff is
  `docs/superpowers/2026-10-21-substrate-03-design-approved-handoff.md`.
- The new evidence is in `docs/superpowers/evidence/2026-10-21-substrate-03-seams/`. Run each script
  from the repo root with `PYTHONPATH=src:. .venv/bin/python <script>`, about a minute each. The
  scripts reuse `../2026-10-21-substrate-03-probe/probe_lib.py`.
  - `seams.py` / `seams.out`: the full bundle on the shipped `iladub-shapes.ttl`, with the spec
    § 4.3 closure set computed from it (16 shape predicates). Identity is sent by **header** on every
    request. It records:
    - counts U=2, A=2, B=0, W=2, S=3;
    - seam B, W's type retraction of a NodeShape, refused with 403;
    - seam A, rdflib's `_:fdb-…` bytes (typed and list-wrapped) accepted from S with 200, and
      refused from W with 403;
    - the composite, W's ungoverned doc-a, refused with 400 and the INVARIANT text;
    - W's self-promotion, the anonymous commit and B's commit, each refused with 403;
    - the minCount-guard-dropped arm, where W's retraction is accepted (200) and so is the
      ungoverned commit after it (200).
  - `tamper.py` / `tamper.out`: six attempts by W on the policy nodes. Every one is **accepted
    (200)**. Five are harmless. **`DELETE DATA { ex:guardShapesProps a f:AccessPolicy }` disables
    the guard:** W's blank-node minCount retraction is then accepted (200) and so is the ungoverned
    commit (200). That is the hole.
  - `remedy.py` / `remedy.out`: the same six attempts and the config-node type retraction, with and
    without the two new guards. Without them, the config type retraction is already 403. With them,
    all seven are 403, and the membrane holds after each one. Controls: W's doc-a commit is
    accepted (200), and S's retraction of a guard's type is accepted (200).

## 3. What was decided, and where it is recorded

- The maintainer approved the amendment's substance in chat on 2026-10-22 ("approved, go ahead"),
  as part 5 item 1 lists it. This handoff is the record until the amendment PR lands.
- #363 merged after a header fix (`8d1587d`). The parser rejected the handoff's `**Serves:**` line
  because of a trailing period, and the file had no `**Topic:**` line.

## 4. Unverified or assumed

- Everything here was measured on macOS aarch64 only. Linux first runs it in the `substrate` CI job
  on the implementation PR.
- `onClass` was not checked against a policy node typed only through an RDFS subclass of
  `f:AccessPolicy`. This is the carried RDFS-reach item (spec § 7).
- The probe guard IRIs are under `ex:`. The shipped bundle's IRIs are the plan's to choose.
