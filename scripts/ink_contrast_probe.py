"""ink_contrast_probe — per-glyph contrast against the surface painted behind it.

Measurement only. Reads nothing the pipeline reads, writes nothing, decides nothing: it exists so
that R213's colour discriminator, and every alternative to it, can be argued from figures rather
than from a chosen constant. See docs/superpowers/2026-09-17-unshown-ink-evidence.md, which quotes
this script's output verbatim.

  ./.venv/bin/python scripts/ink_contrast_probe.py           'corpus/*/*.pdf'   # WCAG ratio census
  ./.venv/bin/python scripts/ink_contrast_probe.py --gap     'corpus/*/*.pdf'   # luminance-gap band
  ./.venv/bin/python scripts/ink_contrast_probe.py --palette <one.pdf>          # ink/backdrop census

Containment rule (it differs from the throwaway probe R213 recorded, and the difference shows in
the band width): a char sits on the TOPMOST filled rect whose box contains the char's CENTRE; a
char on no filled rect is scored against white.
"""
from __future__ import annotations

import glob
import sys
from collections import Counter, defaultdict

import pdfplumber

WHITE = (1.0, 1.0, 1.0)
WCAG_LARGE_TEXT = 3.0   # WCAG 2.2 SC 1.4.3 minimum for large text — CITED, not chosen. E2 refutes it.
WCAG_BODY_TEXT = 4.5


def rgb(c):
    """pdfplumber colour -> (r, g, b) in 0..1, or None when unreadable."""
    if c is None:
        return None
    if isinstance(c, (int, float)):
        return (float(c),) * 3
    t = tuple(float(x) for x in c)
    if len(t) == 1:
        return (t[0],) * 3
    if len(t) == 3:
        return t
    if len(t) == 4:                     # naive CMYK -> RGB; adequate for a census
        c_, m, y, k = t
        return (1 - min(1, c_ + k), 1 - min(1, m + k), 1 - min(1, y + k))
    return None


