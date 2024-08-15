#!/bin/bash

# Path to the script that provides the status information
URL="http://localhost:8000/?metric=gpu&metric=rss&metric=wired"

# Function to get the current status
get_current_status() {
    tmux show-options -gqv status-right
}

# Function to set the new status
set_new_status() {
    tmux set-option -g status-right "$1"
    tmux refresh-client -S
}

# Initial status
current_status=$(get_current_status)

while true; do
    # Get the new status from the script
    new_status=$(curl -s "$URL")

    # Compare the new status with the current status
    if [ "$new_status" != "$current_status" ]; then
       # Update the status if it has changed
       set_new_status "$new_status"
       current_status="$new_status"
    fi

    # Wait for a short period before checking again
    sleep 0.1
done

