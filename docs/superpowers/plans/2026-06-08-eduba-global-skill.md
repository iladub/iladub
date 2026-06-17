# eduba Global Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `eduba`, a global Claude Code skill (+ thin `/eduba` command) that reads the private `Frosselet/vault` LLMWiki read-only and grounds answers in it, working identically on the personal Mac and a corporate laptop behind a proxy.

**Architecture:** A bundled, deterministic, read-only bash fetch script (`eduba-fetch.sh`) resolves transport in the order local-clone → authed `gh api` → `curl`+token, exposing two verbs (`get`, `ls`). A thin `SKILL.md` owns transport + grounding and defers the consumption protocol to the vault's own `AGENTS.md` Role A. A `/eduba` command is a one-line wrapper over the same procedure. Everything lives under `~/.claude/` (global), nothing in the iladub repo.

**Tech Stack:** bash, GitHub CLI (`gh`), curl. No `jq`/`python3` dependency (uses `gh -q`). Markdown skill + command files.

**Spec:** `docs/superpowers/specs/2026-06-08-eduba-global-skill-design.md`

> **Note on commits.** `~/.claude` is not a git repo, so the skill files get no per-task `git commit`. Each task's checkpoint is the runnable test script `test-eduba-fetch.sh` returning the expected result. Versioning/distribution is handled once in Task 7. The plan and spec themselves are committed to the iladub repo (Task 8). All fetch tests are integration tests against the live private repo and require `gh` to be authenticated (it is, on this machine).

---

### Task 1: Scaffold the skill directory and a failing fetch test

**Files:**
- Create: `~/.claude/skills/eduba/scripts/eduba-fetch.sh` (empty placeholder this task)
- Create: `~/.claude/skills/eduba/scripts/test-eduba-fetch.sh`

- [ ] **Step 1: Create the directories**

Run:
```bash
mkdir -p ~/.claude/skills/eduba/scripts
```

- [ ] **Step 2: Write the test harness with the first failing test**

Create `~/.claude/skills/eduba/scripts/test-eduba-fetch.sh`:
```bash
#!/usr/bin/env bash
# Regression tests for eduba-fetch.sh.
# Fetch tests are integration tests against the live private repo and require `gh` authed.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FETCH="$HERE/eduba-fetch.sh"
fails=0
t() { # t <name> <cmd...>
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then printf 'ok   %s\n' "$name"
  else printf 'FAIL %s\n' "$name"; fails=$((fails+1)); fi
}

t "get index" bash -c "\"$FETCH\" get wiki/index.md | grep -q 'title: Index'"

echo "---"
[ "$fails" -eq 0 ] && echo "ALL PASS" || { echo "$fails FAILED"; exit 1; }
```

- [ ] **Step 3: Make the test runnable and run it to verify it FAILS**

Run:
```bash
chmod +x ~/.claude/skills/eduba/scripts/test-eduba-fetch.sh
bash ~/.claude/skills/eduba/scripts/test-eduba-fetch.sh
```
Expected: `FAIL get index` then `1 FAILED` (the fetch script does not exist yet).

---

### Task 2: Implement `eduba-fetch.sh` with the `get` verb

**Files:**
- Create: `~/.claude/skills/eduba/scripts/eduba-fetch.sh`
- Test: `~/.claude/skills/eduba/scripts/test-eduba-fetch.sh` (already has `get index`)

- [ ] **Step 1: Write the script**