def lin(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(c):
    r, g, b = c
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def ratio(fg, bg):
    hi, lo = max(lum(fg), lum(bg)), min(lum(fg), lum(bg))
    return (hi + 0.05) / (lo + 0.05)


def backdrop(ch, rects):
    """Topmost filled rect containing the char's centre, or None."""
    cx, cy = (ch["x0"] + ch["x1"]) / 2.0, (ch["top"] + ch["bottom"]) / 2.0
    best = None
    for r in rects:
        if r["x0"] <= cx <= r["x1"] and r["top"] <= cy <= r["bottom"]:
            best = r
    return best


def glyphs(path):
    """(page, text, fg, bg, on_rect) for every non-space char of every page."""
    with pdfplumber.open(path) as pdf:
        for pi, page in enumerate(pdf.pages):
            rects = [r for r in page.rects if r.get("fill")]
            for ch in page.chars:
                if not ch["text"].strip():
                    continue
                r = backdrop(ch, rects)
                yield (pi, ch["text"], rgb(ch.get("non_stroking_color")),
                       rgb(r.get("non_stroking_color")) if r else WHITE, r is not None)


def segmentation(path):
    """Per page, word counts with and without extra_attrs=['non_stroking_color'] (E4)."""
    out = []
    with pdfplumber.open(path) as pdf:
        for pi, page in enumerate(pdf.pages):
            kw = dict(use_text_flow=False, keep_blank_chars=False)
            out.append((pi, len(page.extract_words(**kw)),
                        len(page.extract_words(extra_attrs=["non_stroking_color"], **kw))))
    return out


def census(paths):
    for p in paths:
        rows = list(glyphs(p))
        seg = segmentation(p)
        on = [r for r in rows if r[4] and r[2] and r[3]]
        rat = {id(r): ratio(r[2], r[3]) for r in on}
        lo3 = [r for r in on if rat[id(r)] < WCAG_LARGE_TEXT]
        lo45 = [r for r in on if rat[id(r)] < WCAG_BODY_TEXT]
        vals = sorted(rat.values())
        print(f"\n== {p.split('/')[-1]}  pages={len(seg)} chars={len(rows)}")
        print(f"   word-seg differs on {len([s for s in seg if s[1] != s[2]])}/{len(seg)} pages: "
              f"{[s for s in seg if s[1] != s[2]]}")
        print(f"   colour unreadable: {len([r for r in rows if not r[2] or not r[3]])}")
        print(f"   on a filled rect: {len(on)}  | ratio<3: {len(lo3)}  ratio<4.5: {len(lo45)}")
        print(f"   off any rect: {len([r for r in rows if not r[4]])}")
        if vals:
            best = max(((vals[i] - vals[i - 1], (vals[i - 1], vals[i]))
                        for i in range(1, len(vals))), default=(0, None))
            print(f"   on-rect ratio min={round(vals[0], 4)} max={round(vals[-1], 4)}")
            print(f"   largest on-rect gap: ({round(best[0], 4)}, "
                  f"{None if best[1] is None else (round(best[1][0], 4), round(best[1][1], 4))})")
        if lo3:
            print(f"   glyphs under 3:1 -> {Counter(r[1] for r in lo3).most_common(8)}")
            print(f"   their fg/bg sample: {lo3[0][2]} on {lo3[0][3]}  "
                  f"ratio={round(rat[id(lo3[0])], 4)}")


def gap_band(paths):
    rows = [(p.split("/")[-1], pi, t, abs(lum(fg) - lum(bg)), onr)
            for p in paths for (pi, t, fg, bg, onr) in glyphs(p) if fg and bg]
    on = [r for r in rows if r[4]]
    vals = sorted(r[3] for r in on)
    best = max(((vals[i] - vals[i - 1], (vals[i - 1], vals[i])) for i in range(1, len(vals))),
               default=(0, None))
    lo = [r for r in on if r[3] <= 0.0065]
    off = sorted(r[3] for r in rows if not r[4])
    print(f"chars on a filled rect: {len(on)}   all chars: {len(rows)}")
    print(f"min gap {round(vals[0], 5)} max {round(vals[-1], 5)}")
    print(f"largest empty band: {round(best[0], 5)} "
          f"{None if best[1] is None else (round(best[1][0], 5), round(best[1][1], 5))}")
    print(f"gap<=0.0065: {len(lo)} docs: {sorted({(r[0], r[1]) for r in lo})}")
    print(f"their glyphs: {Counter(r[2] for r in lo).most_common(5)}")
    print(f"next 5 sorted gaps above that: {[round(v, 4) for v in vals if v > 0.0065][:5]}")
    print(f"off-rect gap min {round(off[0], 5)} count under 0.2: {sum(1 for v in off if v < 0.2)}")


def palette(path):
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[0]
        rects = [r for r in page.rects if r.get("fill")]
        print("filled rect fills:",
              Counter(rgb(r.get("non_stroking_color")) for r in rects).most_common())
        by = defaultdict(Counter)
        for (_pi, _t, fg, bg, _onr) in glyphs(path):
            by[bg][fg] += 1
        print()
        for bg, c in by.items():
            print("backdrop", bg, "-> glyph colours", c.most_common())
        print()
        # H1, per ink colour rather than as one boolean: "is a glyph painted in a colour the
        # author uses to PAINT areas with?" A single yes/no over the page answers a different
        # question and reads as confirmation — the per-colour table is what E3 argues from.
        fills = {rgb(r.get("non_stroking_color")) for r in rects}
        strokes = {rgb(r.get("stroking_color")) for r in rects}
        print("H1 per ink colour — is it also a rect FILL / a rect STROKE?")
        for bg, c in by.items():
            for fg, n in c.most_common():
                print(f"   ink {fg} x{n} on {bg}: fill={fg in fills} stroke={fg in strokes}")
        print("rect stroke colours:",
              Counter(rgb(r.get("stroking_color")) for r in rects).most_common())


if __name__ == "__main__":
    args = sys.argv[1:]
    mode = "census"
    if args and args[0] in ("--gap", "--palette"):
        mode, args = args[0].lstrip("-"), args[1:]
    paths = sorted(q for a in args for q in glob.glob(a))
    if not paths:
        sys.exit("usage: ink_contrast_probe.py [--gap|--palette] <pdf glob>")
    if mode == "gap":
        gap_band(paths)
    elif mode == "palette":
        palette(paths[0])
    else:
        census(paths)
