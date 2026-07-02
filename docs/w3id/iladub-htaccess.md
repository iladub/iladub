# w3id.org redirect configuration — iladub namespace migration

**Draft** to submit as a PR to [perma-id/w3id.org](https://github.com/perma-id/w3id.org)
(the community redirect registry — a maintainer merges it, as dgarijo merged the original
`etkl` entry). **Not yet submitted.** Style matches the existing `w3id.org/etkl` entry
(single `HTTP_ACCEPT` alternation cond, `R=302` content-negotiation, header + `README.md`).

The migration moves all artifacts from `https://w3id.org/etkl/*` to `https://w3id.org/iladub/*`.
Two perma-id changes: **add** a new `iladub/` entry (below), and **replace** the existing
`etkl/` entry with 301 redirects to the new homes.

> **⚠️ Ordering dependency.** The RDF targets point at files on
> `github.com/iladub/iladub` **`main`** (`vocab/ontology/dec.ttl`, `etkl-holons.ttl`, …).
> Those filenames only exist on `main` **after PR #19 (the migration) merges**. Submit/merge
> this w3id PR **after** #19 lands on `main`, or the RDF redirects will 404. (Once #19 merges,
> the *old* `etkl` entry also breaks — it points at `hol.ttl`, now renamed — so land the two
> close together.)
>
> **Redirect codes:** `302` for content negotiation (matches the existing `etkl` entry's
> convention), `301` for the permanent old→new `etkl`→`iladub` moves.

---

## File 1 — new `iladub/.htaccess`

```apache
# # /iladub/
#
# Persistent namespace root for iladub and its modules:
#
#   https://w3id.org/iladub               — iladub core: assertion/proposition epistemics
#   https://w3id.org/iladub/etkl          — ET(K)L method (knowledge-first transform)
#   https://w3id.org/iladub/etkl/holons   — the doc-holon fabric (Raw/Clean/Portal/membrane)
#   https://w3id.org/iladub/dec           — dec: decidability / decision-context vocabulary
#   https://w3id.org/iladub/risk          — contextual-risk vocabulary
#   https://w3id.org/iladub/hga-alignment      — iladub/etkl ↔ W3C Holon CG (HGA) alignment
#   https://w3id.org/iladub/dec/hga-alignment  — dec ↔ HGA alignment
#   https://w3id.org/iladub/risk/hga-alignment — risk ↔ HGA alignment
#   https://w3id.org/iladub/governance-shapes  — governance SHACL shapes
#
# Content is negotiated: RDF clients receive Turtle from the source repository
# (github.com/iladub/iladub), browsers are sent to the documentation site
# (https://iladub.dev).
#
# ## Contact
# François Rosselet
# GitHub username: Frosselet

Options +FollowSymLinks
RewriteEngine on

# ---- https://w3id.org/iladub/etkl/holons  (most specific first) ----------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^etkl/holons/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/etkl-holons.ttl [R=302,L]
RewriteRule ^etkl/holons/?$ https://iladub.dev/holonic-interaction/ [R=302,L]

# ---- https://w3id.org/iladub/dec/hga-alignment --------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^dec/hga-alignment/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/dec-hga-align.ttl [R=302,L]
RewriteRule ^dec/hga-alignment/?$ https://iladub.dev/holonic-interaction/ [R=302,L]

# ---- https://w3id.org/iladub/risk/hga-alignment -------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^risk/hga-alignment/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/risk-hga-align.ttl [R=302,L]
RewriteRule ^risk/hga-alignment/?$ https://iladub.dev/holonic-interaction/ [R=302,L]

# ---- https://w3id.org/iladub/hga-alignment ------------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^hga-alignment/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/iladub-hga-align.ttl [R=302,L]
RewriteRule ^hga-alignment/?$ https://iladub.dev/holonic-interaction/ [R=302,L]

# ---- https://w3id.org/iladub/etkl ---------------------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^etkl/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/etkl.ttl [R=302,L]
RewriteRule ^etkl/?$ https://iladub.dev/etkl/ [R=302,L]

# ---- https://w3id.org/iladub/dec ----------------------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^dec/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/dec.ttl [R=302,L]
RewriteRule ^dec/?$ https://iladub.dev/dec/ [R=302,L]

# ---- https://w3id.org/iladub/risk ---------------------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^risk/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/risk.ttl [R=302,L]
RewriteRule ^risk/?$ https://iladub.dev/ [R=302,L]

# ---- https://w3id.org/iladub/governance-shapes --------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^governance-shapes/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/shapes/governance-shapes.ttl [R=302,L]
RewriteRule ^governance-shapes/?$ https://iladub.dev/ [R=302,L]

# ---- https://w3id.org/iladub (core) -------------------------------------
RewriteCond %{HTTP_ACCEPT} (text/turtle|application/rdf\+xml|application/n-triples|application/ld\+json|text/n3) [NC]
RewriteRule ^$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/iladub.ttl [R=302,L]
RewriteRule ^$ https://iladub.dev/assertion-proposition/ [R=302,L]

# ---- fallback: any other /iladub/* path -> documentation site -----------
RewriteRule ^(.*)$ https://iladub.dev/ [R=302,L]
```

## File 2 — new `iladub/README.md`

