import os
import time
import threading

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from tools.apps import open_app, close_app
from voice.text_to_speech import speak
from voice.speech_to_text import listen
from tools.files import (
    list_files,
    create_folder,
    copy_file,
    move_file,
    search_files,
    get_file_info,
    read_text_file,
    rename_file
)

from tools.terminal import execute_command, close_running_apps


# ==========================================
# MAIN LOOP
# ==========================================

def main():

    print("\n================================")
    print("        🤖 Jarvis")
    print("================================")
    print("Type 'help' to see available commands.")
    print("Type 'exit' to quit.\n")


    # Local wake-word mode.
    # Jarvis stays idle and listens only for "Hey Jarvis".
    wake_model = Model(wakeword_models=["hey_jarvis"])
    wake_event = threading.Event()
    wake_score = {"value": 0.0}

    def wake_callback(indata, frames, time_info, status):
        if status:
            print(status)

        audio = (indata[:, 0] * 32767).astype(np.int16)
        prediction = wake_model.predict(audio)
        score = prediction.get("hey_jarvis", 0.0)

        if score > 0.5:
            wake_score["value"] = score
            wake_event.set()

    voice_mode = True
    active_voice = False

    print("🎤 Wake-word mode is active.")
    print("Say: Hey Jarvis")
    print("Press Ctrl+C to stop.\\n")

    while True:

        try:
            # ============================
            # INPUT MODE
            # ============================

            if voice_mode:

                # First activation: wait for "Hey Jarvis".
                if not active_voice:
                    print("🟢 Waiting for 'Hey Jarvis'...")

                    wake_event.clear()
                    wake_score["value"] = 0.0

                    with sd.InputStream(
                        samplerate=16000,
                        channels=1,
                        dtype="float32",
                        blocksize=1280,
                        callback=wake_callback
                    ):
                        while not wake_event.is_set():
                            time.sleep(0.05)

                    score = wake_score["value"]
                    print(f"\\n🔥 Wake word detected! Score: {score:.2f}")

                    wake_model.reset()
                    active_voice = True
                    speak("Yes, I am listening.")

                # After activation, listen directly for commands.
                voice_command = listen()

                if not voice_command:
                    speak("Sorry, I could not understand.")
                    continue

                user_input = voice_command.strip()

            else:
                user_input = input("Jarvis > ").strip()

            if not user_input:
                continue

            # ============================
            # VOICE MODE CONTROLS
            # ============================

            command_lower = user_input.lower().strip()

            if command_lower in [
                "jarvis stop listening",
                "stop listening",
                "jarvis stop",
                "stop"
            ]:
                voice_mode = False
                active_voice = False
                speak("Voice mode stopped. You can type commands.")
                continue

            if command_lower in [
                "jarvis exit",
                "exit",
                "quit"
            ]:
                print("Goodbye 👋")
                speak("Goodbye.")
                break

            if command_lower in ["voice", "listen"]:
                voice_mode = True
                active_voice = False
                speak("Voice mode activated.")
                continue

            if command_lower == "test voice":
                speak("Hello, I am Jarvis")
                continue
            # ==================================
            # HELP
            # ==================================

            elif user_input.lower() == "help":

                print("""
Available Commands:

APP:
    open <app>
    close <app>

FILES:
    list <folder>
    mkdir <folder>
    copy <source> -> <destination>
    move <source> -> <destination>
    search <keyword> -> <folder>
    info <file>
    read <file>
    rename <old_path> -> <new_name>

TERMINAL:
    run <command>

SYSTEM:
    sleep
    shutdown
    reboot / restart
    exit
                """)


            # ==================================
            # OPEN APP
            # ==================================

            elif user_input.lower().startswith("open "):

                app_name = user_input[5:].strip()

                result = open_app(app_name)
                speak(f"{app_name} opened.")


            # ==================================
            # CLOSE APP
            # ==================================

            elif user_input.lower().startswith("close "):

                app_name = user_input[6:].strip()

                if app_name.lower() in ["all apps", "all"]:
                    result = close_running_apps()

                    if result.get("still_running"):
                        speak("Some applications could not be closed.")
                    else:
                        speak("All apps closed.")
                else:
                    result = close_app(app_name)

                    if result.get("success", True):
                        speak(f"{app_name} closed.")
                    else:
                        speak(f"I could not close {app_name}.")


            # ==================================
            # LIST FILES
            # ==================================

            elif user_input.lower().startswith("list "):

                folder = user_input[5:].strip()

                if folder.lower() == "desktop":
                    folder = os.path.expanduser("~/Desktop")

                result = list_files(folder)

                if not result["success"]:

                    print("❌", result["message"])
                    continue

                print(f"\n📂 {result['path']}")

                for item in result["items"]:

                    icon = (
                        "📁"
                        if item["type"] == "folder"
                        else "📄"
                    )

                    print(
                        f"{icon} {item['name']}"
                    )

                speak(f"{len(result['items'])} items found.")


            # ==================================
            # CREATE FOLDER
            # ==================================

            elif user_input.lower().startswith("mkdir "):

                folder = user_input[6:].strip()

                result = create_folder(folder)

                print(result)
                speak(f"Folder {folder} created.")


            # ==================================
            # COPY
            # ==================================

            elif user_input.lower().startswith("copy "):

                command = user_input[5:]
                command = command.replace("to", "->")

                if "->" not in command:

                    print(
                        "❌ Use: copy <source> -> <destination>"
                    )
                    continue

                source, destination = command.split(
                    "->",
                    1
                )

                source = source.strip()
                destination = destination.strip()

                result = copy_file(
                    source,
                    destination
                )

                print(result)
                speak("File copied successfully.")


            # ==================================
            # MOVE
            # ==================================

            elif user_input.lower().startswith("move "):

                command = user_input[5:]
                command = command.replace("to", "->")

                if "->" not in command:

                    print(
                        "❌ Use: move <source> -> <destination>"
                    )
                    continue

                source, destination = command.split(
                    "->",
                    1
                )

                source = source.strip()
                destination = destination.strip()

                result = move_file(
                    source,
                    destination
                )

                print(result)
                speak("File moved successfully.")

            # ==================================
            # SEARCH
            # ==================================

            elif user_input.lower().startswith("search "):

                command = user_input[7:]
                command = command.replace("in", "->")

                if "->" not in command:

                    print(
                        "❌ Use: search <keyword> -> <folder>"
                    )
                    continue

                keyword, folder = command.split(
                    "->",
                    1
                )

                keyword = keyword.strip()
                folder = folder.strip()

                if folder.lower() == "desktop":
                    folder = os.path.expanduser("~/Desktop")

                result = search_files(
                    folder,
                    keyword
                )

                if not result["success"]:

                    print("❌", result["message"])
                    continue

                if not result["results"]:

                    print("No matching files found.")
                    continue

                print("\n🔎 Search Results:")

                for item in result["results"]:

                    icon = (
                        "📁"
                        if item["type"] == "folder"
                        else "📄"
                    )

                    print(
                        f"{icon} {item['path']}"
                    )

                speak(f"{len(result['results'])} matching files found.")


            # ==================================
            # FILE INFO
            # ==================================

            elif user_input.lower().startswith("info "):

                file_path = user_input[5:].strip()

                result = get_file_info(file_path)

                print(result)
                speak("File information retrieved.")


            # ==================================
            # READ FILE
            # ==================================

            elif user_input.lower().startswith("read "):

                file_path = user_input[5:].strip()

                result = read_text_file(file_path)


                if not result["success"]:

                    print("❌", result["message"])
                    continue

                print("\n📄 File Content:")
                print("--------------------------------")

                print(result["content"])

                print("--------------------------------")
                speak("File content retrieved successfullys.")


            # ==================================
            # RENAME
            # ==================================

            elif user_input.lower().startswith("rename "):

                command = user_input[7:]
                command = command.replace("to", "->")
                command = command.replace("2", "->")
            

                if "->" not in command:
                    print(
                        "❌ Use: rename <old_path> -> <new_name>"
                    )
                    continue

                old_path, new_name = command.split(
                    "->",
                    1
                )

                old_path = old_path.strip()
                new_name = new_name.strip()

                result = rename_file(
                    old_path,
                    new_name
                )

                print(result)
                speak(f"File renamed to {new_name}")


            # ==================================
            # SHUTDOWN MAC
            # ==================================

            elif user_input.lower() == "shutdown":

                result = execute_command("shutdown")

                if result["success"]:
                    print("\n🔌 Mac is shutting down.")
                    speak("Mac is shutting down.")
                else:
                    print("\n❌ Shutdown failed.")

                    if result.get("message"):
                        print(result["message"])

                    if result.get("stderr"):
                        print("\nError:")
                        print(result["stderr"])


            # ==================================
            # RESTART MAC
            # ==================================

            elif user_input.lower() in {"reboot", "restart"}:

                result = execute_command("reboot")

                if result["success"]:
                    print("\n🔄 Mac is restarting.")
                    speak("Mac is restarting.")
                else:
                    print("\n❌ Restart failed.")

                    if result.get("message"):
                        print(result["message"])

                    if result.get("stderr"):
                        print("\nError:")
                        print(result["stderr"])


            # ==================================
            # SLEEP MAC
            # ==================================

            elif user_input.lower() == "sleep":

                result = execute_command("sleep")

                if result["success"]:
                    print("\n😴 Mac is going to sleep.")
                    speak("Mac is going to sleep.")
                else:
                    print("\n❌ Sleep failed.")

                    if result.get("message"):
                        print(result["message"])

                    if result.get("stderr"):
                        print("\nError:")
                        print(result["stderr"])


            # ==================================
            # TERMINAL COMMAND
            # ==================================

            elif user_input.lower().startswith("run "):

                command = user_input[4:].strip()

                if not command:

                    print(
                        "❌ Please provide a command."
                    )
                    continue

                result = execute_command(
                    command
                )


                if result["success"]:

                    print("\n✅ Command executed.")

                    if result.get("stdout"):

                        print("\nOutput:")
                        print("--------------------------------")
                        print(result["stdout"])
                        print("--------------------------------")
                    speak("Command executed successfully.")

                else:

                    print("\n❌ Command failed.")

                    if result.get("message"):

                        print(result["message"])

                    if result.get("stderr"):

                        print("\nError:")
                        print(result["stderr"])


            # ==================================
            # UNKNOWN COMMAND
            # ==================================

            else:

                print(
                    "❌ Unknown command."
                )

                print(
                    "Type 'help' to see available commands."
                )


        except KeyboardInterrupt:

            print("\n\nGoodbye 👋")
            break


        except Exception as e:

            print(
                f"\n❌ Unexpected error: {e}"
            )


# ==========================================
# PROGRAM START
# ==========================================

if __name__ == "__main__":

    main()