# w3id.org redirect configuration — iladub namespace migration

This is a **draft** of the redirect configuration to be submitted as a pull request to
[perma-id/w3id.org](https://github.com/perma-id/w3id.org) under the author's GitHub
account, where a w3id maintainer will merge it (as dgarijo merged the original `etkl`
entry in PR #6144). **This file is NOT yet submitted.**

The migration moves all semantic artifacts from `https://w3id.org/etkl/*` to
`https://w3id.org/iladub/*`. Two changes are required in the perma-id repo:

1. A new `iladub/.htaccess` entry (content negotiation for the new namespace).
2. Additions to the existing `etkl/.htaccess` (301 permanent redirects from every old path to its new equivalent, so dated links in published ontologies and citations continue to resolve).

**Redirect codes used:**
- `303 See Other` for RDF content-negotiation rules — the classic Linked Data convention
  (the IRI identifies a concept, not the document; 303 signals that you are being sent
  elsewhere for a representation of it).
- `301 Moved Permanently` for the old→new `etkl` → `iladub` redirects — the IRIs have
  genuinely moved; caches and crawlers should update.

---

## Block 1 — new `iladub/.htaccess`

This file lives at `w3id.org/iladub/.htaccess` in the perma-id repo. It handles
content negotiation for all nine ontology/shape paths plus the base IRI.

```apache
Options +FollowSymLinks
RewriteEngine on

# ---------------------------------------------------------------------------
# Base IRI: https://w3id.org/iladub
# Core epistemics ontology → iladub.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/iladub.ttl [QSA,R=303,L]

RewriteRule ^/?$ https://iladub.dev [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/etkl  — the ET(K)L method ontology → etkl.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^etkl/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/etkl.ttl [QSA,R=303,L]

RewriteRule ^etkl/?$ https://iladub.dev/etkl [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/dec  — decidability / decision-context ontology → dec.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^dec/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/dec.ttl [QSA,R=303,L]

RewriteRule ^dec/?$ https://iladub.dev/dec [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/risk  — contextual-risk ontology → risk.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^risk/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/risk.ttl [QSA,R=303,L]

RewriteRule ^risk/?$ https://iladub.dev/risk [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/etkl/holons  — holonic fabric ontology → etkl-holons.ttl
# (must come before bare ^etkl/?)
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^etkl/holons/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/etkl-holons.ttl [QSA,R=303,L]

RewriteRule ^etkl/holons/?$ https://iladub.dev/etkl/holons [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/hga-alignment  — iladub↔HGA alignment → iladub-hga-align.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^hga-alignment/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/iladub-hga-align.ttl [QSA,R=303,L]

RewriteRule ^hga-alignment/?$ https://iladub.dev/hga-alignment [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/dec/hga-alignment  — dec↔HGA alignment → dec-hga-align.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^dec/hga-alignment/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/dec-hga-align.ttl [QSA,R=303,L]

RewriteRule ^dec/hga-alignment/?$ https://iladub.dev/dec/hga-alignment [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/risk/hga-alignment  — risk↔HGA alignment → risk-hga-align.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^risk/hga-alignment/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/risk-hga-align.ttl [QSA,R=303,L]

RewriteRule ^risk/hga-alignment/?$ https://iladub.dev/risk/hga-alignment [QSA,R=303,L]

# ---------------------------------------------------------------------------
# https://w3id.org/iladub/governance-shapes  — governance SHACL shapes → governance-shapes.ttl
# ---------------------------------------------------------------------------
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} text/n3 [OR]
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [OR]
RewriteCond %{HTTP_ACCEPT} application/ld\+json
RewriteRule ^governance-shapes/?$ https://raw.githubusercontent.com/iladub/iladub/main/vocab/shapes/governance-shapes.ttl [QSA,R=303,L]

RewriteRule ^governance-shapes/?$ https://iladub.dev/governance-shapes [QSA,R=303,L]
```

---

## Block 2 — additions to the existing `etkl/.htaccess`

These rules are **prepended** to the existing `w3id.org/etkl/.htaccess`. They must
come before any existing content-negotiation rules so that old IRIs redirect permanently
to their new locations before any content negotiation fires. Most-specific (longest)
paths are listed first to prevent shorter patterns from swallowing them.

```apache
# ---------------------------------------------------------------------------
# 301 Permanent redirects: old etkl/* paths → new iladub/* paths
# (namespace migration; prepend to existing etkl/.htaccess content-neg rules)
# Most-specific paths first.
# ---------------------------------------------------------------------------

# /etkl/iladub/holons → /iladub/etkl/holons
RewriteRule ^iladub/holons/?$ https://w3id.org/iladub/etkl/holons [R=301,L]

# /etkl/iladub/hga-alignment → /iladub/hga-alignment
RewriteRule ^iladub/hga-alignment/?$ https://w3id.org/iladub/hga-alignment [R=301,L]

# /etkl/hol/hga-alignment → /iladub/dec/hga-alignment
RewriteRule ^hol/hga-alignment/?$ https://w3id.org/iladub/dec/hga-alignment [R=301,L]

# /etkl/risk/hga-alignment → /iladub/risk/hga-alignment
RewriteRule ^risk/hga-alignment/?$ https://w3id.org/iladub/risk/hga-alignment [R=301,L]

# /etkl/iladub → /iladub  (after the more-specific /iladub/holons and /iladub/hga-alignment)
RewriteRule ^iladub/?$ https://w3id.org/iladub [R=301,L]

# /etkl/hol → /iladub/dec
RewriteRule ^hol/?$ https://w3id.org/iladub/dec [R=301,L]

# /etkl/risk → /iladub/risk
RewriteRule ^risk/?$ https://w3id.org/iladub/risk [R=301,L]

# /etkl/governance-shapes → /iladub/governance-shapes
RewriteRule ^governance-shapes/?$ https://w3id.org/iladub/governance-shapes [R=301,L]

# /etkl → /iladub/etkl  (bare etkl path; must be last so it doesn't shadow sub-paths)
RewriteRule ^/?$ https://w3id.org/iladub/etkl [R=301,L]
```

---

## Submission checklist

- Fork `perma-id/w3id.org` (github.com/perma-id/w3id.org).
- Add the file `iladub/.htaccess` containing Block 1 above.
- Edit `etkl/.htaccess` to **prepend** Block 2 above (before any existing content-negotiation rules).
- Open a PR referencing this migration (mention PR #6144 for context and dgarijo as the prior approver).
- After the PR is merged by a w3id maintainer, verify the following:
  - RDF client resolves to the raw Turtle file: `curl -sI -H "Accept: text/turtle" https://w3id.org/iladub/dec` → `303 See Other` → `Location: https://raw.githubusercontent.com/iladub/iladub/main/vocab/ontology/dec.ttl`.
  - Browser redirect works: `curl -sI https://w3id.org/iladub` → `303 See Other` → `Location: https://iladub.dev`.
  - Old etkl path redirects permanently: `curl -sI https://w3id.org/etkl/hol` → `301 Moved Permanently` → `Location: https://w3id.org/iladub/dec`.
  - Spot-check a deep path: `curl -sI https://w3id.org/etkl/iladub/holons` → `301 Moved Permanently` → `Location: https://w3id.org/iladub/etkl/holons`.
