#!/bin/bash

START_PORT=8701
END_PORT=8720

echo "🚀 Starting HR UIs from $START_PORT to $END_PORT"

for PORT in $(seq $START_PORT $END_PORT)
do
  echo "➡️  Starting HR UI on port $PORT"

  export AZIRO_SESSION_ID=$PORT
  export AZIRO_STATE_DIR=/home/aziro/.aziro_state

  nohup streamlit run src/app.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --server.headless true \
    > logs/hr_ui_$PORT.log 2>&1 &

  sleep 1
done

echo "✅ All HR UIs started successfully"
