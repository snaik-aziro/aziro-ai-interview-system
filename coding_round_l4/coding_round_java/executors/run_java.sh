#!/bin/bash

# DO NOT use `set -e` (breaks repeated runs)

# -------------------------------
# Create isolated temp workspace
# -------------------------------
WORKDIR=$(mktemp -d)
trap "rm -rf $WORKDIR" EXIT

cd "$WORKDIR" || exit 1

# -------------------------------
# Read full stdin
# -------------------------------
INPUT="$(cat)"

if [ -z "$INPUT" ]; then
  echo '{"stdout":"","stderr":"No input received by Java executor","returncode":-1}'
  exit 0
fi

# -------------------------------
# Extract code
# -------------------------------
CODE=$(echo "$INPUT" | python3 - <<EOF
import sys, json
print(json.loads(sys.stdin.read())["code"])
EOF
)

# -------------------------------
# Extract args (string only)
# -------------------------------
ARG=$(echo "$INPUT" | python3 - <<EOF
import sys, json
args = json.loads(sys.stdin.read()).get("args", [])
print(args[0] if args else "")
EOF
)

# -------------------------------
# Write Java source
# -------------------------------
cat > Main.java <<EOF
$CODE
EOF

# -------------------------------
# Compile
# -------------------------------
if ! javac Main.java 2> compile_err.txt; then
  ERR=$(sed 's/"/\\"/g' compile_err.txt)
  echo "{\"stdout\":\"\",\"stderr\":\"$ERR\",\"returncode\":1}"
  exit 0
fi

# -------------------------------
# Run with timeout (safe)
# -------------------------------
OUT=$(timeout 5s java Main "$ARG" 2> run_err.txt)
RC=$?

if [ $RC -ne 0 ] && [ -s run_err.txt ]; then
  ERR=$(sed 's/"/\\"/g' run_err.txt)
  echo "{\"stdout\":\"\",\"stderr\":\"$ERR\",\"returncode\":2}"
  exit 0
fi

# -------------------------------
# Success
# -------------------------------
OUT_ESCAPED=$(echo "$OUT" | sed 's/"/\\"/g')
echo "{\"stdout\":\"$OUT_ESCAPED\",\"stderr\":\"\",\"returncode\":0}"
