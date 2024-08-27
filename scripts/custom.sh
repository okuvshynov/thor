#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSE_SCRIPT="python $CURRENT_DIR/custom.py"

result="$("$@")"
echo "$result" | $PARSE_SCRIPT
