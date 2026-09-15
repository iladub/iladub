# Evidence — the docstring census R235 asked for: one retired gate, five stale descendants

**Serves:** maintenance — [[R235]]'s closing column names this census as the precondition for
calling the row closed.

**Date:** 2026-09-15. **Tree:** branch `r235-stale-gate-citations`, cut from `main` at `63156d9`.
**Five docstrings/comments corrected. No executable line changed.**

**Doc impact: none.**

[[R235]] asked: *how many docstrings in `src/iladub/etkl/` name a threshold, statistic or gate that
a later loop replaced?* It was raised because one such docstring misled a loop in the same week it
was read ([[R234]]'s measurement, corrected pre-merge in PR #229).

---

## 1. The instrument, and the version of it that found nothing

**The obvious check is worthless here, and that had to be designed around.** "Does this identifier
still exist in `src/`?" would **miss [[R235]] itself** — `lead` is still live in `cells.py` as the
fallback when a band certifies no row boundary. An instrument that cannot find its own founding
case is a low-power oracle, so the census keys on the **claimed comparison** (`gap < lead`) and asks
whether that comparison occurs in the code being described. A claim about a gate is falsifiable
against the gate; a bare identifier is not.

**v1 found 2 candidates and neither was R235 — because v1 was self-validating.** It searched each
file's full text for the claimed comparison. That text *contains the docstring making the claim*, so
`gap < lead` matched itself and was discarded as current. The failure is the same shape as the one
the previous loop recorded (*a null result is not self-validating*), one level up: **the instrument
confirmed the claim against the claim.**

**v2 blanks every STRING and COMMENT token** (via `tokenize`, positions preserved so line structure
survives) and searches only executable code. It carries its own control:

```
CONTROL (must find R235, headers.py `gap < lead`): PASS -- gap < lead
```

A census that cannot find the defect it was commissioned for reports `FAIL -- instrument is
low-power, do not trust it` and says so in its output.

## 2. What it measured

```
scanned 68 files, 430 docstrings, 51 backticked comparisons
=== 13 CANDIDATE stale-gate claims ===   ->   2 TRUE, 11 false
```

**The 11 false positives, triaged by reading each one** (a candidate is not a verdict — the
operative question is whether the docstring states the gate as CURRENT or as HISTORY):

| site | why it is not a defect |
| --- | --- |
| `cells.py` ×4 | Its own *"The previous gate, `gap < lead` (B3), asserted…"* and the `lead` **fallback**, which is live. Correct prose. |
| `adoption.py:43` | **Instrument bug.** The claim `tokens_asserted + tokens_escalated > 0` matches the code exactly (`compile`-side, `r.tokens_asserted + r.tokens_escalated > 0`); `cooccurs` requires the operator to sit *between* the two operands and cannot match the `a + b > 0` form. |
| `headers.py:166` | **Prescribed absence.** *"Do NOT add a `cc != lc and cc != rc` guard"* describes code that deliberately does not exist. The instrument reads absence as staleness. |
| `compile.py:510` | A worked example, `(first, last) == (2, 5)`. |
| `donation.py:55` | SPARQL (`FILTER(?a < ?b)`) — lives in `.rq`, outside a Python-only corpus. |
| `holon.py:417`, `membrane.py:538` | An IRI pattern and a prose placeholder. |

## 3. The answer is narrower than the question

**Every true positive traces to ONE event:** [[R208]] replacing `gap < lead` with
`gap < tightest_row_gap` (`0133362`, 2026-09-10). A power check over every *"retired / no longer /
replaced / superseded"* mention in `src/iladub/etkl/*.py` surfaced **no second replacement event
with un-updated descendants** — the other hits describe current state accurately, and `membrane.py`
even labels its own stale passage *"HISTORY, no longer justification"*.

**This is not diffuse rot. It is one commit with five descendants**, found by widening from the
census's 2 `src/` hits to the whole repo:

| site | stated as | status |
| --- | --- | --- |
| `src/iladub/etkl/headers.py` | present tense | [[R235]] — the founding case |
| `src/iladub/etkl/rowrole.py` | present tense, **inside the § 8 NEURAL justification** | new |
| `tests/etkl/test_rowrole_reading.py` | present tense | new |
| `tests/etkl/test_row_defusion.py` | present tense | new |
| `tests/etkl/test_rowrole_integration.py` | present tense | new |

Already correct, and left alone: `cells.py` (6 mentions of `tightest_row_gap`),
`tests/etkl/test_wrap_continuation.py`, `scripts/at_pitch_weld_probe.py`.

**Severity, stated honestly: in all five the CONCLUSION still holds.** Each argues *"at uniform
pitch the gate cannot fire"*, which remains true under `tightest_row_gap` — [[R234]] measured
exactly that on ons p4 (`12.00 < 12.00` false). These are **wrong citations with right
conclusions**, individually minor. Collectively they were enough to send a loop down a false path.

## 4. The fix

All five now name `gap < tightest_row_gap`, mark `gap < lead` and `0.9 x lead` as retired, cite
[[R208]] (`0133362`), and restate their worked examples against *the minimum over the band's certain
pairs* rather than a median. `headers.py` additionally records the live ons p4 case (the band's own
spanning→leaf boundary certifies 12.00pt, its wraps sit at 12.00pt), names [[R208]] spec § 4 HONEST
LIMIT (b) as the accepted residual, and warns that the NEURAL proposer it points to is **not always
reached** — on ons p4 `merge_tiling_ok` is satisfied by the truncated tree ([[R234]]).

**Citations are by SYMBOL, not line number** (CLAUDE.md § Plan authoring discipline rule 7): every
reference is to `cells.group_wrapped` / `tightest_row_gap` / a commit SHA, so the downward same-file
hazard is removed rather than guarded, and no re-measurement after the edit is required.

**No executable line changed** — docstrings and one comment block only.

## 5. What this census does NOT claim

- **It catches only backticked COMPARISONS.** A stale threshold named in pure prose, with no
  comparison, is invisible to it. `headers.py` was caught only because it *also* carried the
  comparison; its adjacent prose (*"the adaptive median inter-line gap"*) would not have been.
- **Python only.** `.rq` SPARQL, `vocab/`, and `docs/wiki/` are unscanned.
- **It is not a lint and is not shipped.** It is a scratch instrument, re-runnable from § 1's
  description; shipping it would imply coverage it does not have (2 of 13 candidates were its own
  bugs — see § 2).
- **"No second replacement event" is a grep over a vocabulary of change-words**, not a proof. A
  replacement documented without any of those words would not appear.
