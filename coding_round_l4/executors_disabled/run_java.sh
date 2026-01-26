#!/bin/bash
set -e

read INPUT

CODE=$(echo "$INPUT" | jq -r '.code')
ARGS=$(echo "$INPUT" | jq -r '.args[0]')

# Write candidate code
echo "$CODE" > Main.java

# Compile
javac Main.java 2> compile_err.txt || {
  echo "{\"stdout\":\"\",\"stderr\":\"$(cat compile_err.txt)\",\"returncode\":1}"
  exit 0
}

# Run (pass STRING argument directly)
OUT=$(timeout 5 java Main "$ARGS" 2> run_err.txt || true)

if [ -s run_err.txt ]; then
  echo "{\"stdout\":\"\",\"stderr\":\"$(cat run_err.txt)\",\"returncode\":2}"
else
  echo "{\"stdout\":\"$OUT\",\"stderr\":\"\",\"returncode\":0}"
fi
