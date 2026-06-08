# Design — `eduba` as a global, infra-agnostic Claude Code capability

**Date:** 2026-06-08
**Author:** François Rosselet
**Status:** Approved design, pending implementation plan

> **Name.** The skill is called **`eduba`** — Sumerian *é-dub-ba*, the "tablet-house"
> (scribal archive/library), the natural companion to **iladub** (*íl-dub*, the
> document-carrier). It is deliberately **not** named `vault`: on a corporate laptop
> "Vault" is the secrets-management infrastructure, and a skill named `vault` reading from
> a private GitHub repo would invite needless security suspicion.

## Goal

Make **vault** — the curated, strongly-interconnected LLMWiki of articles and notes
underpinning iladub / ET(K)L / holon-graph / AI theory — available as a **global**
Claude Code capability (the **`eduba`** skill) that works identically from any machine: the
personal Mac and a corporate laptop behind an enterprise proxy. The capability is
**read-only** against the GitHub repo and is **infra-agnostic** (no dependency on a fixed
local path such as `/Volumes/WD Green/dev/git/vault`).

> Terminology: the **repo/knowledge base** keeps its own name *vault*
> (`github.com/Frosselet/vault`); the **Claude Code skill that reads it** is *eduba*.

## Source of truth

- Repo: **`github.com/Frosselet/vault`**, default branch **`main`**, **private**.
- The repo is **private by design**: its README and `AGENTS.md` state that `raw/`
  reproduces verbatim third-party material for private study and **must not be
  redistributed**. (The repo was briefly public on 2026-06-08; reverted to private the
  same day once this conflict was caught. The authed transport below is the consequence of
  that decision.)
- Access transport verified under private visibility:
  - `gh api -H "Accept: application/vnd.github.raw" repos/Frosselet/vault/contents/<path>`
    (authenticated) → returns raw file content. Honors `HTTPS_PROXY`. **Works.**
  - Unauthenticated `raw.githubusercontent.com` → **HTTP 404** (correctly blocked).
- The vault ships its own agent contract:
  - **`AGENTS.md` Role A** is the canonical *consumption* protocol: read `wiki/index.md`
    first, then `wiki/overview.md`; resolve `[[WikiLinks]]` by basename
    (`[[PageName]]` → `wiki/**/PageName.md`, case-insensitive, drop `|alias`); weight by
    `confidence` (high > medium > low); honor `[[raw/...]]` provenance.
  - `CLAUDE.md` is the maintainer contract; `wiki/index.md` is the live catalog
    (74 concepts, 33 entities, 35 source summaries, 8 comparisons at time of writing).

## Decisions (settled)

1. **Skill name is `eduba`**, never `vault` (corporate-security collision).
2. **Repo stays private.** Third-party `raw/` material is not redistributed.
3. **Transport: authenticated `gh api` only.** The unauthenticated path is gone with
   privacy. The corporate laptop must `gh auth login` once.
4. **Footprint on corporate laptop: ephemeral, no copy.** Fetch only the pages a question
   needs, use them in-context, persist nothing to disk — consistent with iladub's
   "personal resources, no internal data" posture.
5. **Read-only.** The capability only ever issues GETs. No clone-with-write, no push.
6. **Defer to the vault's own contract.** The skill does not duplicate the consumption
   protocol; it points at `AGENTS.md` Role A so it auto-tracks future changes.
7. **Global, not per-project.** Lives in `~/.claude/skills/`, available in every project
   and session.
8. **Two entrypoints.** Build both the auto-invoked skill and a thin `/eduba` command.
9. **No iladub repo change.** `iladub/CLAUDE.md` is left untouched.

## Architecture

### Component 1 — `eduba-fetch.sh` (bundled transport script)

Location: `~/.claude/skills/eduba/scripts/eduba-fetch.sh`. Deterministic, read-only.

Verbs:

- `eduba-fetch.sh get <path>` — print one file's raw contents to stdout.
- `eduba-fetch.sh ls <dir>` — list a directory's entries.

Transport resolution order (first that succeeds wins):

1. **Local clone** — used only if `EDUBA_LOCAL` is set and points at an existing clone
   (personal Mac fast path). Never configured on corporate.
2. **`gh api` (authenticated, primary)** —
   `gh api -H "Accept: application/vnd.github.raw" repos/$EDUBA_REPO/contents/<path>?ref=$EDUBA_BRANCH`
   for `get`; `gh api repos/$EDUBA_REPO/contents/<dir> -q '.[].name'` for `ls`.
3. **`curl` + token (optional fallback)** — for a machine where the `gh` CLI cannot be
   installed but a PAT is available: `curl -fsSL -H "Authorization: Bearer $GITHUB_TOKEN"
   -H "Accept: application/vnd.github.raw" https://api.github.com/repos/$EDUBA_REPO/contents/<path>?ref=$EDUBA_BRANCH`.
   Off unless `$GITHUB_TOKEN` is set.

Preflight: if no transport is available (no local clone, `gh` not authed, no token), the
script exits non-zero with a one-line remedy (`run: gh auth login`).

Config via env (defaults baked in): `EDUBA_REPO` (default `Frosselet/vault`),
`EDUBA_BRANCH` (default `main`), `EDUBA_LOCAL` (optional), `GITHUB_TOKEN` (optional).

