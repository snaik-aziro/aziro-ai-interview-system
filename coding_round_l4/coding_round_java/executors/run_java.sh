#!/bin/bash
set -e

# Read full stdin
INPUT="$(cat)"

if [ -z "$INPUT" ]; then
  echo '{"stdout":"","stderr":"No input received by Java executor","returncode":-1}'
  exit 0
fi

# Extract code
CODE=$(echo "$INPUT" | python3 -c '
import sys, json
print(json.loads(sys.stdin.read())["code"])
')

# Extract first arg (always string)
ARG=$(echo "$INPUT" | python3 -c '
import sys, json
args = json.loads(sys.stdin.read()).get("args", [])
print(args[0] if args else "")
')

# Write Java source
cat > Main.java <<EOF
$CODE
EOF

# Compile
if ! javac Main.java 2> compile_err.txt; then
  echo "{\"stdout\":\"\",\"stderr\":\"$(cat compile_err.txt)\",\"returncode\":1}"
  exit 0
fi

# Run
OUT=$(timeout 5 java Main "$ARG" 2> run_err.txt || true)

if [ -s run_err.txt ]; then
  echo "{\"stdout\":\"\",\"stderr\":\"$(cat run_err.txt)\",\"returncode\":2}"
else
  echo "{\"stdout\":\"$OUT\",\"stderr\":\"\",\"returncode\":0}"
fi
