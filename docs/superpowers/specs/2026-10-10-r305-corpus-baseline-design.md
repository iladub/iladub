# Spec: a committed corpus baseline, so a blast-radius check is one pass (R305)

**Serves:** maintenance. This is [[R305]], picked by the maintainer on 2026-10-10 from the
candidates in `docs/superpowers/2026-10-10-r300-closed-handoff.md` § 5.1.

**Date:** 2026-10-10. **Branch:** `r305-snapshot-baseline`, cut from `main` at `554979f`.

**Doc impact: none.** It adds a script, a test and a directory of generated JSON under `tests/`. No
vocabulary term, shape, query or released assertion changes.

**Global Constraint: the neurosymbolic gate (CLAUDE.md § 8).** Everything this spec adds is
classified in § 3. None of it reads a document or decides anything about one.

---

## 0. The concern, first

A loop that changes the reading runs the whole corpus twice: once on `main` for "before", once on
the branch for "after". Each serial pass over the eleven documents takes 24 min (R305 row). The
"before" pass re-measures a `main` that has not changed since its last measurement. **This spec
removes that pass.** The "before" becomes a committed file, and the blast radius becomes
`git diff` on it after one regeneration.

What this does **not** make cheaper, stated up front so nobody expects it: an exploratory probe, a
corpus-gated test module, and the regeneration itself (still 24 min). Only the before/after pair
drops from 48 min to 24.

## 1. Measured (this session, at `554979f`)

- **What a compile reads.** An audit hook (`sys.addaudithook`, `open` events) around
  `compile_document("corpus/health/who-wfa-boys-zscore-0-5.pdf")`, 78.8 s, recorded these repo
  files outside `.venv` and `__pycache__`: the PDF, two files under `readings/header_lines/`,
  `src/iladub/etkl/document.py` (other modules loaded from bytecode, so `src/` as a whole is the
  input), 5 files under `vocab/ontology/`, 26 under `vocab/queries/` and 5 under `vocab/shapes/`.
  `socket.connect`, `socket.getaddrinfo`, `subprocess.Popen` and `os.system`: none.
- **The NEURAL readers replay offline.** `RecordedBoxheadReader.read_boxhead`
  (`src/iladub/etkl/boxhead.py`, from `READINGS_DIR` down) returns a recorded reading, and on a
  miss returns `None` unless a live reader exists. `default_reader()` attaches one only when
  `BAML_LIVE=1`, and writes only when `ILADUB_RECORD_READINGS=1`. The other three readers
  (`headerlines.py`, `printedtotal.py`, `totalrole.py`) share the `READINGS_DIR` pattern, and § 6
  records that only boxhead's miss path was read. **So the environment is an input:** with
  either variable set, a compile is neither offline nor reproducible.
- **Where the inputs change.** Of the last 60 first-parent commits touching
  `src/ vocab/ readings/` (back to 2026-08-13), 56 touch the compile core (`src/iladub/etkl/`,
  `vocab/{ontology,queries,shapes}/`, `readings/`). The other 4 touch only `vocab/internal/corpus.ttl`,
  `src/iladub/{ground,splitkey,feed,__init__}.py`. So fingerprinting the whole of those trees
  forces at most 4 in 60 needless regenerations. Narrowing it would buy little and risk a stale
  baseline passing the gate.
