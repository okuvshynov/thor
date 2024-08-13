#!/bin/bash
URL="http://localhost:8000/?metric=gpu&metric=rss&metric=pcpu"
GPU=$(curl -s "$URL")
echo "${GPU}"