```markdown
# /iladub/

Persistent namespace root for **iladub** — the document-carrier that compiles
unstructured documents into FAIR, contract-defined semantic knowledge graphs.
`iladub = a thin epistemic core + etkl (the K-transform) + dec (decidability)`, aligned
to the W3C Holon CG substrate (HGA).

| Persistent IRI | Resolves to |
| --- | --- |
| `https://w3id.org/iladub` | iladub core — assertion/proposition epistemics |
| `https://w3id.org/iladub/etkl` | ET(K)L method (knowledge-first transform) |
| `https://w3id.org/iladub/etkl/holons` | the doc-holon fabric |
| `https://w3id.org/iladub/dec` | `dec` — decidability / decision-context vocabulary |
| `https://w3id.org/iladub/risk` | contextual-risk vocabulary |
| `https://w3id.org/iladub/hga-alignment` | iladub/etkl ↔ HGA alignment |
| `https://w3id.org/iladub/dec/hga-alignment` | dec ↔ HGA alignment |
| `https://w3id.org/iladub/risk/hga-alignment` | risk ↔ HGA alignment |
| `https://w3id.org/iladub/governance-shapes` | governance SHACL shapes |

Requests are **content-negotiated**: RDF clients (`Accept: text/turtle`,
`application/rdf+xml`, `application/ld+json`, …) are redirected to the Turtle files in the
source repository; browsers are redirected to the documentation site.

This supersedes the former `w3id.org/etkl` layout, whose paths now 301-redirect here.

- **Documentation:** https://iladub.dev
- **Source & ontologies:** https://github.com/iladub/iladub (under `vocab/`)
- **License:** ontologies are CC-BY-4.0; code is Apache-2.0.

## Maintainer

- **François Rosselet**
- GitHub: [@Frosselet](https://github.com/Frosselet)
```

## File 3 — replace `etkl/.htaccess` (old paths → 301 → iladub)

```apache
# # /etkl/
#
# MIGRATED 2026-07-01 → the iladub namespace root (https://w3id.org/iladub).
# Every former /etkl/* path now 301-redirects to its new home under /iladub/.
# See the /iladub/ entry for content negotiation.
#
# ## Contact
# François Rosselet
# GitHub username: Frosselet

Options +FollowSymLinks
RewriteEngine on

# 301 permanent redirects: old /etkl/* -> new /iladub/*  (most specific first)
RewriteRule ^iladub/holons/?$        https://w3id.org/iladub/etkl/holons [R=301,L]
RewriteRule ^iladub/hga-alignment/?$ https://w3id.org/iladub/hga-alignment [R=301,L]
RewriteRule ^hol/hga-alignment/?$    https://w3id.org/iladub/dec/hga-alignment [R=301,L]
RewriteRule ^risk/hga-alignment/?$   https://w3id.org/iladub/risk/hga-alignment [R=301,L]
RewriteRule ^iladub/?$               https://w3id.org/iladub [R=301,L]
RewriteRule ^hol/?$                  https://w3id.org/iladub/dec [R=301,L]
RewriteRule ^risk/?$                 https://w3id.org/iladub/risk [R=301,L]
RewriteRule ^governance-shapes/?$    https://w3id.org/iladub/governance-shapes [R=301,L]
RewriteRule ^$                       https://w3id.org/iladub/etkl [R=301,L]
# any other former /etkl/* subpath -> the new root
RewriteRule ^(.*)$                   https://w3id.org/iladub/ [R=301,L]
```

## File 4 — update `etkl/README.md`

Prepend a migration note to the existing `etkl/README.md`:

```markdown
> **Migrated 2026-07-01.** This namespace moved to the **iladub** root:
> [`https://w3id.org/iladub`](https://w3id.org/iladub). Every former `/etkl/*` IRI now
> 301-redirects to its new home under `/iladub/` (e.g. `/etkl/hol` → `/iladub/dec`,
> `/etkl/iladub` → `/iladub`, `/etkl` → `/iladub/etkl`). See the `/iladub/` entry.
```

---

## Submission steps

Run **after PR #19 merges to `iladub/iladub@main`** (so the RDF targets resolve):

```bash
# 1. Fork + clone perma-id/w3id.org
gh repo fork perma-id/w3id.org --clone --remote

# 2. On a branch, add the new iladub/ entry and rewrite the etkl/ entry
#    - create  iladub/.htaccess        (File 1)
#    - create  iladub/README.md        (File 2)
#    - replace etkl/.htaccess          (File 3)
#    - prepend etkl/README.md note     (File 4)

# 3. PR
gh pr create --repo perma-id/w3id.org \
  --title "Add /iladub namespace; migrate /etkl -> /iladub (301)" \
  --body "New persistent namespace root https://w3id.org/iladub (content-negotiated to \
github.com/iladub/iladub Turtle + iladub.dev). Supersedes the /etkl entry, whose paths now \
301-redirect to /iladub/*. Admin: @Frosselet (same as the existing /etkl entry)."
```

**Verify after merge:**
- `curl -sIL -H "Accept: text/turtle" https://w3id.org/iladub/dec` → 302 → the raw `dec.ttl`.
- `curl -sI https://w3id.org/iladub` → 302 → `https://iladub.dev/assertion-proposition/`.
- `curl -sI https://w3id.org/etkl/hol` → 301 → `https://w3id.org/iladub/dec`.
- `curl -sI https://w3id.org/etkl/iladub/holons` → 301 → `https://w3id.org/iladub/etkl/holons`.
```
