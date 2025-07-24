#!/bin/bash
cd "$(dirname "$0")"

echo "[🔁] Loading environment..."
source venv/bin/activate

echo "[🧠] Starting Praetor Brain..."
nohup python3 brain.py > logs/brain.log 2>&1 &

echo "[🖥️] Starting Dashboard..."
nohup npm run dev > logs/dashboard.log 2>&1 &

echo "[🌐] Launching Cloudflare Tunnel..."
nohup cloudflared tunnel run praetor > logs/tunnel.log 2>&1 &

# Add future always-on processes here:
# echo "[🗣️] Starting Voice Loop..."
# nohup python3 voice_loop.py > logs/voice.log 2>&1 &

echo "[✅] All Praetor services launched."
 
