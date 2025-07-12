"""Voice skill integrating recording, transcription, and command routing."""

import os
import subprocess
from datetime import datetime

triggers = [
    "voice command",
    "listen for command",
    "voice mode"
]

def run(user_input: str):
    """Record audio, transcribe with Whisper, and pass to the brain."""
    log_dir = os.getenv("VOICE_LOG_DIR", "logs")
    whisper_cli = os.getenv("WHISPER_CLI", "/home/menu150/whisper.cpp/build/bin/whisper-cli")
    model_path = os.getenv("WHISPER_MODEL", "/home/menu150/whisper.cpp/models/ggml-base.en.bin")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    audio_file = os.path.join(log_dir, f"audio_{timestamp}.wav")
    transcript_file = os.path.join(log_dir, f"transcript_{timestamp}.txt")

    print("[🎤] Recording 5 seconds of audio...")
    subprocess.run(["arecord", "-f", "cd", "-d", "5", "-q", audio_file], check=True)

    print("[🤖] Transcribing...")
    subprocess.run([
        whisper_cli,
        "-m", model_path,
        "-f", audio_file,
        "-otxt",
        "--output-file", transcript_file,
        "--no-prints"
    ], check=True)

    with open(f"{transcript_file}.txt", "r") as f:
        transcription = f.read().replace("\n", " ").strip()

    print(f"[📝] Heard: {transcription}")

    import brain
    brain.handle_command(transcription)

    return {"action": "script", "path_or_command": ""}
