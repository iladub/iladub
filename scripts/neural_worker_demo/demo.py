"""Token, accuracy and wall-time comparison of four renderings of ONE NEURAL proposer.

A demonstration instrument for docs/superpowers/2026-09-17-neural-workers-evidence.md, not
production code; nothing in iladub imports it. It compares the shipped ProposeHeaderRowRoles with
three variants (baml_src/ beside this file) on a small model, and times sequential against
concurrent dispatch through BAML's generated async client.

THE INPUT IS HAND-BUILT and is the shipped prompt's OWN worked example (a graincorp-stem-like
header), so the comparison is tilted toward the baseline. It demonstrates techniques; it does not
evaluate a prompt. An evaluation needs recorded contexts and the oracle's verdict, which is the
subject of the handoff this file serves.

PROCEDURAL, justified: it calls models and counts; it makes no reading decision of its own.

USAGE, from a scratch directory (it generates a client, so never run it inside the repo):
  mkdir -p work/baml_src && cd work
  cp <repo>/baml_src/clients.baml <repo>/baml_src/header_rowrole.baml baml_src/
  cp <repo>/scripts/neural_worker_demo/baml_src/*.baml baml_src/
  printf 'generator python_client {\n output_type "python/pydantic"\n output_dir "../"\n version "0.222.0"\n}\n' > baml_src/generators.baml
  baml-cli generate --from baml_src
  OPENAI_API_KEY=... python <repo>/scripts/neural_worker_demo/demo.py [runs-per-variant]
"""

import asyncio
import collections
import os
import sys
import time

sys.path.insert(0, os.getcwd())

from baml_client.async_client import b  # noqa: E402
from baml_py import ClientRegistry, Collector  # noqa: E402

LEAF = ["Month", "Slot Reference Number", "Exporter", "Ship", "ETA of Ship", "Commencement",
        "ETD of Ship", "Received", "Received", "Accepted", "Accepted", "Status", "Load Port",
        "Commodity", "Tonnes"]
ROWS = [["Shipping Stem", "31/07/2026"],
        ["Date of Grain", "Date", "Time", "Date", "Time"],
        ["Unique", "Name Of", "Date", "Loading", "Date", "Nomination", "Nomination", "Nomination",
         "Nomination", "Nomination"]]
COLS = [[0, -1], [5, 7, 8, 9, 10], [1, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
TRUTH = ("Furniture", "Continuation", "Continuation")
MERGED = [[(f"{c} {LEAF[k]}" if k >= 0 else "") for c, k in zip(r, ks)] for r, ks in zip(ROWS, COLS)]
COUNTS = [len(r) for r in ROWS]


def row_major() -> str:
    """One line per header row: `fragment@column>label below`. Nothing is sent twice."""
    out = [f"labels[{len(LEAF)}]: " + "|".join(LEAF)]
    for i, (r, ks) in enumerate(zip(ROWS, COLS)):
        cells = " ; ".join(f"{c}@{k}" + (f">{LEAF[k]}" if k >= 0 else "") for c, k in zip(r, ks))
        out.append(f"r{i}[{len(r)}]: {cells}")
    return "\n".join(out)


def column_major() -> str:
    """One line per column: its stack top to bottom and the name that stack would compose."""
    by, out = collections.defaultdict(list), []
    for i, (r, ks) in enumerate(zip(ROWS, COLS)):
        for c, k in zip(r, ks):
            if k < 0:
                out.append(f'col -1: r{i} "{c}"')
            else:
                by[k].append((i, c))
    for k in sorted(by):
        stack = " / ".join(f"r{i} {c}" for i, c in by[k])
        out.append(f'col {k}: {stack} / {LEAF[k]} -> "{" ".join(c for _, c in by[k])} {LEAF[k]}"')
    return "\n".join(out)


VARIANTS = {
    "baseline": lambda o: b.ProposeHeaderRowRoles(ROWS, LEAF, COLS, MERGED, COUNTS, len(LEAF), baml_options=o),
    "outonly": lambda o: b.ProposeHeaderRowRolesOut(ROWS, LEAF, COLS, MERGED, COUNTS, len(LEAF), baml_options=o),
    "lean": lambda o: b.ProposeHeaderRowRolesLean(row_major(), len(ROWS), baml_options=o),
    "lean2": lambda o: b.ProposeHeaderRowRolesLean2(column_major(), len(ROWS), baml_options=o),
}


def registry(model: str) -> ClientRegistry:
    cr = ClientRegistry()
    cr.add_llm_client("M", "openai", {"model": model, "api_key": os.environ["OPENAI_API_KEY"], "max_tokens": 600})
    cr.set_primary("M")
    return cr


async def one(variant: str, cr: ClientRegistry):
    c = Collector()
    r = await VARIANTS[variant]({"collector": c, "client_registry": cr})
    roles = r.roles if hasattr(r, "roles") else r
    answer = tuple(str(getattr(x, "value", x)).capitalize() for x in roles)
    return answer, c.last.usage.input_tokens, c.last.usage.output_tokens


async def main() -> None:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    for model in ("gpt-4.1-nano", "gpt-4.1-mini"):
        cr = registry(model)
        for variant in VARIANTS:
            t = time.time()
            out = await asyncio.gather(*[one(variant, cr) for _ in range(n)])
            wall = time.time() - t
            tin, tout = sum(x[1] for x in out) / n, sum(x[2] for x in out) / n
            right = sum(x[0] == TRUTH for x in out)
            print(f"{model:13s} {variant:9s} in={tin:4.0f} out={tout:4.0f} correct={right}/{n} wall={wall:4.1f}s")
    cr = registry("gpt-4.1-mini")
    t = time.time()
    for _ in range(n):
        await one("outonly", cr)
    sequential = time.time() - t
    t = time.time()
    await asyncio.gather(*[one("outonly", cr) for _ in range(n)])
    concurrent = time.time() - t
    print(f"\n{n} outonly calls on mini: sequential {sequential:.1f}s | asyncio.gather {concurrent:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
