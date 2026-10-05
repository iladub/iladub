#!/bin/bash
# M4 diagnostic rerun (counterfactual only), serial.
S=${S:-$(cd "$(dirname "$0")" && pwd)/out}; mkdir -p "$S"
cd "/Volumes/WD Green/dev/git/iladub" || exit 1
unset BAML_LIVE ILADUB_RECORD_READINGS
.venv/bin/python $S/m4_counterfactual.py $S/m4-diag.json > $S/m4-diag.out 2> $S/m4-diag.err
echo "exit $?" >> $S/m4-diag.out
