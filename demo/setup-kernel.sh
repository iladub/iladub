#!/usr/bin/env bash
# Set up an isolated env + Jupyter kernel for the ET(K)L showcase notebook.
# Deliberately baml-free: the ET(K)L compiler pipeline has no LLM dependency, so
# the version-skew issues around baml_client cannot occur here.
set -euo pipefail
cd "$(dirname "$0")/.."   # repo root

python3 -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -e ".[etkl,demo]"
.venv/bin/python -m ipykernel install --user \
    --name iladub-etkl --display-name "iladub · ETKL"

echo
echo "Done. Now:"
echo "  .venv/bin/jupyter lab demo/etkl_1a_showcase.ipynb"
echo "and select the kernel:  iladub · ETKL"
