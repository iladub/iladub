# Handoff — repairing the context-budget regime

**Topic:** the context-budget regime — CLAUDE.md describes a hook deleted eleven days ago, the status
line renders the unit that hook's replacement was built to reject, and the originating floor has been
eaten by the session baseline. This file carries the pointers; the audit carries the numbers.

**Date:** 2026-08-26 · **Branch:** `main` at `a5fa232` · **Shape: pointers only.**

**Why this exists and what it is NOT:** it was written at ~232k tokens, **4.6× the 50k originating
floor** — which is itself an instance of the problem it describes. Choosing a remedy is originating
work, so it was not done here. **Nothing below is a decision.**

## Goal

One line: **decide and apply the repair to iladub's context-budget regime — starting with the three
contradictions that are live every turn — in a cleared session, in that session's first third.**

## Where the primaries are, and what to establish at each

| primary | what to establish there |
|---|---|
| `docs/superpowers/2026-08-26-context-regime-audit.md` | **The evidence. Read §0 first** — it states which measurements were verified directly and which were delegated and never re-run. §3 is the contradiction list; §4 is what the audit does *not* establish. |
| `CLAUDE.md` § Loop & context hygiene (`:275-293`) | The Contract text that must change. It mandates 40% of the window, names `scripts/context_budget.py` as *"wired as a UserPromptSubmit hook"*, and never mentions plimslop. **Contract class — edited only on explicit request.** |
| `.claude/settings.json` | 117 bytes, `statusLine` only, **no `hooks` key**. Establish this yourself before planning; it is the fact CLAUDE.md contradicts. |
| commit `2b33802` (2026-08-15) | The maintainer's own written resolution of the percentage/absolute question, in its commit message. It was never propagated to the Contract. **Cite it; do not re-derive it.** |
| `scripts/context_budget.py` | Orphaned but tracked, and still soft-imported by the status-line gauge. Establish whether anything else reads it before proposing deletion. |
| `~/.claude/skills/managing-context-budget/SKILL.md` + `/Volumes/WD Green/dev/git/plimslop` | The replacement's own account of itself. `HANDOFF.md` (**not** `BRIEF.md`) §4 lists its validation gaps in its own words. `TESTS.md § Scenario D` is the precedent for how a rule here gets refuted. |
| `~/.claude/plimslop/corpus.jsonl` | 672 records. The override rate (54%) and the baseline growth (15,658 → 46,243) are computed from here. **`reader.py` never reads `preflight` records** — that computation exists nowhere in code. |

## The findings, ranked by how live they are

**1. The floor is unsatisfiable (audit §2.3).** A fresh session starts at **92.5% of the 50K
originating floor**; 3 of 474 recorded turns have ever been under it; the override rate is **54%,
flat over three weeks**. This is the one that makes the other two matter — a gate nobody can satisfy
is a gate that teaches override as normal.

**2. The Contract is wrong in two ways (audit §2.1, §3).** It names a deleted hook, and it mandates
the percentage unit. Both were already resolved in `2b33802`'s message and never propagated.

**3. The status line contradicts the gate every turn (audit §2.2).** At the median session peak of
183,435 tokens the gauge reads **18%, blue, no warning**; the floor calls the same moment 3.7× over.

**Not a finding, and do not treat it as one:** *fragmentation caused harm.* Audit §2.6 and §4. The
correlation is clean and the causal claim has no evidence behind it. §0 is a point against it — 30
commits from ~13 fragmented sessions passed full CI first try.

## What was decided, and where each decision is recorded

- **Nothing about the remedy is decided.** No option was chosen, costed, or ruled out.
- **The audit's provenance split is recorded in the audit's own preamble and nowhere else** —
  §0 verified directly, §1 and §2 delegated and never re-run. **Therefore reversible, and the
  numbers are re-runnable: every command is recorded.**
- **The five artifact dates in audit §0 were verified in the commissioning session** and are the
  only measurements in this handoff's chain that had two pairs of eyes.
- **PR #123 merged** (`a5fa232`), closing the `holon:05` routing gap. Recorded in the PR and in git.
  **PR #125** carries the R135 spec. Neither bears on this handoff except as §0's evidence.

## Unverified or assumed

- **§1 and §2 of the audit were produced by delegated agents and NOT independently re-run.** This is
  the largest caveat in the chain. The commands are recorded so a fresh session can re-run any single
  number before planning against it — and it should, for anything load-bearing.
- **The 1.28× post-cutoff residue rate has no power calculation**, and 9 of its 94 attributed rows had
  their primary artifact assigned by judgement rather than citation. The agent notes all 9 land in the
  PRE bucket, so correcting them would strengthen its conclusion rather than weaken it — **that
  reasoning was not checked.**
- **The 54% override rate counts 19 logged `stop` decisions as compliance.** `preflight.py` validates
  `--shape` but not `--decision`, and `stop` is undocumented. So 54% is a **floor**, not a ceiling.
- **Whether 50K and 150K are the right numbers is unestablished by anyone**, including their author —
  `tiers.py` labels 150K `NO SOURCE`. A remedy that only moves the numbers is unfalsifiable unless it
  says what would show the new ones wrong.
- **No pre-plimslop token baseline exists or can ever exist.** The corpus starts 2026-08-15.
- **`.claude/settings.local.json` is gitignored** and was read in one session; it may differ per
  machine. Re-read it rather than trusting this file.
- **The status-line median (183,435) and the baseline series are single-source** (audit §2).

## The trap this work sets for itself

**Editing the guidance is originating work, so improving it crosses the floor in the act.** plimslop
records this happening *"evidenced three times"* — including its own reader, built at 272K tokens on
an explicit override after two earlier sessions refused the task. A fresh session should expect to hit
this and decide, in advance and in writing, what it will do about it — that decision is itself part of
the remedy, not an obstacle to it.

And the method to use is already in the tree: `TESTS.md § Scenario D` refuted two shipped rules by
**running a pressure battery against a control**, not by reasoning about them. Half of what shipped
there did not survive. **A remedy argued rather than measured is the failure mode this whole file
documents.**

## The next concrete action

**In a fresh session, open the audit (§0 first, then §3), re-run one load-bearing number from §2.3 —
the baseline and the override rate — and then rule on the unit question**: does iladub adopt absolute
floors, keep a percentage, or something else. That single ruling determines whether CLAUDE.md, the
status line, and the gauge are three fixes or one.

**Do not start with the CLAUDE.md edit.** It is Contract class, it requires explicit maintainer
request, and it is downstream of the ruling — writing it first would encode a decision nobody has
taken.
