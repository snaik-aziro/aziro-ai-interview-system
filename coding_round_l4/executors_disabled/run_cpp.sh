#!/bin/bash
set -e

read INPUT
CODE=$(echo "$INPUT" | jq -r '.code')
ARGS=$(echo "$INPUT" | jq -r '.args | @json')

echo "$CODE" > solution.cpp

g++ solution.cpp -o solution.out 2> compile_err.txt || {
    echo "{\"stdout\": \"\", \"stderr\": \"$(cat compile_err.txt)\", \"returncode\": 1}"
    exit
}

OUT=$(timeout 5 ./solution.out "$ARGS" 2> run_err.txt) || true

if [ -s run_err.txt ]; then
    echo "{\"stdout\": \"\", \"stderr\": \"$(cat run_err.txt)\", \"returncode\": 2}"
else
    echo "{\"stdout\": \"$OUT\", \"stderr\": \"\", \"returncode\": 0}"
fi
