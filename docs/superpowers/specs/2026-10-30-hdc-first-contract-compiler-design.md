# Models decide, the symbolic layer reasons, gaps become owned rules: the HDC-first contract compiler (design, 2026-10-30)

**Serves:** prog:criterion:contract:02 — proposed. Neither `contract:01` nor `contract:02` is in
`tests/arc-manifest.ttl` yet. `contract:01` enters through
`docs/superpowers/specs/2026-10-30-contract-rung-design.md` (the *contract-rung spec*), and this
design's criterion follows it.

**Topic:** contract · **Date:** 2026-10-30

**Doc impact: increment.** A new owned package (HDC core), a family-model format, a decision-trace
renderer, and a second contract criterion. Nothing the released vocabulary says changes meaning.

**Status: DRAFT for the maintainer.** It comes out of the 2026-10-30 brainstorm (two sessions:
the hdc-contract handoff `docs/superpowers/2026-10-30-handoff-hdc-first-contract-compiler.md` and
the parallel `docs/superpowers/2026-10-30-contract-semantic-model-first-handoff.md`, both in this
worktree), plus this session's conversation with the owner.

## 1. Intent

iladub's table compiler (etkl) grew a decision layer that nobody, including the owner, can follow
any more. Its concepts are named for the machine's view of the page (bands, gutters, flanks, donor
bands), its thresholds are tuned constants, and compiling is slow. The owner's words (2026-10-30,
verbatim, typos kept):

> humans and machine must have a lingua franca, simple enough so iladub maintenance become easier
> as well as efficiency for compiling. […] the first concenr is not zero llm, it is only where no
> other choice or to catalyze rule compilation we own totally.

and:

> We are not building a document GIS engine, but a semantic one.

This design rebuilds compiling on one division of labour. **Small, cheap deciders (exact rules,
HDC, Jev, a small model) answer named questions. The symbolic layer (SHACL, SPARQL, the family
model) reasons.** Every answer leaves a trace in domain words. The design is tried on GAFTA
contracts first and then carried over to etkl tables (§ 9).

**What success looks like.** As a contract family's model matures, model calls per compiled PDF
fall towards zero, and compile time falls with them. When the owner asks months later why a clause
was typed the way it was, they read the answer in GAFTA's own words, linked to the clause.

## 2. Decisions this design records (owner, 2026-10-30)

These are recorded here for the first time in iladub. Items 1–7 come from the hdc-contract
session (handoff § 3). Items 8–11 come from this session.

1. **iladub's no-LLM rule is softened.** Models **decide, never reason**, and every decision is
   traced.
2. **Spatial evidence is a means, not the product.** Concepts, names and traces stay in the
   domain vocabulary, and geometry appears only as evidence.
3. **Contracts first, then etkl tables.**
4. **Every decision is a named question in domain vocabulary**, answered by the simplest capable
   decider: exact rule, then HDC, then Jev, then a small model. Each answer records the question,
   the evidence, the decider and the confidence.
5. **The HDC core moves into iladub, and hdc-contract imports it.** hdc-contract keeps the
   arbitrage-specific parts (comparison, scoring, bench). This reverses the contract-rung spec's
   ruling 2 and the HDC half of its ruling 5.
6. **Haiku stands in for a small local model** until a local 4–9B runtime exists. It plays the
   same narrow role, so the swap changes only the client.
7. **Establish everything HDC can do first, then fill the gaps with Jev and a small model.**
   The research is `docs/superpowers/research/2026-10-30-hdc-capabilities-research.md`.
8. **The model runs only on gaps, and each answer becomes an owned rule.** When a family's model
   covers a PDF, it compiles with no model call. A gap gets one model call, and its answer is
   written back into something iladub owns, so the next PDF with that gap needs no model.
9. **A calibrated check admits confident answers on its own and asks the owner only about the
   rest.** Every admission is an `iladub:PromotionDecision`, whether the check or the owner made it.
10. **The trace is the human's view.** It is a decision trace in plain domain words, linked to the
    clause, with numbers and examples available but kept out of the main text.
