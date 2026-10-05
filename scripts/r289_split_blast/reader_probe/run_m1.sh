#!/bin/bash
# M1: one document per process, strictly serial.
S=${S:-$(cd "$(dirname "$0")" && pwd)/out}; mkdir -p "$S"
cd "/Volumes/WD Green/dev/git/iladub" || exit 1
rm -f $S/m1.done
for pair in cbh:ag-trade/cbh-stem-2026-08-03.pdf gstem:ag-trade/graincorp-stem-2026-07-31.pdf gcap:ag-trade/graincorp-capacity-2026-08-04.pdf ons:gov-stats/ons-index-of-services-2026-02.pdf bfs:gov-stats/bfs-population-bilan-2023.pdf apple:financial/apple-fy2026q3-statements.pdf who:health/who-wfa-boys-zscore-0-5.pdf; do
  name=${pair%%:*}; doc=${pair#*:}
  echo "=== $name $(date +%T)" >> $S/m1.log
  .venv/bin/python $S/harness_m1.py "$doc" $S/m1-$name.jsonl > $S/m1-$name.out 2> $S/m1-$name.err
  echo "exit $? $(date +%T)" >> $S/m1.log
done
touch $S/m1.done
