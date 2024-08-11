#!/bin/bash

METRICS=$(curl -s http://localhost:8000/metrics)
echo "${METRICS}"
