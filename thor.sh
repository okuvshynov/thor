#!/bin/bash

# Define colors
HELLO_FG="#[fg=colour231]" # White
HELLO_BG="#[bg=colour16]"  # Black
WORLD_FG="#[fg=colour40]"  # Green
WORLD_BG="#[bg=colour232]" # Dark Gray

METRICS=$(curl -s http://localhost:8000/metrics)

# Output the formatted string
echo "${HELLO_FG}${HELLO_BG}hello${WORLD_FG}${WORLD_BG}${METRICS}"
