"""Synthetic contract set generator (spec 2026-10-31). Licence: Apache-2.0.

Justified PROCEDURAL (CLAUDE.md § 8): this package MAKES documents; it never reads one to
decide anything. Its jitter/noise constants are generation parameters, not reading
tolerances. The only reads are raw extraction (template text) and decidable exact matching of
strings the generator itself wrote. No generator function may be called from a reader."""
