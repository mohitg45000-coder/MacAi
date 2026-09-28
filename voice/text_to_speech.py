import subprocess


def speak(text):
    if not text:
        return

    print(f"🤖 jarvis: {text}")

    subprocess.run(
        ["say", text],
        check=False
    )