Create `~/.claude/skills/eduba/scripts/eduba-fetch.sh`:
```bash
#!/usr/bin/env bash
# eduba-fetch.sh — read-only reader for the private vault LLMWiki.
# Repo: github.com/Frosselet/vault. Verbs: get <path> | ls <dir>.
# Transport order: local clone (EDUBA_LOCAL) -> gh api (authed) -> curl + GITHUB_TOKEN.
# Read-only by construction: GET requests only; never writes, pushes, or clones.
set -euo pipefail

EDUBA_REPO="${EDUBA_REPO:-Frosselet/vault}"
EDUBA_BRANCH="${EDUBA_BRANCH:-main}"
EDUBA_LOCAL="${EDUBA_LOCAL:-}"

die() { printf 'eduba: %s\n' "$*" >&2; exit 1; }
have_gh() { command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; }

get_local() { [ -n "$EDUBA_LOCAL" ] && [ -f "$EDUBA_LOCAL/$1" ] && cat "$EDUBA_LOCAL/$1"; }
ls_local()  { [ -n "$EDUBA_LOCAL" ] && [ -d "$EDUBA_LOCAL/$1" ] && ls -1 "$EDUBA_LOCAL/$1"; }

get_gh() { gh api -H "Accept: application/vnd.github.raw" "repos/$EDUBA_REPO/contents/$1?ref=$EDUBA_BRANCH"; }
ls_gh()  { gh api "repos/$EDUBA_REPO/contents/$1?ref=$EDUBA_BRANCH" -q '.[].name'; }

get_curl() {
  [ -n "${GITHUB_TOKEN:-}" ] || return 1
  curl -fsSL -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github.raw" \
    "https://api.github.com/repos/$EDUBA_REPO/contents/$1?ref=$EDUBA_BRANCH"
}

cmd="${1:-}"; arg="${2:-}"
[ -n "$cmd" ] && [ -n "$arg" ] || die "usage: eduba-fetch.sh get <path> | ls <dir>"

case "$cmd" in
  get)
    if get_local "$arg"; then exit 0; fi
    if have_gh; then get_gh "$arg"; exit 0; fi
    if get_curl "$arg"; then exit 0; fi
    die "no transport available — run: gh auth login   (or set GITHUB_TOKEN)" ;;
  ls)
    if ls_local "$arg"; then exit 0; fi
    if have_gh; then ls_gh "$arg"; exit 0; fi
    die "ls needs gh or EDUBA_LOCAL — run: gh auth login   (or: eduba-fetch.sh get wiki/index.md)" ;;
  *)
    die "unknown verb '$cmd' — use: get | ls" ;;
esac
```

- [ ] **Step 2: Make it executable**

Run:
```bash
chmod +x ~/.claude/skills/eduba/scripts/eduba-fetch.sh
```

- [ ] **Step 3: Run the test to verify the `get index` test PASSES**

Run:
```bash
bash ~/.claude/skills/eduba/scripts/test-eduba-fetch.sh
```
Expected: `ok   get index` then `ALL PASS`.

- [ ] **Step 4: Manually sanity-check a real fetch**

Run:
```bash
~/.claude/skills/eduba/scripts/eduba-fetch.sh get wiki/overview.md | head -5
```
Expected: the first lines of the overview page (YAML frontmatter or prose), not an error.

---

### Task 3: Add the `ls` verb

**Files:**
- Modify: `~/.claude/skills/eduba/scripts/test-eduba-fetch.sh` (add `ls` test)
- (Implementation already present in `eduba-fetch.sh` from Task 2 — this task verifies it via test.)

- [ ] **Step 1: Add the failing `ls` test**

In `~/.claude/skills/eduba/scripts/test-eduba-fetch.sh`, add this line immediately after the `get index` test line:
```bash
t "ls concepts" bash -c "\"$FETCH\" ls wiki/concepts | grep -q 'Holon.md'"
```

- [ ] **Step 2: Run the tests to verify both PASS**

Run:
```bash
bash ~/.claude/skills/eduba/scripts/test-eduba-fetch.sh
```
Expected: `ok   get index`, `ok   ls concepts`, then `ALL PASS`.

(If `ls concepts` fails with a transport error rather than a missing page, confirm `gh auth status` succeeds; if it fails because `Holon.md` was renamed, replace the grep target with any page name from `eduba-fetch.sh ls wiki/concepts`.)

---

### Task 4: Lock in the read-only, preflight, and privacy guarantees

**Files:**
- Modify: `~/.claude/skills/eduba/scripts/test-eduba-fetch.sh` (add three guarantee tests)

- [ ] **Step 1: Add the three guarantee tests**

In `~/.claude/skills/eduba/scripts/test-eduba-fetch.sh`, add these three lines immediately after the `ls concepts` test line:
```bash
t "read-only" bash -c "! grep -Eq 'git +push|clone|-X +(POST|PUT|PATCH|DELETE)|--method +(POST|PUT|PATCH|DELETE)' \"$FETCH\""
t "preflight remedy" bash -c "out=\$(PATH=/usr/bin:/bin GITHUB_TOKEN= \"$FETCH\" get wiki/index.md 2>&1 || true); printf '%s' \"\$out\" | grep -q 'gh auth login'"
t "privacy 404" bash -c "[ \"\$(curl -s -o /dev/null -w '%{http_code}' https://raw.githubusercontent.com/Frosselet/vault/main/wiki/index.md)\" = 404 ]"
t "proxy honored" bash -c "! HTTPS_PROXY=http://127.0.0.1:9 \"$FETCH\" get wiki/index.md >/dev/null 2>&1"
```

