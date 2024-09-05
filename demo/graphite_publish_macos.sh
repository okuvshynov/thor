#!/usr/bin/env bash

interval=10
interval_ms=$((interval * 1000))

send_graphana() {
    tstamp=$(($(date +%s) / $interval * $interval))

    curl -X POST -H "Authorization: Bearer $GRAPHITE_USERID:$GRAPHITE_WRITE_KEY" -H "Content-Type: application/json" "$GRAPHITE_ENDPOINT/metrics" -d '[{
    "name": "m2ultra.sys.'$1'",
    "interval": '$interval',
    "value": '$2',
    "time": '$tstamp'
}]'
}

sudo powermetrics -i $interval_ms -s gpu_power,cpu_power | grep --line-buffered -E '^(GPU idle residency:|P[0-9]+-Cluster idle residency:)' | awk '{gsub("%", "", $NF); print $1, 1-$NF/100; system("")}' | while read -r key value; do
    send_graphana "$key" "$value"
done
