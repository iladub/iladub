# Rulings — O2's `Compromised` leg, and where finding 6 lives (`holon:05`)

**Date:** 2026-08-25 · **Decides:** the ruling asked for at the end of
`docs/superpowers/2026-08-25-holon-05-seam-6-refusal-vehicle.md`, plus that file's finding 6 ·
**`main` @ `f9f7a75`** (merge of PR #121) · **Shape: mechanical** — this file records decisions taken
in conversation and one measurement taken to price an option. It authors no design; the spec edits it
requires are listed at the end and are made in `…-the-membrane-reports-its-health-design.md`, not here.

---

## Ruling 1 — O2's third leg: option **(a′)**, a refinement of (a)

**Chosen by the maintainer, 2026-08-25**, from the four options the seam-6 measurement put with their
costs. **Recorded here and nowhere else — therefore reversible.**

### The refinement, and the measurement that produced it

The seam-6 file priced option (a) as *"needs a seam that does not exist on `compile_document`"* → *"new
public surface on the compiler, in a loop that already mints three terms and a shape."* **That price was
measured down before the ruling was taken.** The block is inline in `compile_document`:

```
$ grep -n "ESCALATION_FURNISH_RQ, graph\|if validate_shapes:\|conforms, text, legs = _validate(graph, _legs_for_document\|raise AssertionError(_refusal_message(\"document-level facts\"\|asserted = sum(rep.asserted" src/iladub/etkl/document.py
1609:    graph += interpret.run(ESCALATION_FURNISH_RQ, graph, _escalation_vocab())
1623:    if validate_shapes:
1624:        conforms, text, legs = _validate(graph, _legs_for_document(recognized, section_facts))
1626:            raise AssertionError(_refusal_message("document-level facts", legs, text))
1628:    asserted = sum(rep.asserted for rep in pages)
```

Two consequences fix the shape of the seam:

1. **The seam must START AT OR BEFORE `:1609`, not at `:1623`.** The mutation is a second
   `dec:rationale`; it only becomes fatal once `escalation-furnish.rq` carries it into a second
   `dec:condition` (seam-6: *"before re-furnish: 1 … after re-furnish: 2"*). A seam that begins at the
   validation call cannot be driven by the measured lever.
2. **`:1609–:1626` is already inside this loop's blast radius.** §4.5 mints health at this site and §2.4
   / O7 replace the bare `AssertionError` with `MembraneRefusal`. Extracting the block into one named
   **internal** function is therefore a refactor of code the loop rewrites regardless — **not** a new
   public parameter on `compile_document`, and **not** a test-only backdoor in the public signature.

**(a′) is therefore: extract `:1609–:1626` (furnish → validate → mint health → raise) into one named
internal seam, and have O2's third leg and O7 call it with `real_compiled_graph + one added triple`.**

### Why (a′) over (c), which was the live alternative

**(c) and (a′) cost the same spec amendment.** Both concede in writing that no public input reaches the
document gate ahead of the page gate — seam-6 measured that on three independent routes. Neither can
satisfy O2 as currently worded. So the amendment is not a discriminator, and the question is only what
each buys for it:

| | what produces the `Compromised` value |
|---|---|
| (c) | a hand-built fixture graph, and a `.rq` run over it |
| **(a′)** | a **real compiled document graph**, mutated by **one triple**, re-entering the **real** furnish → membrane → raise path, with **no monkeypatch of `validate`/`_validate`** and **no `validate_shapes=False`** |

(a′) buys strictly more evidence for the same admission. The one-triple mutation is also **not
arbitrary**: it is the exact triple that finding 6 says a language-tagged rationale pair will produce —
so the test pins a latent real defect rather than an invented one.

**Rejected: (b)** — fixing finding 6 first destroys the only measured lever and leaves `Compromised`
with no route at all (the four tab-side levers are gated off by `_legs_for_document` precisely when
they would matter). **Rejected: (d)** — shipping a three-valued property with one unmintable value is
the R106 class this loop exists to close.

### What (a′) still concedes, and where the concession is written

`Compromised` is **not reachable from any public input today**. O2's wording must be amended to say so
in terms, per the seam-6 file's own warning that the plan *"must not silently weaken O2 to make it
pass."* The amendment is Ruling 1's cost, not a way around it — see **Spec edits**, below.

---

## Ruling 2 — finding 6 lives as a residue, named as a successor-loop **candidate**

**Chosen 2026-08-25 on the assistant's recommendation, the maintainer having asked for one.** Same
reversibility.

**Not fixed in this loop** (that is option (b), rejected above). **Raised as `R127`**, with the seam-6
file's findings 7 and 8 raised beside it as **`R128`** and **`R129`** in the same act.

**The reason it is *named* rather than merely appended:** Ruling 1 makes **O2's third leg load-bearing
on `R127` staying open.** Whoever caps `dec:rationale`, collapses the furnish, or admits one condition
per language turns O2 red, and the test itself will not say why. `R127`'s row therefore records that
coupling explicitly — *closing this requires re-homing O2's `Compromised` leg first* — and a row that a
shipped oracle depends on cannot sit unranked among 116 others.

**The three are one subject:** the `dec` membrane does not constrain what it derives from —
`dec:rationale` uncapped while `dec:condition` is capped at 1 (R127); `dec:supersedes` constrained by
nothing at all (R128); a non-IRI `suggester_iri` crashing `membrane.py:348` instead of refusing (R129).
That is a loop, not a patch.

**Candidate, not pre-committed.** `holon:06` is the other named successor (§11 residues 1 and 4 point
at it). The next-loop pick is made at loop close, in the handoff — this ruling only guarantees `R127`
is *visible* there.

---

## What these rulings settle, and what they do NOT

**Settle:** which of the seam-6 file's four options the plan is written against; that O2's standard is
amended openly rather than quietly weakened; that findings 6–8 become register rows in this loop rather
than in a follow-up; and that the `Compromised` lever must survive this loop intact.

**Do NOT settle — these are seams for the plan to MEASURE, per plan-authoring rule 3. Named, not
answered:**

1. **Whether re-entering the extracted seam on an already-furnished graph is a no-op absent the
   mutation.** O2's third leg needs a control arm: the same real graph, re-entered *without* the extra
   `dec:rationale`, must still conform. `escalation-furnish.rq` runs a second time on a graph that
   already carries its own output; measure that the unmutated re-entry conforms before writing the
   mutated one.
2. **Whether any CORPUS document escalates at document scope.** The seam-6 lever was proven on
   `recognized_pair_plus_escalating_page_pdf` (`tests/etkl/test_escalation_wiring.py:33-34,54-61`) — a
   **synthetic PDF generator**, not a corpus document. O2's `Intact`/`Weakened` legs use corpus
   specimens (§5.5); the third leg may not be able to. Measure which, and state it in the oracle's
   docstring rather than letting the reader assume all three legs share a corpus.
3. **What the extracted seam does to `DocumentReport` construction** (`document.py:1636-1639`, keyword
   per R73) — §10 seam 4 already names this; the extraction makes it live rather than precautionary.
4. **Which object `graph` names across the extraction** — §10 seam 3, unchanged and now sharper: the
   seam takes `graph` as a parameter and `:1609` uses in-place `+=`.

---

## Spec edits these rulings require

Made in `docs/superpowers/specs/2026-08-25-the-membrane-reports-its-health-design.md`, cited from the
plan rather than re-derived in it (plan-authoring rule 6):

1. **§7 O2** — amend the third leg and its standard. The sentence *"If a value cannot be produced from
   real input, this test fails and says which — it does not fall back to a fixture"* stands **for
   `Intact` and `Weakened`**; for `Compromised` it is replaced by the (a′) standard: *a real compiled
   graph, one added triple, the real seam, no monkeypatch, no `validate_shapes=False`* — together with
   the written concession that no public input reaches the document gate today, and a pointer to
   `R127`.
2. **§7 O7** — same vehicle, same seam; state that O2's third leg and O7 share it.
3. **§4.5 / §2.4** — record that the mint site is an **extracted internal seam** spanning `:1609–:1626`,
   not an edit in place, and why (the mutation must precede the furnish).
4. **§10 seam 6** — mark ruled, pointing here; its four options are now history, not a live choice.
5. **§11** — `R127`, `R128`, `R129` added with their closing conditions, `R127` carrying the O2
   coupling. Tally snapshot `(24/116 closed)` stands; the next number after this loop is `R130`.
6. **§9** — add: this loop does **not** fix `R127`, and says why (it is the lever O2's third leg runs on).
