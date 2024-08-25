#!/usr/bin/env bash

[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSE_SCRIPT="python $CURRENT_DIR/graphite_reader.py"

result="$(curl -s -H "Authorization: Bearer $GRAPHITE_USERID:$GRAPHITE_READ_KEY" "$GRAPHITE_ENDPOINT/render?target=test.metric&from=-1h" | $PARSE_SCRIPT)"
echo "$result"