Properties: **read-only** (GET only), **ephemeral** (stdout only; no cache file written),
**proxy-aware** (delegates to `gh`/`curl`, which read `HTTPS_PROXY`/`HTTP_PROXY`/`NO_PROXY`).

### Component 2 — `SKILL.md` (the skill procedure)

Location: `~/.claude/skills/eduba/SKILL.md`. Model-invoked. Thin by design — it owns
*transport + grounding*, and delegates *how to read the graph* to the vault's `AGENTS.md`.

Triggers: a question touches iladub / ET(K)L / holon-graph / CGA or the theory behind
them; the user references vault / eduba; or design work in the iladub repo needs grounding.

Procedure:

1. `get AGENTS.md` once per session if not already seen — adopt **Role A** as the
   consumption contract (do not restate it; follow it).
2. **Index-first** — `get wiki/index.md`, then `wiki/overview.md`.
3. Select relevant `concepts/` `entities/` `sources/` `comparisons/` pages.
4. `get` those pages; resolve `[[WikiLinks]]` by basename, one hop when it helps.
5. **Answer grounded** — cite `wiki/…md` paths and surface each page's `confidence`. Vault
   claims are flagged as vault-sourced, never silently merged into Claude's own assertions
   (mirrors iladub's assert-vs-propose discipline). Treat `low`-confidence claims as
   provisional.
6. **Never write** to vault. Writing (`/ingest` `/query` `/lint`) stays on the machine with
   the local clone.

### Component 3 — `/eduba` slash command (thin wrapper)

Location: `~/.claude/commands/eduba.md`. Explicit entrypoint (`/eduba <question>`) running
the same procedure as the skill. Both entrypoints ship: the **skill** gives automatic,
model-invoked grounding during iladub work; the **command** is a ~15-line wrapper for
explicit on-demand queries. Complements — does not replace — automatic skill invocation.

### Component 4 — Discovery / search behavior

- Primary discovery is always the `index.md` catalog (by vault design).
- For deeper full-text search, `gh search code --repo Frosselet/vault <term>` (authed).
- If only index-navigation is available, the skill **says so** — no silent coverage gaps.

### iladub linkage — none (decided)

No change to `iladub/CLAUDE.md`. The capability is purely a global `~/.claude/` skill;
iladub's repo files stay untouched. Grounding happens via automatic skill invocation (and
explicit `/eduba`), not via a pointer committed into this repo.

## Installing on a second machine (the corporate laptop)

The capability is **just files under `~/.claude/`** — there is no build step.

**Copy the skill files:**

- *Path A — git-tracked dotfiles (preferred):* commit `~/.claude/skills/eduba/` (and
  `~/.claude/commands/eduba.md` if used) to your dotfiles repo; pull it on the corporate
  laptop.
- *Path B — manual copy:* copy `~/.claude/skills/eduba/` to the same path on the corporate
  laptop (USB / internal share / `scp`). A handful of small text files — **no secrets, no
  vault content**.

**Make access work (the repo is private, so this is required):**

1. Install GitHub CLI if absent (`brew install gh`, or your corporate package channel).
2. **`gh auth login`** once — authenticate to the account that can read `Frosselet/vault`.
   `gh` stores the token in the OS keychain and honors `HTTPS_PROXY` automatically.
   - *If `gh` cannot be installed* on the corporate machine: instead set `GITHUB_TOKEN` to a
     fine-grained PAT with read-only Contents on `Frosselet/vault`; the script's curl
     fallback uses it.
3. `chmod +x ~/.claude/skills/eduba/scripts/eduba-fetch.sh`.
4. **Do not** set `EDUBA_LOCAL` on corporate (keeps it ephemeral, no on-disk copy).
5. **One-time verification:**
   `~/.claude/skills/eduba/scripts/eduba-fetch.sh get wiki/index.md` — expect the catalog to
   print. If it does, the capability is live in every Claude Code session on that machine.

**Proxy:** if the corporate shell sets `HTTPS_PROXY`/`HTTP_PROXY`, `gh` (and the curl
fallback) pick it up automatically — nothing to configure in the skill.

## Testing

- `eduba-fetch.sh get wiki/index.md` returns the catalog via the `gh api` path.
- `eduba-fetch.sh ls wiki/concepts` lists pages.
- Token fallback: with `gh` forced unavailable and `GITHUB_TOKEN` set, curl path returns
  content; with neither, the script exits non-zero with the `gh auth login` remedy.
- Read-only guarantee: script contains no write/push/clone-with-write operations
  (grep-asserted).
- Privacy guarantee: unauthenticated `raw.githubusercontent.com` fetch returns 404
  (regression guard against accidental re-publication).
- Proxy honored: with `HTTPS_PROXY` set to a dummy, the command fails through the proxy
  (proving it is consulted) rather than connecting directly.

## Out of scope

- Writing to vault from other machines (`/ingest` etc. stay local to the clone).
- Persistent caching on corporate.
- Re-publishing the repo or any part of `raw/`.
- A GitHub MCP server (rejected: heaviest per-machine setup, proxy-fragile, overkill for one
  private read-only repo).
