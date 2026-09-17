# Handoff — the ink the page does not show: the spec exists, attack it

**Serves:** prog:criterion:etkl:02 — graincorp-capacity. [[R250]] is blocked on [[R213]].

**Date:** 2026-09-17. **Doc impact: none.**

Written with part 5 first, per CLAUDE.md § "The handoff's next action is TYPED". **plimslop reports
no measured turn for this project this session** (`preflight` → *"unmeasured — no turn recorded"*),
so the usual working-token figure is absent rather than withheld; the spec was written in the
session's first third, after the measurements and before anything else.

## 5. The next concrete action

### 5a. ASSERTED — adversarially review the spec, in a fresh session, before any plan

`docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md` (PR #262). §§ 1–3 are
measured and cite `2026-09-17-unshown-ink-evidence.md` command by command. **§§ 4–6 are PROPOSED
and have never been run.** The repo's practice (and the `neural-worker-foundation` precedent, which
was reviewed and lost its § 1d.1 to [[R249]]) is to attack a spec's premises before planning
against it. The spec's own § 7 lists the four weakest parts; a reviewer should not be limited to
them.

### 5b. ASSERTED — O1 is the run that can kill § 4, and it is cheap

The spec's § 5 orders the oracles and puts **O1 on cbh-stem first, not gcap**. cbh's 780
white-on-pale-blue glyphs are the port codes `ALB`/`ESP`/`GER`/`KWI` beside their tonnages — low
contrast, plainly legible, load-bearing data (**E7**, rendered and read). If a vision worker calls
them unshown, `tab:UnshownInk` over-fires on a document the term was never about and § 4's disposal
is refuted. **Run it before building anything**, and before gcap, where the spec is expected to
succeed and will teach nothing.

### 5c. ASSERTED — the term and the fork are decided, and do not need re-deciding

`tab:UnshownInk`, a `tab:CellDatatype` that abstains, with `tab:unshownText` carrying the suppressed
transcription and `tab:gridText` empty. The ruling's open fork is resolved as **a datatype, not a
proposition**, argued in § 2.2. The naming decision (not `HiddenInk`, not `InvisibleInk`) is § 2.3's
last bullet. Re-open any of these only with an argument the spec does not already answer.

### 5d. PROPOSED — the plan's first measurement, and how it could go wrong

The spec deliberately does not state the region count or whether a rendered region crop is legible
to a worker (§ 7.2) — plan rule 3 sends both to the call site. **The proposition is that one ask per
region is affordable and that a crop is readable.** It fails if regions are large multi-page
constructs whose crops are illegible at any sane resolution, or if the corpus's region count is far
higher than the ~30 this session assumed without measuring. Measure both before writing the worker's
signature; if either fails, the ask's grain is the thing to redesign, not the term.

### 5e. ASSERTED — what must NOT be done

- **Do not carry a colour into `src/`.** § 1.1 is the measured reason and § 3.2 makes it a gate.
  `extra_attrs=['non_stroking_color']` is specifically forbidden: it splits words on 4 of 27 corpus
  pages (**E4**).
- **Do not ship a threshold**, including a cited one. WCAG 2.2's published 3:1 was the best
  available and fires on 858 visible glyphs (**E2**).
- **Do not promote E7's `Y`/`N` witness into the disposal.** It is contract knowledge about one
  table's shape — *hidden ⟹ N* holds 110/110, *N ⟹ hidden* is false (5 counter-instances), and no
  other corpus document has a flag column. It checks O2; it is not the rule.
- **Do not build [[R250]]'s derivation** (blocked on R213) and do not re-litigate R213 option (c).

## 1. Where the primaries are

- Spec: `docs/superpowers/specs/2026-09-17-the-ink-the-page-does-not-show-design.md`.
- Evidence, E1–E7, every command and its output:
  `docs/superpowers/2026-09-17-unshown-ink-evidence.md`.
- Instrument (measurement only; no `src/` module imports it): `scripts/ink_contrast_probe.py` —
  three modes, `--gap`, `--palette`, and the default WCAG census.
- The rows: `residues-open.md` [[R213]] (amended, still open) and [[R251]] (new).
- The predecessor handoff, two of whose premises this loop refutes:
  `docs/superpowers/2026-09-17-r213-term-handoff.md`.
- The seams the spec builds on: `regions.Cell` (`regions.py:34-41`), `headers._grid_cells`
  (`headers.py:66-81`), `celltype.grid_evidence` (`celltype.py:138-150`), the lattice
  (`vocab/ontology/tab.ttl:259-303`).

## 2. What was decided, and where it is recorded

- **The fork: a datatype, not a proposition** — spec § 2.2. Recorded nowhere else; it is this spec's
  decision and reversible by a better argument.
- **No colour in `src/`, and § 5c of the predecessor handoff retired** — spec § 1.2, on E2/E4.
- **The disposal is a disagreement between the text layer and a NEURAL reader of the render** —
  spec § 4. Proposed, never run.
- **[[R213]] amended, not closed** — the register row carries both refutations and says explicitly
  that nothing is implemented.
- **[[R251]] raised** — two implementations of R213's own instrument disagree by 25% on their
  population (30,404 vs 25,925 on-rect chars; band 0.1935 vs 0.42174), while the 110-cell set
  identity reproduces exactly.

## 3. Unverified or assumed

- **§ 4 has never been run.** No vision worker exists; `baml_src/` holds five text functions and no
  image input.
- **E7's renders were read by this session, not by the maintainer.** R213's own rendering check
  agrees, and is the maintainer's.
- **Region count and crop legibility** — unmeasured, deliberately (5d).
- **The cost of rendering pages** — unmeasured.
- **The trichotomy may not be a trichotomy** — a fourth case (ink the page shows but places outside
  any cell) is not addressed and is not known to be empty (spec § 7.4).
- **O3's bit-identical prediction on the other six documents is a real prediction** — the worker
  would run on all seven, so it can fail.

## 4. What this session did

Measured before writing: replicated R213's luminance band independently (E1), refuted its
cited-standard variant on 858 visible glyphs across two documents (E2), refuted three threshold-free
palette rules (E3), measured that the prescribed extraction route moves the reading on 4 of 27 pages
(E4), located the one seam a per-cell fact must cross (E5), and rendered both contested populations
and looked at them (E7). Then wrote the spec, amended R213, raised R251, and shipped the instrument.
PR #262.
