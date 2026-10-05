#!/bin/bash
# M4: counterfactual then baseline control, strictly serial.
S=${S:-$(cd "$(dirname "$0")" && pwd)/out}; mkdir -p "$S"
cd "/Volumes/WD Green/dev/git/iladub" || exit 1
unset BAML_LIVE ILADUB_RECORD_READINGS
.venv/bin/python $S/m4_counterfactual.py $S/m4.json > $S/m4.out 2> $S/m4.err
echo "exit $?" >> $S/m4.out
M4_BASELINE=1 .venv/bin/python $S/m4_counterfactual.py $S/m4-baseline.json > $S/m4-baseline.out 2> $S/m4-baseline.err
echo "exit $?" >> $S/m4-baseline.out
