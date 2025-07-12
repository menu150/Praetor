# Praetor

This repository hosts the Praetor assistant. Skills can be defined using JSON files in `skills/` or Python modules in `skills_py/`.

## New Voice Skill

A new Python skill `skills_py/voice_skill.py` combines recording, Whisper transcription and command routing in one place. Use triggers like "voice command" or "listen for command" to start recording.
