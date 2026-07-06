# ET(K)L increment-1a showcase

`etkl_1a_showcase.ipynb` runs the deterministic layout+grid engine on a synthetic lab report and
**shows each step visually** — because the semantic structure of a human document lives in its 2-D
geometry, and increment 1a's job is to *measure* that geometry and make it explicit, with **no model
calls**.

Pipeline shown: `extract_words → text_lines → detect_bands → infer_leaf_grid`
(geometry in points → rows → layout bands → column grid + confidence).

## Run it

One-time setup (creates an isolated `.venv`, installs deps, registers a Jupyter kernel):

```bash
./demo/setup-kernel.sh
```

Then open the notebook and select the **`iladub · ETKL (1a)`** kernel:

```bash
.venv/bin/jupyter lab demo/etkl_1a_showcase.ipynb
```

The notebook ships already-executed (figures embedded), so it also reads fine on GitHub without running.

## Notes on the environment

- The engine and this demo have **no LLM / baml dependency**, so the `baml-py` version-skew that affects
  the full test suite in a mismatched venv cannot occur here.
- Deps: `pip install -e ".[etkl,demo]"` (pdfplumber + numpy for the engine; matplotlib + pypdfium2 +
  jupyterlab + ipykernel for the notebook).
- Files: `etkl_demo_data.py` (synthetic PDF), `etkl_viz.py` (matplotlib overlays — kept out of the notebook
  so its cells stay about the *pipeline*, not plotting).
