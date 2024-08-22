#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BG_SCRIPT="python3 $CURRENT_DIR/macos_local.py"

start_background_process() {
    if ! pgrep -f "$BG_SCRIPT" > /dev/null; then
        tmux new-session -d -s "thor_bg" "$BG_SCRIPT"
    fi
}

DATA_FILE="/tmp/thor_metric_$1_data"
get_status_data() {
    if [ -f "$DATA_FILE" ]; then
        cat "$DATA_FILE"
    else
        echo "N/A"
    fi
}

#start_background_process
get_status_data

