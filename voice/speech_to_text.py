import speech_recognition as sr


def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {text}")
        return text.lower()

    except sr.UnknownValueError:
        print("❌ Could not understand.")
        return ""

    except sr.RequestError as e:
        print(f"❌ Speech service error: {e}")
        return ""