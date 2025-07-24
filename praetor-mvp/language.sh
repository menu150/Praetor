#!/bin/bash

# === Settings ===
LOG_DIR="/home/menu150/praetor/logs"
WHISPER="/home/menu150/whisper.cpp/build/bin/whisper-cli"
MODEL="/home/menu150/whisper.cpp/models/ggml-base.en.bin"
BRAIN="/home/menu150/praetor/brain.py"

mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
AUDIO_FILE="$LOG_DIR/audio_${TIMESTAMP}.wav"
TXT_LOG="$LOG_DIR/log_${TIMESTAMP}.txt"
TRANSCRIPT_RAW="$LOG_DIR/transcript_${TIMESTAMP}.txt"

echo "[🎤] Recording..."
arecord -f cd -d 5 -q "$AUDIO_FILE"

echo "[🤖] Transcribing..."
"$WHISPER" -m "$MODEL" -f "$AUDIO_FILE" -otxt --output-file "$TRANSCRIPT_RAW" --no-prints

# Clean up transcription: remove timestamps, trim whitespace
TRANSCRIPTION=$(cat "$TRANSCRIPT_RAW" | sed -E 's/\[.*\]//g' | xargs)

echo "[🔍] Classifying..."
LABEL=$(python3 "$BRAIN" "$TRANSCRIPTION" --run)

echo "[🧾] Logging..."
{
  echo "timestamp: $TIMESTAMP"
  echo "transcription: $TRANSCRIPTION"
  echo "label: $LABEL"
  echo "audio_file: $AUDIO_FILE"
} > "$TXT_LOG"

echo "[✅] Logged: $LABEL - \"$TRANSCRIPTION\""
