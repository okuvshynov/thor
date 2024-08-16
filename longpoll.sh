#!/bin/bash

# Path to the script that provides the status information
URL="http://localhost:8000/?metric=gpu&metric=rss&metric=wired&metric=pcpu&metric=ecpu"

# Function to set the new status
set_new_status() {
    tmux set-option -g status-right "$1"
    tmux refresh-client -S
}

curr_id=""

while true; do
    count=0
    output=$(curl -s "${URL}&last=${curr_id}")
    while read -r line; do
        if [[ $count -eq 0 ]]; then
            curr_id="$line"
        elif [[ $count -eq 1 ]]; then
            set_new_status "$line"
        fi
        ((count++))
    done <<< "$output"
done

