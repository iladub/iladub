# Handoff — Jev and a typed-only decision architecture for etkl (2026-09-27)

**Serves:** maintenance — the brainstorm that decides how etkl's reading decisions are re-architected around TypeSafe's Jev; it meets no criterion itself. The unmet ones it bears on are `etkl:03` (cbh) and `etkl:05` (bfs).

Written at ~53,000 working tokens (just over the 50K originating floor) and completed at ~65,000, 1.3x the floor. **Part 5 was written first**, before the Jev measurements landed. Parts 1-4 are pointers and records.

## 5. Next action — PROPOSED, may be refuted

**Run the brainstorm (superpowers:brainstorming, architectural path) for "Jev as etkl's reading worker", starting at *propose 2-3 approaches*.** The maintainer's intent is already captured (§ 3), so don't ask for it again.

The proposition the brainstorm should test first, in minutes, before designing on it:

> *Jev can answer an etkl reading question the host code can already state as a closed option set, from a textual/structural `state`, at a cost low enough that a whole document's questions cost less than one `ReadBoxhead` call today.*

It fails if Jev needs the page image (the two live workers read images; see § 4), or if a realistic `state`, meaning a band's word listing, exceeds Jev's input limit. If it fails, the architecture is "Jev for structural and grounding decisions, vision stays on BAML/Sonnet", and the brainstorm should say so rather than force Jev onto vision.

