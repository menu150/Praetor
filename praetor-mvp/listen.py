import pvporcupine
import pyaudio
import struct
import subprocess

porcupine = pvporcupine.create(
    access_key="mS0j9GTsvg84IjsLmMUffDMV3WujZKB3Rzz6DLxiy2QqY2Rs+M6pxw==",
    keyword_paths=["/home/menu150/praetor/praetor.ppn"]
)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("🎧 Praetor is listening...")

try:
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm) >= 0:
            print("👂 Wake word detected!")
            subprocess.run(["aplay", "/home/menu150/praetor/chime.wav"])
            subprocess.run(["bash", "/home/menu150/praetor/language.sh"])
except KeyboardInterrupt:
    print("Stopping...")
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()
import pvporcupine
import pyaudio
import struct
import subprocess
import os

porcupine = pvporcupine.create(
    access_key="mS0j9GTsvg84IjsLmMUffDMV3WujZKB3Rzz6DLxiy2QqY2Rs+M6pxw==",
    keyword_paths=["/home/menu150/praetor/praetor.ppn"]
)

import pvporcupine
import pyaudio
import struct
import subprocess
import os

porcupine = pvporcupine.create(
    access_key="mS0j9GTsvg84IjsLmMUffDMV3WujZKB3Rzz6DLxiy2QqY2Rs+M6pxw==",
    keyword_paths=["/home/menu150/praetor/praetor.ppn"]
)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

print("🎧 Praetor is now always listening...")

try:
    while True:
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        if porcupine.process(pcm) >= 0:
            print("👂 Wake word detected!")
            subprocess.run(["aplay", "/home/menu150/praetor/chime.wav"])
            subprocess.run(["bash", "/home/menu150/praetor/language.sh"])

except KeyboardInterrupt:
    print("Stopping listener.")
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()