11. **Sequence.** contract:01 lands first, as the contract-rung spec drafts it: no model, exact
    heading match, gUFO fallback, membrane refusals. Its § 2 rulings are updated to items 1, 5
    and 8 above. This design is written now, and its work is built as contract:02 on top of
    contract:01. **The contract:02 plan is written only after contract:01 has merged**, because
    every path and seam it names comes from contract:01.

Items 12–15 were settled in this session after the builder check (owner: "agree with all four").

12. **A model's pick is admitted on its own only when it is inside the candidate set the check
    produced, and that model's measured error rate on owner-validated answers is within α.**
    Otherwise the owner is asked. Each model is calibrated like HDC is (§ 4.5).
13. **"None of these" is a gap, not a final answer.** The clause keeps contract:01's gUFO type
    in the graph, so nothing is left unasserted. It also enters the gap path, so the family model
    learns from it.
14. **contract:02 covers Q-type only.** Learning clause starts for the 13 refused forms moves to
    a later contract:03, because it would revise contract:01's deliberate refusal of
    period-less numbers.
15. **iladub owns the family model, the owner questions and the write-back.** hdc-contract keeps
    comparison, scoring and bench. Its untyped-clause arbitration and `corrections/hero.yaml`
    process are retired once contract:02 lands, so only one system decides a clause.

Item 16 was given after the design was first committed (`754d938`), and it governs items 5 and 15.

16. **hdc-contract is paused, and out of scope, from 2026-10-30.** Work focuses on iladub and on
    contract compiling with concrete GAFTA examples. hdc-contract imports iladub's methods
    **only once they work in iladub, and not before**. No change to hdc-contract is part of
    contract:01, contract:02 or their plans. Its code and ontology may still be **read** as a
    reference, and `gco:` is still consumed through the read-only vendored snapshot.
    Decision 5's "hdc-contract imports it" and decision 15's retirement step happen after the
    pause ends, and are outside this design.
17. **HDC is developed natively in iladub, as a domain in its own right, not a project imported
    or ported.** It is built here on `torchhd`, and it gets a **dedicated skill**, because it is a
    new domain for this repo. hdc-contract's `src/hdcc/hdc/` is prior art that may be read, not a
    source to port. Decision 5 reads, under 16 and 17: *iladub develops HDC; hdc-contract may
    later use iladub's.*

## 3. Goals, non-goals, anti-goals

**Goals**

- G1. The compiler for a known contract family runs **without a model call** on any PDF the
  family model covers.
- G2. Every gap is answered, admitted (by the check or the owner), and **written back** as an owned
  rule, so the same gap never calls a model twice.
- G3. Every decision carries a **trace that renders as plain GAFTA prose**, generated from its RDF.
- G4. **No hand-tuned threshold** anywhere in the decision path. Thresholds are statistics from
  data (conformal quantiles, data-derived bandwidths) or a declared risk tolerance (α).
- G5. HDC is **a native iladub domain** (`iladub.hdc`, on `torchhd`), with its own skill, and it
  works on GAFTA examples. hdc-contract importing it is outside this design (decision 16).

**Non-goals**

- Parties, roles, modality, fillers such as `finalAt`. These are later criteria, as in the
  contract-rung spec § 4.
- The etkl tables rework. § 9 names what carries over, and that work is its own design.
- A local-model runtime. Haiku stands in (decision 6).
- Riders, amendments, multi-document contracts.

**Anti-goals** (this would be a failure even if it worked)

- A decider whose reasons cannot be said in domain words, such as an opaque embedding as the only
  channel or a geometric name in a trace.
- A model call that recurs on the same gap.
- A model answer entering the graph without a `PromotionDecision`.
- A second layer of hand-tuned constants replacing the first.
- Re-authoring HGA, or editing the GAFTA scheme (`gco:`), which is hdc-contract's.

## 4. The architecture

### 4.1 Named questions

The compiler is a list of questions, each named in the domain's words. For contracts, contract:02
covers these:

| question | its answer | first decider tried |
| --- | --- | --- |
| Q-start: where does clause *n* begin? | a line | exact rule (contract:01 § 5) |
| Q-type: what kind of clause is this? | a `gco:ClauseType` concept, or "none of these" | exact rule (heading = label), then HDC |
| Q-family: which family model does this PDF belong to? | a family model IRI | declared by the caller (§ 4.7) |

**contract:02 answers Q-type only (decision 14).** Q-start stays exactly as contract:01 has it.
The 13 forms contract:01 refuses (period-less numbers, sentence case, contract-rung spec M-o) are
gaps in the family model, but closing them is contract:03's: it would revise contract:01's
deliberate refusal of period-less numbers, which look like margin line numbers (contract-rung
spec § 5).

**"None of these" is a gap (decision 13).** A clause no decider can type keeps its gUFO type in
the graph, as in contract:01, and also enters the gap path. On the 67 admitted forms that is up
to 220 clauses before any write-back (contract-rung spec M-i).

Later criteria add questions (which concept does this value denote; which clause does "as per
clause 12" point to). Each enters the same way: a named question, a decider list, a trace
template.

### 4.2 The decider ladder

For each question, deciders are tried in a fixed order, and the first to give an **admissible**
answer decides:

1. **Exact rule:** a SPARQL derivation or a typographic extraction rule. Admissible when it fires.
2. **HDC:** prototype similarity against the family model's examples. Admissible when the
   calibrated check (§ 4.5) returns a set of size 1.
3. **Jev:** a typed choice among the candidates the check left. Jev is an LLM (`jev-1.14.0`,
   reached through a `typesafeai` BAML client in hdc-contract, `baml_src/clients.baml:21`; price
   per `config/prices.yaml:6,9` there). It is given the candidate set, never an open question.
4. **Small model (Haiku):** reads the span and proposes an answer. It is called **only** when
   1–3 leave the question open (decision 8).
5. **The owner (SME):** asked when the check cannot admit the model's answer (decision 9).

Steps 3–5 are the **gap path**. Each answer that comes out of it is written back (§ 4.4), so the
next PDF with the same gap stops at step 1 or 2.

**Why the order** (my reasoning): cost, determinism and explainability all fall as you go down the
ladder. Exact rules and HDC are deterministic, CPU-only, and explain themselves in words. Jev
is cheap and typed. Haiku is the most capable and the least owned.

### 4.3 The family model

The family model is what makes "compile against the model" true (the parallel handoff's two
phases: **model once per family, compile per PDF**). For GAFTA it holds:

- the clause types: a **reference** to the `gco:` scheme (hdc-contract's, consumed, vendored
  read-only per the contract-rung spec § 6.3), never a copy;
- the **durable examples** behind each HDC prototype: clause-type label, the example's text
  source (form and clause number, not GAFTA text where licensing forbids it, § 8), who
  admitted it, and when. Prototypes are rebuilt from examples, never stored (research § A,
  "durable memory, transient prototypes");
- the **written-back rules** from § 4.4, each with its `PromotionDecision`;
- the **calibration set**: the SME-validated answers the conformal check is computed from.

**Format: JSON-LD** (the owner's stated preference), with a published `@context` mapping to the
owned vocabulary. Turtle is produced from it for SHACL validation.

**Per family, with per-form refinement** — my call. One GAFTA model, where a rule or example can be
scoped to a form number when the forms disagree (Nos. 48 and 64 have different clause lists, per
the parallel handoff § 4). Starting per form would multiply models before any disagreement is
measured.

**It lives in iladub (decision 15)**, under the owned root, CC-BY. iladub is the only writer.

### 4.4 Gap to owned rule

When the gap path answers a question:

1. Haiku's (or Jev's) answer is a **proposition**: an `iladub:CandidateConcept`-style record
   carrying the question, the span, the decider and its stated evidence.
2. The calibrated check (§ 4.5) decides whether to admit it. If yes, the check admits it. If not,
   the owner is asked, given the candidate set and the span.
3. Admission is an `iladub:PromotionDecision` (a `dec:DecisionHolon`). `prov:wasAssociatedWith`
   names the check or the owner, and `prov:used` names the proposition and the evidence.
4. The admitted answer is **written into the family model** as a new HDC example, a new label, or
   a new rule, and the model is versioned.
5. The compile resumes. This PDF's answer is the admitted one.

A rejected proposition stays quarantined, as iladub's § 3 epistemics already require. It is never
dropped and never asserted.

### 4.5 The calibrated check

From research § C, unvalidated on our data:

1. **Noise gate.** z = sim₁·√D against Φ⁻¹(1−α/K), where K is the number of candidates. Below the
   gate the answer is "none of these". D, K and α are recorded on the trace.
2. **Split conformal prediction** over the calibration set (§ 4.3). The prediction set at level α
   decides: size 1 → admit, size 0 → "none of these", size ≥ 2 → ask (Jev, then the owner, with
   the set as the candidate list).
3. **Cold start is handled by the arithmetic, not by a constant.** Split conformal is valid only
   for α ≥ 1/(n+1). Until the calibration set is large enough for the declared α, the check admits
   nothing on its own and everything goes to the owner. Per-class sets need about ⌈1/α⌉−1 points
   per class, otherwise pool at the gUFO parent.
4. **α is a declared risk tolerance, set by the owner per question**, recorded in the family
   model. It is the cost of a wrong admission stated as a rate. It is not fitted to make a score
   pass, which is what keeps it out of G4's "tuned constant" class. A starting value is open
   (§ 11 O2).
5. Quantiles are recomputed after each owner batch.

**Model proposals (Jev, Haiku) — decision 12.** A model's pick is admitted on its own only when:

- it is **inside the candidate set** the check produced (for Haiku on a size-0 set, there is no
  set, so Haiku's pick always goes to the owner); and
- that model's **measured error rate** on owner-validated answers for this question is at most
  α, with the same cold-start arithmetic as item 3 (too few validated answers → ask).

Otherwise the owner is asked. A model's self-reported confidence is never used: it is not
calibrated and not owned. Each owner answer extends both the HDC calibration set and the model's
error record.

### 4.6 The trace

- **What it is.** The decision holon's own RDF: question, answer, evidence, decider,
  `PromotionDecision` (where admitted), check figures, and a link to the clause by
  provenance-to-the-page (iladub § 6).
- **What the human reads.** Plain prose generated from that RDF, one template per question, so
  prose and graph cannot drift apart. The shape the owner approved:

  > **Clause 12 of GAFTA No. 49 — typed as *Default*.**
  > **Question:** what kind of clause is this? **Answer:** Default.
  > **Why:** its wording is closest to the clauses you confirmed as Default before ("fails to
  > fulfil", "the defaulter", "damages"). The next closest type, *Arbitration*, was well behind.
  > **Decided by:** the clause matcher, admitted automatically at the 5% error rate you set.
  > **Source:** page 3, clause 12 → (link to the clause text)

  Similarity numbers, the examples compared against, and their admission history sit behind it,
  available but not in the main text.
- **Every decider must explain itself in domain words.** An exact rule names the label it
  matched. HDC names its top contributing n-grams (lexical scores split linearly per n-gram,
  research § D). Jev and Haiku name the span they read. Geometry, where used, is phrased as
  evidence ("indented under clause 11"), never as a concept.
- **Nothing in iladub renders a decision holon as prose today.** `dec:rationale` is written as a
  bare literal (`src/iladub/decision.py:85-108`, `etkl/decisionlog.py:39`) and read by nobody.
  The renderer is new.

### 4.7 Recognising a contract (Q-family)

iladub routes documents by the caller's choice of function today: `readers.read_document` picks a
reader by suffix (`src/iladub/readers.py:16-28`), and nothing classifies document type. For
contract:02, **the family is declared by the caller** (`--family gafta`) — my call, kept small. An
HDC "which family?" decider over the family models' prototypes is the natural later step, and it
enters as one more named question.

### 4.8 HDC in iladub: a native domain (decisions 5, 17)

`iladub.hdc` is designed and written in iladub, on `torchhd`, as its own domain. Its operations
are the ones this design needs and the research names (§ A): records as Σ bind(role, value) with
unbind-and-clean-up, permutation for order and depth, prototypes rebuilt from durable examples,
per-n-gram attribution for traces, and similarity as the only output. **Admission is never
inside `iladub.hdc`**: it returns similarities, and the calibrated check (§ 4.5) decides. Its
inputs are iladub's own types (the concept scheme read from RDF, the `ctr:Clause` graph), not
hdc-contract's.

**hdc-contract's `src/hdcc/hdc/` is prior art only** (read 2026-10-30: 501 lines; torch,
`torch-hd==5.8.4`, msgspec, numpy). It is a cautionary one as well: its `text.py` carries
`MIN_MARGIN = 0.02`, `MAP_THRESHOLD = 0.75` and `MAX_WINDOW = 4`, and `eval/hdc_sweep.py` sweeps
D. Those are the tuned-constant class G4 forbids, and nothing in `iladub.hdc` reproduces them.

**A dedicated skill comes first** (decision 17). HDC is new to this repo, so before `iladub.hdc`
is planned, a skill is written (superpowers:writing-skills, with its RED/GREEN evidence) that
fixes how HDC is done here: `torchhd` idioms and its pinned version, the VSA model choice, how D
is chosen and recorded, capacity limits, the "similarities out, admission elsewhere" rule, trace
attribution, and the traps the research names (bundling capacity, crosstalk, no meaning from a
random codebook). The skill's content is its own design. This design only requires that it exist
before the HDC plan.

**Torch is a heavy dependency** for iladub's install. Whether `iladub.hdc` is an optional extra
(`pip install iladub[hdc]`) is the plan's call. Making it optional is my lean.

### 4.9 Encoding

**Text (Q-type):** the research § D recommendation, adopted as the starting encoder:

- character 3–4-grams;
- word bigrams with order permuted;
- an explicit negation/modal feature (`bind(NEG, verb)` for "shall not", "unless", "except").

A projected embedding channel enters **only** if the § D A/B passes its pre-registered rule
(adopt the embedding only when it wins by at least 3 macro-F1 points on held-out whole forms).
That 3-point margin is a pre-declared decision rule, not a fitted constant. If adopted, the
embedding is scored separately, so traces stay lexical (§ 4.6).

**Layout:** not needed for contract:02's questions (Q-start stays typographic). Research § E's
data-derived kernel density estimate is the tables phase's (§ 9).

## 5. The classification gate (CLAUDE.md § 8)

This design stays inside § 8 as written. **No CLAUDE.md edit is required by it**, though the owner
may want decision 1 recorded there (§ 11 O3).

| decider | § 8 class | its oracle |
| --- | --- | --- |
| exact rule (heading = label; typographic start) | AXIOM / PROCEDURAL raw extraction, as in contract:01 § 5 | SHACL membrane |
| HDC prototype match | **NEURAL-class proposer, owned and deterministic**: it answers a reading judgement ("what kind of clause is this?") by similarity, not by axiom | the calibrated check (set size 1) **and** the SHACL membrane |
| Jev, Haiku | NEURAL (GenAI via BAML, proposing) | the calibrated check, else the owner, then the membrane |
| conformal quantile, noise gate | PROCEDURAL, decidable exact arithmetic | — |
| written-back rule | becomes AXIOM (a label, a declared pattern) or an HDC example, by its `PromotionDecision` | the membrane, on every later compile |

"No oracle, no worker" holds: every proposer has the calibrated check and the membrane behind it.
Decision 8 is § 8's "one attempt, then NEURAL" turned into a loop: NEURAL answers a gap once, and
its admitted answer becomes AXIOM or owned HDC memory.

**Classing HDC as NEURAL-class is my reading** and the one a reviewer is most likely to dispute.
The alternative reading is "AXIOM over an evidence graph", which does not fit, because similarity
is not entailment (research § B). Treating HDC as a proposer keeps it under § 3's epistemics.

## 6. Constraints

- **No tuned constant** in the decision path (G4). α, D and K are recorded. Bandwidths, when they
  arrive, are computed from data. The § 4.9 3-point A/B margin is declared before the A/B runs.
- **D (HDC dimension)** is chosen from published capacity figures (research § A: exact recovery
  100% at D=8192 for 50 facts) and recorded. It must not be swept to fit a score.
- **Source ownership** (CLAUDE.md): `gco:` is consumed, never edited. Written-back labels go into
  the family model, not into `gco-concepts.ttl`. A label that belongs in the scheme is recorded
  as a proposal for hdc-contract, to raise when its pause ends. While it is paused, a disagreement
  such as 48 cl.7 (contract-rung spec Q6) is disposed by a dated adjudication or by the trader,
  not by a scheme edit.
- **GAFTA text is never committed** (contract-rung spec § 6.6). Family-model examples store a
  reference (form, clause number, sha of the pinned PDF) **and** the n-gram vector or features, not
  the clause text. Whether the encoded vector counts as redistribution is part of § 11 O4. **Until
  O4 is answered, the plan assumes the worst case** — my call: the committed family model holds
  references only, the GAFTA examples are rebuilt locally from the fetched PDFs, and CI runs on a
  synthetic family (`examples/contract/`), as contract:01's corpus tests already do.
- **The producer-side guard rule** (CLAUDE.md, R89) applies to the write-back: the write-back
  refuses a rule without a `PromotionDecision` at the call site, even though a membrane shape
  also checks it.
- **Every vocabulary or shape ships a conforming example and a failing negative test**, as
  always.

## 7. contract:02 (sketch; the plan fixes the wording)

> "On the GAFTA corpus (tests/contract-corpus-manifest.ttl), a first compile pass answers every Q-type
> gap through the gap path and writes each admitted answer back into the GAFTA family model; a
> second pass over the same corpus makes **zero** model calls; every decision in both passes
> carries a trace that renders; and on held-out SME answers the calibrated check's admission error
> rate is at most the declared α."

Oracle tests (names fixed by the plan):

1. `test_second_pass_makes_no_model_call`: pass 2 with the BAML client entry points patched to
   raise. This is decision 8's direct falsifier.
2. `test_every_writeback_has_a_promotion_decision`: SHACL over the family model.
3. `test_trace_renders_for_every_decision`: each decision holon renders through its template, and
   the rendered text names the decider and the clause.
4. `test_admission_error_within_alpha`: held-out split of owner-validated answers. **This needs an
   owner-labelled set that does not yet exist** (§ 10).
5. `test_no_model_call_on_covered_pdf`: a hero form with a mature model compiles with models
   patched to raise (G1).
6. `test_heldout_forms_need_fewer_gap_calls`: write back from a training split of whole forms,
   then compile the held-out forms and compare their gap-path calls to a cold-start compile of
   the same forms. Test 1 alone passes by memorisation (each clause meets its own example), so
   this is the test that shows learning generalises — my call.

A first pass that calls the owner on every gap is expected (cold start, § 4.5 item 3). **Owner
answers given in pass 1 are recorded and replayable**, so later runs (and test 4's held-out split)
reuse them rather than asking again — my call.

## 8. What is left to the builder

- The exact JSON-LD shape of the family model and its `@context`, within § 4.3.
- How a written-back Q-start rule is represented (declared pattern, regex in the model, or HDC
  example), within § 5's classes.
- The package layout of `iladub.hdc` and whether torch is an optional extra.
- The trace template language, provided prose is generated from the RDF and never stored as the
  only record.
- The BAML function for the Haiku gap call, and its typed, closed return shape (CLAUDE.md § 8:
  "never returns a value that is on the page").
- How the owner is asked (CLI prompt, a queue file, a DataBook of open questions).

Settled as my calls, for the builder to follow:

- **Both the Jev and the Haiku BAML functions live in iladub's `baml_src`.** iladub gains a
  `typesafeai` client and its key (`TYPESAFE_API_KEY`). The Haiku stand-in is the newest Haiku
  hdc-contract already uses (`claude-haiku-5-5`), not iladub's current `claude-haiku-4-5-20251001`
  client. Tests 1 and 5 patch both clients.

## 9. What carries over to etkl tables

The tables phase is its own design, after a fresh drift scan (the line numbers in the hdc-contract
handoff § 2 are not to be trusted by then). This design hands it:

- **Named questions in domain vocabulary.** "Which rows are headers", "which column is a total",
  "is this a suppressed repeat": these replace band, gutter, flank and donor-band names in
  traces. `tab.ttl` and `tab-datagrid.ttl` already have most of the domain classes
  (HierarchicalTable, HeaderNode, AggregationRow/Column, SuppressedRepeat, RepeatedHeader).
- **The decider ladder and the gap-to-owned-rule loop**, unchanged.
- **The calibrated check** in place of tuned thresholds.
- **Data-derived layout encoding** (research § E) in place of `bands.py:60` (`gap_factor 1.8`),
  `grid.py:129` and `headers.py:268/287/387`, adopted only once it reproduces today's segmentation
  on the corpus.
- **The trace renderer.**
- **What does not carry over:** the GAFTA family model. Tables need their own notion of a family
  (publisher, report series), and that is the tables design's question.

## 10. Risks

- **The calibration set does not exist.** Of the 49 hero rows, 42 are `needs_trader_check: true`
  (contract-rung spec M-p). The check starts by admitting nothing, and contract:02's test 4 needs
  owner labels first. Cold start is safe, because it means asking, not guessing. But it is slow.
- **Lexical HDC on GAFTA headings is circular.** The `gco` altLabels were written from these
  forms (contract-rung spec M-j). The A/B must hold out whole forms.
- **Haiku is a vendor dependency.** Decision 6 accepts it. Decision 8 bounds it: its calls should
  trend to zero.
- **Jev is a second vendor** (`typesafeai`). It is used only on candidate sets, and the ladder
  works without it (owner instead), so a Jev outage degrades to more owner questions.
- **Decision 13 raises pass-1 volume.** Up to 220 untyped clauses on the admitted forms enter the
  gap path, and under cold start most reach the owner. Recording and replaying owner answers
  (§ 7) means each is asked once.
- **HDC classed as NEURAL-class** may be disputed (§ 5).
- **Write-back can overfit.** A rule admitted from one form can be wrong on another. Per-form
  scoping (§ 4.3) and the membrane on every later compile are the guard. A rule the membrane
  refuses later is withdrawn by a superseding `PromotionDecision`.

## 11. Open questions for the owner

- ~~O1. Where does the GAFTA family model live?~~ Answered: iladub (decision 15).
- **O2. The starting α** for Q-type.
- **O3. Record decision 1 in CLAUDE.md?** CLAUDE.md is edited only on explicit request. § 5
  argues no edit is required.
- **O4. GAFTA licence**, including whether stored n-gram vectors of clause text count as
  redistribution (the contract-rung spec's Q5, widened).

## 12. Unverified or assumed

- The research recipes (§ C calibration, § D encoding, § E layout) are agents' inference, not
  measured on our data.
- The hdc-contract measurements in § 4.2 and § 4.8 were read from its working tree on 2026-10-30,
  not at a pinned sha. The plan pins one.
- Jev's second function (`RouteQuestionJev`) has an unverified schema. This design uses only
  "typed choice over a candidate set", which may need a new BAML function.
- iladub's BAML `Claude` client is `claude-haiku-4-5-20251001` (`baml_src/clients.baml:1-4`).
  hdc-contract uses newer models. Which Haiku version stands in is not decided.
- "Per family with per-form refinement" (§ 4.3) is not measured against how often forms disagree.