**Update after § 2a landed (same session).** Two of the conditions above are now answered by measurement: **Jev is text-only** (no media; so it does not replace `ReadBoxhead`/`ReadEmptyCells` as-is), and **cost and size are not the constraint** (≈$0.04/M input tokens, ~0.3 s, a 21k-token state works). **The proposition still open is accuracy:** on a real etkl question (a band's word listing as `state`, a host-derived closed option set **with an explicit abstain option**), does Jev's pick agree with what the oracle accepts, and with the recorded Sonnet boxhead readings in `readings/boxhead/`? One corpus page, a few dozen calls, minutes. If it disagrees, find out why before designing on it.

Shape to bring into the approaches (a proposition, not a design): **the host code derives the option set** (AXIOM: SPARQL over the evidence graph, which already exists as `_deliberate` → `dec:optionSpace`), **Jev returns one probability per option and no strings**, **the existing oracle accepts or rejects the answer** ("legality gates admission, never confidence"), and **the rationale becomes the derivation's IRI plus its evidence nodes, never model prose**. This closes the one place model prose enters the graph today (`dec:rationale`, § 4).

## 1. Goal

Decide, with the maintainer, how etkl turns human-addressed text into rich document holons using Jev (typed answers only) as the NEURAL worker, so that more reading decisions can be AI-proposed at far lower cost, while every decision stays deterministic in its reasoning and explainable without model prose.

## 2. Where the primaries are

- **Jev access**: `internal/2026-09-27-jev-access-and-kisal-family-handoff.md` § 2 (endpoint, credentials in Keychain, billing via AI Gateway credits). Confidential, untracked.
- **Jev measurements from this session**: § 2a below. Raw requests and responses live in the session scratchpad, which does not persist, so re-run anything load-bearing.
- **The ruling Jev must satisfy**: CLAUDE.md § 8, *"One geometric attempt, then NEURAL"* (a worker returns a strongly typed, closed shape; no oracle, no worker), and `docs/superpowers/2026-09-17-neural-workers-handoff.md`.
- **Today's seams** (inventory measured this session; re-open the files, not this summary):
  - BAML functions and output types: `baml_src/*.baml`. Clients: `baml_src/clients.baml` (Haiku 4.5; Sonnet 5 for the long vision answers).
  - Where proposals are recorded: `src/iladub/etkl/promote.py:34-203`, `src/iladub/ground.py:230-308`, `src/iladub/splitkey.py:174-306`.
  - Live workers in production compile: `ReadBoxhead` (`etkl/boxhead.py:110`, reached from `compile.py:1608`) and `ReadEmptyCells` (`etkl/unshownink.py:151`, via `compile.py:490-498`, gated on `BAML_LIVE`).
  - Oracles: `etkl/tiling.py` (`region_tiles`, SHACL), `ground.py:285-308` (`_grounds_to`), `etkl/oracle.py` (`round_trip`), `boxhead.py:150` (`dispose_boxhead`), `unshownink.py:185`.
  - Exemplars catalog: `docs/wiki/concepts/neurosymbolic-exemplars.md`.
- **Benchmark**: etkl 5/7 (`tests/arc-manifest.ttl:188-312`, commit `e6ed4fe`). cbh (`etkl:03`) and bfs (`etkl:05`) are unmet.
- **The kisal family** (for placement only): `kisal/docs/specs/2026-09-20-holon-engine-design.md` D18 (vocabulary: HGA ← iladub ← kisal; code: iladub will call kisal) and D19 (kisal = interaction engine; kisurra = + space; Quarter15 = product).

## 3. What was decided, and where

- **Scope for this repo** (maintainer, 2026-09-27, in session; recorded **nowhere but this file**): *"in this repo we will focus on jev to produce semantically rich holons from flat text; we decided recently to simplify the etkl module by allowing more ai based decisions; jev will allow us to really rearchitecture etkl since the AI costs will shrink."* Also: Jev output is types and decisions, no strings, no reasoning, so the reasoning must be defined and deterministic, with Jev validating it.
- **iladub keeps the decision epistemics; kisal runs the holons once they exist.** Measured this session against the kisal records: kisal owns no decision, promotion, escalation, risk or AI concept, and deliberately stops a kisal event from being a `dec:DecisionHolon` (`kisal-contract/vocab/kisal-iladub-align.ttl:44-47`). Nothing in iladub is superseded; migrating iladub onto kisal is out of scope there (spec :48-49). Recorded in the kisal specs, not in this repo.
- **kisal-contract re-pinned iladub to `6d6631f`** (kisal-contract `14da440`, pushed): vocabulary byte-identical, `cargo test` green.

## 4. Unverified or assumed

- **Whether Jev reads images — ANSWERED in § 2a: it does not (text/JSON only).** So as-is it cannot replace `ReadBoxhead` or `ReadEmptyCells`, the only two workers that production compile actually calls.
- **"AI costs will shrink" rests on the premise that current AI cost is the binding constraint.** Measured: five of the seven `Propose*` seams are never constructed from `src/`, only in tests. Across the 7 corpus documents the span and row-role seams are reached 0 times, and grounding is asked 39 distinct questions (`docs/superpowers/2026-09-17-neural-worker-seams-evidence.md`, per the inventory). So the saving is mostly on seams not yet wired. The real gain may be that *more* questions become affordable, which is a design claim to argue, not a measurement.
- **Model prose enters the graph today**: `dec:rationale` carries the LLM's sentence (`promote.py:85-87`, `ground.py:237`, `splitkey.py:271`). Nothing requires it and no test pins it. Removing it is compatible with Jev, but it is a change to what a decision holon records.
- **Open string outputs**: `HeaderRowRoleProposal.roles` is `string[]`, checked host-side against `ROLES`. `ProposeHeaderSpan` is called (`propose.py:88`) but defined in no `.baml` file.
- **Calibration**: nothing in the repo measures whether any worker's confidence is calibrated. Jev returns probabilities; whether they are calibrated on etkl's questions is unmeasured.
- **Model id is not recorded** on a proposal. Only the suggester IRI is (`propose.py:158`).
- Everything in § 2a is from a small number of live calls and vendor documentation. One call is not a benchmark.

## 2a. Jev and BAML measurements (this session)

A measurement agent made 19 live calls through Cloudflare on 2026-09-27: 14 returned 200 and 5 were deliberate limit probes. **The raw requests and responses, the vendor docs snapshot (`docs/llms-full.txt`, the whole TypeSafe docs site) and the BAML sources are kept at `internal/benchmarks/jev-2026-09-27/`** (confidential, untracked; checked for credentials: none). Each fact below cites its call file. Re-open the file before relying on any fact.

- **Input** (`calls/10-18`, `docs/cf_schema_input.json`):
  - `state` is text, JSON or null. **No media.**
  - Question types are `noul` (a yes/no probability, *not* null handling), `choice` (≤255 options) and `score` (2–10 levels).
  - The budget is 64k tokens per request; state plus the longest question may take 32k.
  - 300 questions in one call worked.
  - Cloudflare rejects `temperature`, `seed` and `model`. **The model version cannot be pinned on Cloudflare.** TypeSafe's own `/v1/systemone` accepts `model: jev-1.13.0`.
- **Output:**
  - Per answer, the pick plus `probabilities` and `confidence`, rounded to 2 decimals. The schema is closed, with **no text of any kind**. The response names the model version (`jev-1.13.0`).
  - Confidence is derived from the probabilities (vendor formula) and adds nothing new.
- **Not deterministic:** ±0.01–0.02 on identical calls. In 6 repeats no label flipped (`calls/01-03`, `07/15/16`). The vendor rejects determinism as a goal, so recording and replaying answers is required, as `readings/boxhead/` already does.
- **No abstention by default** (`calls/04`, `19`): with the true option missing, Jev picks a wrong one at confidence 0.92–0.99. With an explicit abstain option it picks that option (0.99–1.0). **Low confidence is not an "I don't know" signal.**
- **Where it is strong** (`calls/05`, `08`, `09`): header and row lookup in a plain-text table; mapping values under a spanning header; reading Turtle (types, `skos:broader`); grounding a label to a concept *and* refusing when no concept fits; checking an extracted fact against its source sentence; logical validity.
- **Where it is weak** (`calls/06`, `07`, `12`):
  - Arithmetic: it could not tell a wrong total from a correct one (0.67 vs 0.62), and said "the total equals the sum" at 0.97 when it did not, systematically.
  - Literal reading: "mentions 4" scored 0.70 on "42 EUR".
  - Both are on the vendor's own list of known weaknesses, `docs/` → `model-jaggedness/jev-1.13.md`. **Arithmetic stays PROCEDURAL** (CLAUDE.md § 8 already says so).
- **Cost and latency:** median 0.335 s round trip. $0.042 per million input tokens; output is free. The whole probe cost about $0.0014.
- **BAML:**
  - Native Jev support is in `baml-language-0.20.1` (and nightly `…20260918.b`), and **only in BAML v1 syntax**. iladub pins `baml-py==0.222.0` (v0), which has no TypeSafe provider.
  - BAML maps `bool`/`float` to noul, enum or literal union to choice, and `T?` to a `"<null>"` option (a built-in abstain). A class is one question per field. `score`, arrays, strings and media are unsupported.
  - **Probabilities are not in the typed result**, only reachable through an HTTP-response hook.
  - BAML routes to TypeSafe's own API, not Cloudflare.
  - So BAML-for-Jev means a v0→v1 migration *and* TypeSafe early access. A thin direct HTTP client to Cloudflare keeps the probabilities and needs neither. Which one to use is a brainstorm decision.
- **Independent evidence:** none on calibration. The vendor declines public benchmarks. Third-party pieces restate vendor figures or report one customer trial.
