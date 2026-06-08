# Design — `vault` as a global, infra-agnostic Claude Code capability

**Date:** 2026-06-08
**Author:** François Rosselet
**Status:** Approved design, pending implementation plan

## Goal

Make **vault** — the curated, strongly-interconnected LLMWiki of articles and notes
underpinning iladub / ET(K)L / holon-graph / AI theory — available as a **global**
Claude Code capability that works identically from any machine: the personal Mac and a
corporate laptop behind an enterprise proxy. The capability is **read-only** against the
public GitHub repo and is **infra-agnostic** (no dependency on a fixed local path such as
`/Volumes/WD Green/dev/git/vault`).

## Source of truth

- Public repo: **`github.com/Frosselet/vault`**, default branch **`main`**.
- Verified reachable two ways:
  - `gh api repos/Frosselet/vault/...` (authenticated, honors `HTTPS_PROXY`, 5000 req/hr).
  - `curl -fsSL https://raw.githubusercontent.com/Frosselet/vault/main/<path>` —
    **unauthenticated, HTTP 200** (the corporate fallback; needs no token).
- Vault is a self-contained Obsidian/LLMWiki vault with its own `CLAUDE.md` contract:
  `wiki/index.md` is the catalog and is **read first**; every wiki page carries a
  `confidence` (high/medium/low); knowledge is connected by `[[wikilinks]]`; `raw/` is
  immutable; writes happen only via the vault's own `/ingest` `/query` `/lint` on the
  machine that holds the local clone.

## Decisions (settled)

1. **Footprint on corporate laptop: ephemeral, no copy.** Fetch only the pages a question
   needs, use them in-context, persist nothing to disk. Keeps the personal knowledge base
   off company hardware — consistent with iladub's "personal resources, no internal data"
   posture.
2. **Read-only.** The capability only ever issues GETs. No clone-with-write, no push.
3. **Transport: try both, in order.** `gh api` when available and authed, else
   unauthenticated `curl` to `raw.githubusercontent.com`. Both honor proxy env vars.
4. **Global, not per-project.** Lives in `~/.claude/skills/`, available in every project
   and session.

## Architecture

### Component 1 — `vault-fetch.sh` (bundled transport script)

Location: `~/.claude/skills/vault/scripts/vault-fetch.sh`. Deterministic, read-only.

Verbs:
- `vault-fetch.sh get <path>` — print one file's raw contents to stdout.
- `vault-fetch.sh ls <dir>` — list a directory's entries.

Transport resolution order (first that succeeds wins):
1. **Local clone** — used only if `VAULT_LOCAL` is set and points at an existing clone
   (personal Mac fast path). Never configured on corporate.
2. **`gh api`** — `gh api -H "Accept: application/vnd.github.raw"
   repos/Frosselet/vault/contents/<path>` for `get`; `gh api repos/Frosselet/vault/contents/<dir> -q '.[].name'`
   for `ls`. Used when `gh` exists and `gh auth status` succeeds.
3. **`curl` raw** — `curl -fsSL https://raw.githubusercontent.com/Frosselet/vault/main/<path>`
   for `get`; the unauthenticated contents API for `ls`. The verified corporate fallback.

Config via env (with sensible defaults baked in):
- `VAULT_REPO` (default `Frosselet/vault`), `VAULT_BRANCH` (default `main`),
  `VAULT_LOCAL` (optional path to a local clone).

Properties: **read-only** (GET only), **ephemeral** (stdout only; no cache file written),
**proxy-aware** (delegates to `gh`/`curl`, which read `HTTPS_PROXY`/`HTTP_PROXY`/`NO_PROXY`).

### Component 2 — `SKILL.md` (the skill procedure)

Location: `~/.claude/skills/vault/SKILL.md`. Model-invoked.

Triggers: a question touches iladub / ET(K)L / holon-graph / CGA or the theory behind
them; the user references vault; or design work in the iladub repo needs grounding.

