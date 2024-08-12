#!/bin/bash
# File to store the current state
STATE_FILE="/tmp/thor_state.txt"
# File to override the current state
OVERRIDE_FILE="/tmp/thor_override.txt"
# Possible values to rotate between
VALUES=("gpu" "ecpu" "pcpu")
# Check if the override file exists
if [ -f "$OVERRIDE_FILE" ]; then
  CURRENT_STATE=$(cat "$OVERRIDE_FILE")
else
  # Read the current state from the state file
  if [ -f "$STATE_FILE" ]; then
    CURRENT_STATE=$(cat "$STATE_FILE")
  else
    CURRENT_STATE="gpu"
  fi
  # Find the index of the current state in the array
  CURRENT_INDEX=-1
  for i in "${!VALUES[@]}"; do
    if [ "${VALUES[$i]}" == "$CURRENT_STATE" ]; then
      CURRENT_INDEX=$i
      break
    fi
  done
  # Calculate the next state index
  NEXT_INDEX=$(( (CURRENT_INDEX + 1) % ${#VALUES[@]} ))
  NEXT_STATE=${VALUES[$NEXT_INDEX]}
  # Write the next state back to the file
  echo "$NEXT_STATE" > "$STATE_FILE"
fi
# Query the appropriate URL based on the current state
URL="http://localhost:8000/${CURRENT_STATE}/"
GPU=$(curl -s "$URL")
echo "${GPU}"
