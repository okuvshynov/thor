#!/usr/bin/env bash

curl -s "http://studio.local:8087/plain" | grep '^gpu ' | awk '{print substr($0, 5)}'
