#!/usr/bin/env bash

curl -s -H "Authorization: Bearer $GRAPHITE_USERID:$GRAPHITE_READ_KEY" "$GRAPHITE_ENDPOINT/render?target=m2ultra.sys.GPU&from=-3600s&to=-10s"
