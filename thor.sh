#!/bin/bash

GPU=$(curl -s http://localhost:8000/gpu/)
echo "${GPU}"
