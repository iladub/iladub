"""Does the PRIOR census's band count come from raw detect_bands rather than page_bands?

Prior reported: apple p0 8, p1 8, p2 8, bfs p5 15, ons p7 16, ons p8 9.
page_bands returns:       3,    3,    8,        15,       16,      9.

If raw detect_bands reproduces the prior figures where page_bands does not, the prior
census compared a PRE-MERGE band list against POST-MERGE region reports, and its
"no 1:1 correspondence" was an artefact of the band source, not a correspondence failure.

Gate classification (CLAUDE.md §8): PROCEDURAL. Reads two existing accountings, prints
both, decides nothing, carries no tolerance.
"""
import pathlib
import sys

sys.path.insert(0, "src")
from iladub.etkl.bands import detect_bands
from iladub.etkl.compile import page_bands
from iladub.etkl.geometry import extract_words, text_lines

PRIOR = {
    ("apple-fy2026q3-statements", 0): 8,
    ("apple-fy2026q3-statements", 1): 8,
    ("apple-fy2026q3-statements", 2): 8,
    ("bfs-population-bilan-2023", 5): 15,
    ("ons-index-of-services-2026-02", 7): 16,
    ("ons-index-of-services-2026-02", 8): 9,
    ("cbh-stem-2026-08-03", 0): 10,
}

pdfs = {p.stem: str(p) for p in pathlib.Path("corpus").rglob("*.pdf")}

print(f"{'document':<24}{'pg':>3}{'prior':>7}{'raw':>6}{'page_bands':>12}  explains?")
for (stem, pg), prior in PRIOR.items():
    path = pdfs[stem]
    lines = sorted([l for l in text_lines(extract_words(path, pg)) if l.words],
                   key=lambda l: l.top)
    raw = len(detect_bands(lines))
    pb = len(page_bands(path, pg))
    verdict = ("RAW matches prior" if raw == prior and pb != prior else
               "both match" if raw == prior and pb == prior else
               "page_bands matches" if pb == prior else
               "NEITHER matches prior")
    print(f"{stem[:23]:<24}{pg:>3}{prior:>7}{raw:>6}{pb:>12}  {verdict}")
