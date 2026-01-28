#!/bin/bash

PORT=$1

if [ -z "$PORT" ]; then
  echo "❌ Usage: ./start_hr_ui.sh <port>"
  exit 1
fi

echo "🚀 Starting HR UI on port $PORT"

export UI_PORT=$PORT
export AZIRO_STATE_DIR=/home/aziro/.aziro_state

# IMPORTANT: run streamlit from PROJECT ROOT
streamlit run src/app.py \
  --server.port $PORT \
  --server.address 0.0.0.0 \
  --server.headless true

