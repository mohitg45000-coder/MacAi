import subprocess


def speak(text):
    if not text:
        return

    print(f"🤖 Cortex: {text}")

    subprocess.run(
        ["say", text],
        check=False
    )
