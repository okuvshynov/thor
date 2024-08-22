#!/usr/bin/env bash

# here we replace the placeholders with entry scripts.
# each entry script might kick off background process to collect
# data.

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

thor_placeholders=(
    "\#{thor_ecpu}"
    "\#{thor_pcpu}"
    "\#{thor_gpu}"
    "\#{thor_rss}"
    "\#{thor_wired}"
    "\#{thor_cpu}"
)

thor_commands=(
    "#($CURRENT_DIR/scripts/metric.sh ecpu)"
    "#($CURRENT_DIR/scripts/metric.sh pcpu)"
    "#($CURRENT_DIR/scripts/metric.sh gpu)"
    "#($CURRENT_DIR/scripts/metric.sh rss)"
    "#($CURRENT_DIR/scripts/metric.sh wired)"
    "#($CURRENT_DIR/scripts/metric.sh cpu)"
)

do_expand() {
    local res="$1"
    for ((i = 0; i < ${#thor_commands[@]}; i++)); do
    	res=${res//${thor_placeholders[$i]}/${thor_commands[$i]}}
    done
    echo "$res"
}

update_tmux_option() {
    local option
    local option_value
    local new_option_value
    option=$1
    option_value="$(tmux show-option -gqv "$option")"
    new_value=$(do_expand "$option_value")
    tmux set-option -gq "$option" "$new_value"
}

update_tmux_option "status-right"
update_tmux_option "status-left"
