#!/usr/bin/env bash

echo "$(awk 'BEGIN { srand(); for (i=1; i<=8; i++) printf "%.1f ", rand() }')"
