# Handoff — reconsider the architecture: deterministic reasoning pieces, Jev decides between them (2026-09-27)

**Serves:** maintenance — carries the maintainer's architecture challenge to a fresh brainstorming session; it meets no criterion

**Topic:** jev-reading · **Date:** 2026-09-27 · **Branch:** `extent-oracle-evidence` (PR #277)

**Doc impact: none.**

Authored at ~67,000 working tokens, **over** the 50K originating floor. Part 5 is written first and
graded per action. Parts 1–4 are pointers.

## 5. Next action

**Proposed, open to refutation:** open a fresh brainstorming session on the maintainer's challenge
(§ 3 item 3) as an *architectural* redesign of how etkl reads a page. Before presenting any approach,
settle the **one question the challenge leaves open**: when Jev *decides* between reasoning pieces,
what refuses a wrong decision? The standing ruling is *Jev proposes, an exact oracle disposes; no
oracle, no worker*. "Jev decides" either keeps that (the pieces are the candidate options and an oracle
still disposes) or replaces it (Jev's choice is admitted on its own), and the second contradicts
CLAUDE.md § 8 and needs an explicit maintainer ruling. **Refutation cost: minutes.** Ask it first.

**Asserted:** before brainstorming, read the lead-1/lead-2 measurement if it landed (§ 4). If nothing
is appended there, it did not land. Its brief is in this session's transcript only, so re-run it from
§ 2's description.

## 1. Goal

Decide whether etkl's reading architecture becomes *deterministic functions compute layout and text
evidence; Jev decides between the candidate readings those pieces support*, replacing the current
heavy deterministic geometry path, and settle how such decisions are disposed.

## 2. Where the primaries are

- **The two refuted extent-oracle probes:** `2026-09-27-extent-boxhead-count-oracle-evidence.md` and
  `2026-09-27-extent-existing-oracles-evidence.md` (PR #277). Table extent has no oracle today, and
  every existing oracle is self-referential.
- **The pending third probe (lead 1 + lead 2):**
  - Lead 1: agreement between the band reader and the page datagrid, as an extent oracle.
  - Lead 2: evidence the author drew (captions such as bfs "T1"/"T2", drawn rules, side-by-side
    separation).
  - Architecture question put to both: *can the signal dispose an arbitrary PROPOSED extent (e.g.
    Jev's), or only critique the derivation's own output?*
  - Scratch output is `…/scratchpad3/` and is non-durable.
- **The approved design, sections 1–3:** `2026-09-27-question-compiler-design-handoff.md` § 3
  (merged in #275).
- **What refuted spatial text as Jev's input:** `2026-09-27-jev-spatial-text-and-geometry-refusal-evidence.md`
  (Probe A/B).
- **Jev's measured behaviour:** `2026-09-27-jev-reading-architecture-handoff.md` § 2a. It is
  text-only, gives no abstain unless offered, and is bad at arithmetic.
- **The ruling this challenge touches:** CLAUDE.md § 8, "One geometric attempt, then NEURAL", and
  `docs/superpowers/2026-09-17-neural-workers-handoff.md`.

## 3. What was decided, and where

1. **Section 4's table-extent slice has no oracle.** Two probes refuted it (PR #277, recorded).
2. The maintainer asked for leads 1 and 2 to be measured together before choosing. That instruction
   is recorded nowhere but this file.
3. **The maintainer's challenge, 2026-09-27, recorded nowhere but this file**, in their words:
   *"we overweight the deterministic path with very convoluted steps to understand documents. now the
   paradigm with jev is different … we are asking jev to decide, so the reasoning stays deterministic
   and decision between reasoning pieces provided by jev at light speed. … can't we build functions
   that understand text geospatial features and layout, just from text, and let jev decide on the
   output."* Also: *"I am afraid we will get stuck in pure llm only flavors when in need."* Not yet
   ruled. It reopens design sections 1–3 only insofar as the brainstorm finds they conflict.

## 4. Unverified or assumed

- **Probe A/B does not refute the challenge; it constrains it.** Probe A/B refuted *layout-preserving
  spatial text* as Jev's input: the alignment-destroyed control matched or beat it. The challenge
  proposes something different: **computed evidence statements** from deterministic functions (e.g.
  "line 25 begins with caption 'T2'", "lines 25–32 have no run under column 3 of the grid above").
  Whether Jev decides better from computed evidence than from raw text is **unmeasured**, and it is
  the cheapest decisive probe for the new architecture.
- Whether the lead-1/lead-2 signals can dispose a proposed extent is pending (§ 2).
- All earlier Jev figures rest on 5 pages, one run per condition.

The lead-1/lead-2 result, if it lands, is appended below this line.

**LANDED** (see `2026-09-27-extent-two-leads-evidence.md`):
- **Lead 1 (reader agreement) is REFUTED as an oracle.** It refuses the correct side-by-side cbh answer, and any cut-off above 0 is a tuned constant.
- **Lead 2 (marks the author drew: captions, ruled boxes, empty gutters) CAN dispose a proposal that carries its x-range.** It covers both cbh and bfs p5 exactly. It abstains on ons p4, where the page has no marks, and apple's interior rules make it a false positive there.
- **For the brainstorm:** the answer must be word- and x-grained, because cbh line L75 holds three objects, so a line-range proposal from Jev cannot be right. The author's marks are exactly the kind of "deterministic reasoning piece" the maintainer's challenge describes, and an oracle besides.

**ANSWERED — first question, 2026-09-27:** the maintainer chose to **test arm A first** (Jev picks,
an exact oracle still disposes). **Spike LANDED** (see `2026-09-27-jev-picks-oracle-disposes-spike-evidence.md`):
- Under computed evidence (E), there were **0 admissions ≠ ground truth in 60 table-runs**. Computed
  evidence beats raw text on held-out pages: 13/24 exact against 5/24.
- The author's box defines what an extent is (titles, footers or sources inside, totals outside,
  varying by author). Whether an extent = the author's box with Jev's roles carried inside it is
  **not ruled**.
