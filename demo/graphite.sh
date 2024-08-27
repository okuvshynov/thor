#!/usr/bin/env bash

curl -s -H "Authorization: Bearer $GRAPHITE_USERID:$GRAPHITE_READ_KEY" "$GRAPHITE_ENDPOINT/render?target=test2.metric&from=-3600s"