What each asserts:
- **read-only** — the script contains no mutating git/API verbs (push, clone, POST/PUT/PATCH/DELETE).
- **preflight remedy** — with `gh` removed from `PATH` and no `GITHUB_TOKEN`, a `get` exits with the `gh auth login` remedy instead of hanging or crashing.
- **privacy 404** — an unauthenticated raw fetch of a vault page returns HTTP 404, proving the repo is private (regression guard against accidental re-publication).
- **proxy honored** — forced through a dead proxy (`HTTPS_PROXY=http://127.0.0.1:9`), the fetch *fails* (nonzero), proving `gh`/`curl` actually consult the proxy env rather than connecting directly. (Port 9 = discard; connection is refused fast.)

- [ ] **Step 2: Run the full suite to verify all six PASS**

Run:
```bash
bash ~/.claude/skills/eduba/scripts/test-eduba-fetch.sh
```
Expected:
```
ok   get index
ok   ls concepts
ok   read-only
ok   preflight remedy
ok   privacy 404
ok   proxy honored
---
ALL PASS
```

---

### Task 5: Write the skill (`SKILL.md`)

**Files:**
- Create: `~/.claude/skills/eduba/SKILL.md`

- [ ] **Step 1: Write the skill file**

Create `~/.claude/skills/eduba/SKILL.md`:
```markdown
---
name: eduba
description: Use when a question touches iladub, ET(K)L, holon-graph / CGA, or the theory behind them, or when the user references the vault / eduba knowledge base. Reads the private Frosselet/vault LLMWiki read-only via gh and answers grounded with citations and confidence levels. Never writes to the vault.
---

# eduba — grounding answers in the vault LLMWiki

`eduba` (Sumerian *é-dub-ba*, "tablet-house") reads the private **vault** knowledge base
(`github.com/Frosselet/vault`) read-only and grounds answers in it. The repo is private;
access is authenticated `gh`. Never write to it.

## How to read the vault

Fetch with the bundled script (transport is auto-selected; output goes to stdout):

- `scripts/eduba-fetch.sh get <path>` — print one file (e.g. `get wiki/index.md`)
- `scripts/eduba-fetch.sh ls <dir>` — list a directory (e.g. `ls wiki/concepts`)

Resolve the script path relative to this skill file.

For deeper full-text search across the vault (beyond the `index.md` catalog), run
`gh search code --repo Frosselet/vault <term>` when `gh` is available. If only index
navigation is available, rely on `get wiki/index.md` and say so.

## Procedure

1. **Adopt the vault's own contract.** Once per session, `get AGENTS.md` and follow its
   **Role A** (consumer) protocol. Do not restate it — follow it.
2. **Index first.** `get wiki/index.md` (the catalog), then `get wiki/overview.md`.
3. **Select pages.** From the index, pick the relevant `concepts/`, `entities/`,
   `sources/`, `comparisons/` pages for the question.
4. **Fetch and traverse.** `get` those pages. Resolve `[[WikiLinks]]` by basename
   (`[[PageName]]` → `wiki/**/PageName.md`, case-insensitive, drop any `|alias`), following
   one hop when it sharpens the answer.
5. **Answer grounded.** Cite the `wiki/…md` page(s) behind each claim and surface their
   `confidence` (high/medium/low). Flag vault claims as vault-sourced — do not silently
   merge them into your own assertions. Treat `low`-confidence claims as provisional.

## Guardrails

- **Read-only.** Only ever `get`/`ls`. Never write, push, or run the vault's
  `/ingest` `/query` `/lint` from here — those belong to the machine that holds the clone.
- **Ephemeral.** Don't cache vault content to disk; use what you fetched in-context.
- **Transport trouble?** If a fetch fails with "gh auth login", tell the user to run
  `gh auth login` once (the repo is private). If only index navigation is available, say
  so — don't imply full coverage.
```

- [ ] **Step 2: Verify the script path referenced in the skill resolves**

Run:
```bash
test -x ~/.claude/skills/eduba/scripts/eduba-fetch.sh && echo "script present + executable"
```
Expected: `script present + executable`.

---

### Task 6: Write the `/eduba` command

**Files:**
- Create: `~/.claude/commands/eduba.md`

- [ ] **Step 1: Create the commands directory**

Run:
```bash
mkdir -p ~/.claude/commands
```

- [ ] **Step 2: Write the command file**

