#!/bin/bash
S=${S:-$(cd "$(dirname "$0")" && pwd)/out}; mkdir -p "$S"
cd "/Volumes/WD Green/dev/git/iladub" || exit 1
unset ILADUB_RECORD_READINGS
export BAML_LIVE=1
export ANTHROPIC_API_KEY=$(zsh -c 'source ~/.zshrc >/dev/null 2>&1; printf %s "$ANTHROPIC_API_KEY"')
.venv/bin/python $S/m2_reader.py $S/bands.json $S/m2.jsonl > $S/m2.out 2> $S/m2.err
echo "exit $?" >> $S/m2.out
