import pvporcupine
import pyaudio
import struct
import subprocess
import os

porcupine = pvporcupine.create(keywords=["computer"])  # We'll customize this next

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
            chime = os.path.expanduser("~/praetor/chime.wav")
            script = os.path.expanduser("~/praetor/language.sh")
            subprocess.run(["aplay", chime], check=True)
            subprocess.run(["bash", script], check=True)

except KeyboardInterrupt:
    print("Stopping listener.")
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
    porcupine.delete()
