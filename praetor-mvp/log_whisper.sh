#!/bin/bash

# Input WAV file
INPUT_FILE=$1
FILENAME=$(basename "$INPUT_FILE" .wav)
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Output file for Whisper
OUTPUT_PATH=~/praetor/logs/${FILENAME}_transcript.txt

# Run Whisper CLI
cd ~/whisper.cpp/build
./bin/whisper-cli -m ../models/ggml-base.en.bin -f "$INPUT_FILE" --output-txt --output-file "$OUTPUT_PATH"

# Append to master log
echo "[$TIMESTAMP] File: $FILENAME.wav" >> ~/praetor/logs/praetor_log.txt
cat "${OUTPUT_PATH}.txt" >> ~/praetor/logs/praetor_log.txt
echo -e "\n---\n" >> ~/praetor/logs/praetor_log.txt
chmod +x ~/praetor/log_whisper.sh
exit