Create `~/.claude/commands/eduba.md`:
```markdown
---
description: Answer a question grounded in the private vault LLMWiki via the eduba skill
---

Use the `eduba` skill to answer the following, grounded in the vault knowledge base with
citations and `confidence` levels. Read-only — never write to the vault.

$ARGUMENTS
```

- [ ] **Step 3: Verify the file exists**

Run:
```bash
test -f ~/.claude/commands/eduba.md && echo "command present"
```
Expected: `command present`.

---

### Task 7: Distribution — version the global files and document the corporate install

**Files:**
- Create: `~/.claude/skills/eduba/INSTALL.md`

- [ ] **Step 1: Run the full test suite one final time**

Run:
```bash
bash ~/.claude/skills/eduba/scripts/test-eduba-fetch.sh
```
Expected: `ALL PASS`.

- [ ] **Step 2: Write the install/distribution note**

Create `~/.claude/skills/eduba/INSTALL.md`:
```markdown
# Installing the `eduba` skill on another machine (e.g. corporate laptop)

The capability is just files under `~/.claude/` — no build step.

## 1. Copy the files
Copy these to the same paths on the target machine:
- `~/.claude/skills/eduba/`  (skill + scripts)
- `~/.claude/commands/eduba.md`  (the /eduba command)

They are small text files — **no secrets, no vault content**. Use a dotfiles repo,
internal share, USB, or `scp`.

## 2. Make access work (the vault repo is private)
1. Install GitHub CLI if absent: `brew install gh` (or your corporate package channel).
2. Authenticate once: `gh auth login` — use the account that can read `Frosselet/vault`.
   `gh` stores the token in the OS keychain and honors `HTTPS_PROXY` automatically.
   - If `gh` cannot be installed: set `GITHUB_TOKEN` to a fine-grained PAT with read-only
     Contents on `Frosselet/vault`; the script's curl fallback uses it.
3. Make the script executable: `chmod +x ~/.claude/skills/eduba/scripts/eduba-fetch.sh`.
4. Do **not** set `EDUBA_LOCAL` here — keeps it ephemeral, no on-disk vault copy.

## 3. Verify
```
~/.claude/skills/eduba/scripts/eduba-fetch.sh get wiki/index.md
```
Expect the catalog to print. If it does, `eduba` is live in every Claude Code session.

## Proxy
If the corporate shell sets `HTTPS_PROXY`/`HTTP_PROXY`, `gh` and `curl` pick it up
automatically — nothing to configure in the skill.
```

- [ ] **Step 3: List the complete set of installed files**

Run:
```bash
ls -R ~/.claude/skills/eduba && echo "---" && ls ~/.claude/commands/eduba.md
```
Expected: `SKILL.md`, `INSTALL.md`, `scripts/eduba-fetch.sh`, `scripts/test-eduba-fetch.sh`, and the command file — all present.

- [ ] **Step 4: (Optional) Back up the global files into version control**

If you keep a dotfiles repo, copy `~/.claude/skills/eduba/` and `~/.claude/commands/eduba.md` into it and commit there. `~/.claude` itself is not a git repo, so there is no commit to make in place. This step is the user's choice and is not required for the skill to work.

---

### Task 8: Commit the plan and spec to the iladub repo

**Files:**
- Commit: `docs/superpowers/plans/2026-06-08-eduba-global-skill.md` (this plan)

- [ ] **Step 1: Stage and commit the plan**

Run:
```bash
cd "/Volumes/WD Green/dev/git/iladub"
git add docs/superpowers/plans/2026-06-08-eduba-global-skill.md
git commit -m "Add implementation plan for the eduba global skill

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```
Expected: a commit is created on the `add-vault-global-skill` branch.

- [ ] **Step 2: End-to-end smoke test of the actual skill (manual)**

In a Claude Code session, type `/eduba what does the vault say a holon's Markov-blanket boundary is?`
Expected: Claude fetches `wiki/index.md` + the relevant `concepts/` pages and answers with
`wiki/…md` citations and confidence levels — confirming the skill, script, and command work end to end.

---

## Notes for the implementer

- **gh must be authed** on whatever machine runs the fetch tests (`gh auth status` should succeed). On this Mac it already is.
- The fetch tests hit the **live private repo**; they are integration tests, not mocks. That is intentional — the whole capability is about reaching the real vault.
- Keep the script **read-only**: if you ever add a verb, it must be a GET. The `read-only` test guards this.
- Do **not** add an `EDUBA_LOCAL` default — it must stay empty so corporate machines never read from (or expect) a local copy.
