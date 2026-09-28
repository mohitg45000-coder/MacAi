import time
import subprocess
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

model = Model(wakeword_models=["hey_jarvis"])

print("🤖 Jarvis wake-word test started")
print("🎤 Say: Hey Jarvis")
print("Press Ctrl+C to stop.\n")


def callback(indata, frames, time_info, status):
    if status:
        print(status)

    audio = (indata[:, 0] * 32767).astype(np.int16)

    prediction = model.predict(audio)

    score = prediction.get("hey_jarvis", 0)

    if score > 0.5:
        print(f"\n🔥 WAKE WORD DETECTED! Score: {score:.2f}")
        print("🤖 Jarvis activated!")

        subprocess.run(
            ["say", "Yes, I am listening."],
            check=False
        )


try:
    with sd.InputStream(
        samplerate=16000,
        channels=1,
        dtype="float32",
        blocksize=1280,
        callback=callback
    ):
        while True:
            time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Wake-word test stopped.")