- **Comment-only changes are rare.** Of the same 60, 3 change no AST once docstrings are stripped
  (`9785ce3`, `f3863f3`, `a78a218`; script in this session's scratchpad). An AST-normalised
  fingerprint would save 5% of regenerations and is not built (§ 4).
- **Dependencies are floor-pinned only.** `pyproject.toml` has `rdflib>=7.0`, `pyshacl>=0.26`,
  `pyyaml>=6.0`. No `uv.lock` or requirements file exists. CI installs `pip install -e
  ".[baml,dev,docs,etkl]"` fresh. So the versions that produced a baseline live in the
  maintainer's `.venv`, where git cannot see them.
- **The corpus never reaches CI.** `.gitignore:52` ignores `corpus/` and `:55` ignores
  `held-out/`, which holds the four held-out PDFs (fed-h41, caltrain, who-covid, arxiv).
  `scripts/corpus_verdict_snapshot.py`'s `main` rglobs `corpus/` only, so today it finds seven
  documents, not eleven.
- **The snapshot is reproducible across trees.** R300's blast radius found all eleven canonical
  graph hashes equal between a `main` worktree and its branch
  (`2026-10-10-r300-closed-handoff.md` § 2a). That is the premise this spec rests on, and § 5 O1
  re-measures it on the committed bytes.

## 2. The design

**Ruled by the maintainer, 2026-10-10, in this session: the CI gate is blocking.** Every PR that
changes an input regenerates the baseline, and its diff is the blast radius in that PR. Weighed and
rejected: a local-only staleness check. This decision is recorded here and in the handoff, and
nowhere else.

**2.1 The directory.** `tests/corpus-baseline/` holds one `<stem>.json` per document, exactly what
`corpus_verdict_snapshot.snapshot()` returns, serialized as today
(`json.dumps(..., indent=2, sort_keys=True)`), plus `inputs.json`:

- `fingerprint`: the input fingerprint (§ 2.2) of the tree the baseline was generated from;
- `documents`: for each document, its repo-relative path and the SHA-256 of the PDF bytes;
- `environment`: the Python version and the installed versions of the distributions the compile
  imports. This is recorded for a human to compare. No gate reads it (§ 6).

**2.2 The fingerprint.** It is a SHA-256 over every path that `git ls-files` lists under `src/`,
`vocab/`, `readings/`, `pyproject.toml`, `scripts/corpus_baseline.py` and
`scripts/corpus_verdict_snapshot.py`, taken in sorted order. Each path contributes its name and
the SHA-256 of its bytes **on disk**. Paths come from the index and bytes from disk, so CI (where
disk equals the commit) and a dirty local tree each fingerprint what they would actually compile.
The two scripts are in the set because they determine the bytes of the baseline.

**2.3 `scripts/corpus_baseline.py`**, three subcommands:

- `regenerate`. Refuse, before writing anything, when any of these holds: `BAML_LIVE` or
  `ILADUB_RECORD_READINGS` is set; any document in the committed list is missing on disk; or
  `git ls-files --others --exclude-standard` reports an untracked file under an input path (an
  un-added module would compile locally and be invisible to the fingerprint). Otherwise, snapshot
  each document **in its own subprocess, serially**, through the existing
  `corpus_verdict_snapshot.py --pdf` form (R301). There is then no second reading path, and no
  state is shared across documents. Write into a temporary directory. Replace
  `tests/corpus-baseline/` only once all documents have succeeded, so a killed run leaves the
  committed baseline untouched.
- `check`. Compare the current fingerprint to `inputs.json`. CI can run this: it needs no corpus.
- `verify`. Regenerate into a temporary directory and compare the bytes with the committed files.
  This is the full regenerate-and-diff, and it runs wherever the corpus exists.

The document list is a constant in the script: the seven under `corpus/` and the four under
`held-out/`, by path. It is not an rglob, so a document that failed to fetch fails loudly instead
of shrinking the baseline. Changing the list changes the script, and so the fingerprint.

**2.4 The CI gate.** `tests/test_corpus_baseline.py`, not corpus-marked, so it runs in the `test`
job:

1. the current fingerprint equals `inputs.json`'s, and on failure the message is the regenerate
   command;
2. the set of `<stem>.json` files equals the document list;
3. the fingerprint function, run on a temporary copy of a fixture tree, moves when one byte of a
   file in each input class changes, and does not move when a file outside the input set changes.

**2.5 What a loop does now.** Change the code. Run `PYTHONPATH=src .venv/bin/python
scripts/corpus_baseline.py regenerate` (one pass, unattended). Read `git diff --
tests/corpus-baseline/` as the blast radius. Commit it with the change.

**What the gate guarantees, at its true strength.** CI proves the baseline was regenerated from
these inputs. It does **not** prove the committed bytes are what those inputs produce: a hand edit
that kept `inputs.json` would pass. Byte-equality is proven by `verify`, locally, where the corpus
lives. The gap exists because the corpus is third-party and never committed. It is narrower than
CLAUDE.md's generated-cache wording ("CI fails unless the tracked bytes are exactly what the source
produces"), and that wording governs tracked markdown under `docs/`, not JSON under `tests/`.
Recorded here, not hidden.

## 3. Classification (CLAUDE.md § 8)

**PROCEDURAL, all of it.** Listing files, hashing bytes, running subprocesses and comparing files
decides nothing about any document, and carries no constant or tolerance. It is irreducible to
AXIOM because its subject is files on disk and processes, not an RDF evidence graph, and
irreducible to NEURAL because nothing in it is underdetermined. The snapshot it orchestrates is
`corpus_verdict_snapshot.py`, which is already classified PROCEDURAL in its docstring.

## 4. Alternatives rejected, with the measurement that rejects them

- **Fingerprint only the compile core** (`src/iladub/etkl/`, three `vocab/` subtrees). It saves at
  most 4 in 60 regenerations (§ 1), and a lazy import or a new query directory outside the narrowed
  set would let a stale baseline pass the gate. The safe direction for an error is over-inclusion.
- **AST-normalised fingerprint, docstrings stripped.** It saves 3 in 60 (§ 1), at the cost of a
  parser in the gate and a fingerprint that disagrees with git.
- **One process for all eleven.** That is what `snapshot`'s `main` does today. It is cheaper by
  one import per document, but it lets module-level state cross documents, so a document's bytes
  could depend on the documents compiled before it. Per-document processes make order irrelevant
  by construction. Whether the two modes agree today is not measured, and with one mode fixed it
  does not need to be.
- **Commit the graphs too, so probes can query them.** That is R305's stretch. The graphs are
  large (fed-h41 alone carries thousands of cells), and the canonical hash already pins them
  triple for triple. Not built (§ 7).

## 5. Oracles

- **O1, reproducibility (PROPOSED: predicted to hold from § 1's last bullet, run before the PR
  opens).** After the first `regenerate`, `verify` must report every file byte-equal. If any
  differs, the cache is not reproducible, the gate would flake, and **this design stops there**: do
  not ship a baseline that its own second pass disagrees with. Cost: one extra 24-min pass, once.
- **O2, the gate fires.** Edit one character of a `src/` docstring without regenerating, and
  `test_corpus_baseline.py`'s fingerprint test fails. Restore, and it passes. This is the task's
  FALSIFICATION block.
- **O3, fingerprint sensitivity.** § 2.4 item 3, falsified by making the fingerprint skip one
  input class and watching that case fail.
- **O4, refusals before writes.** With `BAML_LIVE=1`, and separately with one document renamed
  away, `regenerate` exits non-zero and `git status -- tests/corpus-baseline/` is clean.

## 6. Unverified

- Only boxhead's miss path was read. That the other three readers also return no claim offline,
  and not a live call, is assumed from their shared pattern. O1 would catch a live call only if it
  made two runs differ.
- The `environment` field is a record, not a gate. A dependency upgrade in the `.venv` that moves a
  reading changes no fingerprint, so CI stays green on a baseline that local `verify` would refuse.
  Pinning dependencies (a lockfile) would close that gap. It is out of scope.
- Two input-touching PRs merged against the same base can each pass CI and leave `main` with a
  stale baseline, because `strict: false` (CLAUDE.md § Branch protection) does not re-run a PR's CI
  after `main` moves. The next push to `main` then fails `check`, so the staleness is caught, but
  only after the merge.
- Whether any snapshot field carries third-party document text. `reason` and `anchor` hold codes
  and class IRIs (`compile.py`, `RegionReport`); `notes` was not inspected. Check the first
  regenerated baseline before committing it.

## 7. What is NOT done

- No compile cache keyed by (PDF hash, fingerprint), and no profile of graincorp-stem's 336 s.
  Both are R305's stretch and are not required to close it.
- No change to corpus-gated test modules or probes. Each still compiles for itself.
- `tests/data/r301-fed-h41-baseline.json`, an earlier ungated single-document baseline, is left as
  it is.
- No lockfile (§ 6).
- No edit to CLAUDE.md. The maintainer's ruling in § 2 changes what every input-touching PR must
  carry. Whether it belongs in the Contract is the maintainer's call.

## 8. Execution

Small enough to execute from this spec without a plan, as R208 was: one script, one test, one
generated directory. Order: the fingerprint and `check` with the test, TDD. Then `regenerate` with
the § 2.3 refusals and O4. Then the first real regeneration. Then O1 `verify`. Then the PR. R305
closes when O1 holds and CI is green with the gate in it.