Procedure:
1. **Index-first** — `get wiki/index.md` and `wiki/overview.md` (honors the vault contract).
2. Select relevant `concepts/` `entities/` `sources/` `comparisons/` pages from the index.
3. `get` those pages; follow `[[wikilinks]]` one hop when it helps.
4. **Answer grounded** — cite `wiki/…md` paths and surface each page's `confidence`. Vault
   claims are flagged as vault-sourced, never silently merged into Claude's own assertions
   (mirrors iladub's assert-vs-propose discipline).
5. **Never write** to vault. Writing operations stay on the machine with the local clone.

### Component 3 — `/vault` slash command (optional, thin)

Location: `~/.claude/commands/vault.md`. An explicit entrypoint (`/vault <question>`) that
runs the same procedure. Complements — does not replace — automatic skill invocation.

### Component 4 — Discovery / search behavior

- Primary discovery is always the `index.md` catalog (by vault design).
- When `gh` is available, the skill may additionally run
  `gh search code --repo Frosselet/vault <term>` for deeper full-text search.
- If it falls back to index-only navigation (corporate, no `gh`), it **says so** — no
  silent coverage gaps.

### Component 5 — iladub linkage

A short subsection added to `iladub/CLAUDE.md` declaring vault the canonical **grounding
knowledge source** for ET(K)L / holon theory, reachable via the global `vault` skill, so
design work in this repo consults the curated theory rather than re-deriving it. Scope:
one paragraph + the repo slug; not a re-litigation of any existing decision.

## Installing on a second machine (the corporate laptop)

The capability is **just files under `~/.claude/`** — there is no build step. To make it
available on the company laptop (which also runs Claude Code):

**Path A — git-tracked dotfiles (preferred if `~/.claude` is already version-controlled).**
1. Commit `~/.claude/skills/vault/` (and `~/.claude/commands/vault.md` if used) to your
   dotfiles repo on the personal Mac.
2. On the corporate laptop, pull the dotfiles repo so the same files land in `~/.claude/`.

**Path B — manual copy (no dotfiles repo).**
1. Copy the directory `~/.claude/skills/vault/` to the same location on the corporate
   laptop (e.g. via a USB drive, an internal file share, or `scp`). It is a handful of
   small text files — no secrets, no vault content.

**Corporate-laptop prerequisites & checks:**
- Ensure `~/.claude/skills/vault/scripts/vault-fetch.sh` is executable (`chmod +x`).
- **No token required**: the `curl` raw transport reaches the public repo unauthenticated.
  If `gh` happens to be installed and you want the higher rate limit, `gh auth login` once.
- **Proxy:** if the corporate shell sets `HTTPS_PROXY`/`HTTP_PROXY`, both `gh` and `curl`
  pick it up automatically — nothing to configure in the skill.
- **One-time verification** (run in the corporate terminal):
  `~/.claude/skills/vault/scripts/vault-fetch.sh get wiki/index.md` — expect the catalog to
  print. If it does, the capability is live in every Claude Code session on that machine.
- Do **not** set `VAULT_LOCAL` on corporate (keeps it ephemeral, no on-disk copy).

## Testing

- `vault-fetch.sh get wiki/index.md` returns the catalog (both transports, exercised by
  forcing each path).
- `vault-fetch.sh ls wiki/concepts` lists pages.
- Transport fallback: with `gh` forced unavailable, `curl` path still returns content.
- Read-only guarantee: script contains no write/push/clone-with-write operations (grep-asserted).
- Proxy honored: with `HTTPS_PROXY` set to a dummy, the command fails fast through the proxy
  (proving it is consulted) rather than connecting directly.

## Out of scope

- Writing to vault from other machines (`/ingest` etc. stay local to the clone).
- Persistent caching on corporate.
- A GitHub MCP server (rejected: heaviest per-machine setup, proxy-fragile, overkill for one
  public read-only repo).
