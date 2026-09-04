"""The band-run COST census: how many contiguous runs of >=2 ruled bands the corpus
contains, and what page_bands costs per page today.

Spec: docs/superpowers/specs/2026-09-04-the-run-is-one-band-design.md § 3.5 — the
measurement that rejects "enumerate every contiguous run and let the oracle dispose"
(266 runs corpus-wide) in favour of a relation that prunes it to 14.
"""
import os
import sys
import glob
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pdfplumber  # noqa: E402

from iladub.etkl.compile import page_bands  # noqa: E402

tot_runs = 0
for pdf in sorted(glob.glob(os.path.join(_ROOT, "corpus", "*", "*.pdf"))):
    with pdfplumber.open(pdf) as d:
        n_pages = len(d.pages)
    for p in range(n_pages):
        t0 = time.time()
        bands = page_bands(pdf, p)
        dt = time.time() - t0
        ruled = [i for i, b in enumerate(bands) if b.rules]
        # maximal contiguous stretches of ruled bands, and every (i,j) run inside them
        stretches, cur = [], []
        for i, b in enumerate(bands):
            if b.rules:
                cur.append(i)
            else:
                if len(cur) >= 2:
                    stretches.append(cur)
                cur = []
        if len(cur) >= 2:
            stretches.append(cur)
        pairs = sum(len(s) * (len(s) - 1) // 2 for s in stretches)
        tot_runs += pairs
        print(f"{os.path.basename(pdf)[:28]:30} p{p} bands={len(bands):3} ruled={len(ruled):3} "
              f"maximal_ruled_stretches={[len(s) for s in stretches]} "
              f"all_contiguous_runs>=2={pairs:3} page_bands={dt:5.2f}s")
print("TOTAL contiguous runs of >=2 ruled bands over the corpus:", tot_runs)
