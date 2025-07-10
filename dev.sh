#!/bin/bash
echo "[⚙️] Launching Praetor Development Environment..."

# Activate venv and run Flask (in background)
cd "$(dirname "$0")"
source venv/bin/activate
python3 api.py &

# Wait for port file
while [ ! -f .flask_port ]; do sleep 1; done
PORT=$(cat .flask_port)
echo "[✅] Flask started on port $PORT"

# Start Next.js
cd dashboard
npm run dev
