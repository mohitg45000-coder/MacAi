from tools.apps import open_app, close_app
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

from tools.terminal import execute_command


# ==========================================
# MAIN LOOP
# ==========================================

def main():

    print("\n================================")
    print("        🤖 MacAI Assistant")
    print("================================")
    print("Type 'help' to see available commands.")
    print("Type 'exit' to quit.\n")


    while True:

        try:
            user_input = input("MacAI > ").strip()

            if not user_input:
                continue

            # ============================
            # VOICE COMMAND
            # ============================

            if user_input.lower() in ["voice", "listen"]:
                voice_command = listen()

                if voice_command:
                    user_input = voice_command
                else:
                    continue

            # ============================
            # EXIT
            # ============================
            if user_input.lower() == "exit":

                print("Goodbye 👋")
                break


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

                print(result)


            # ==================================
            # CLOSE APP
            # ==================================

            elif user_input.lower().startswith("close "):

                app_name = user_input[6:].strip()

                result = close_app(app_name)

                print(result)


            # ==================================
            # LIST FILES
            # ==================================

            elif user_input.lower().startswith("list "):

                folder = user_input[5:].strip()

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


            # ==================================
            # CREATE FOLDER
            # ==================================

            elif user_input.lower().startswith("mkdir "):

                folder = user_input[6:].strip()

                result = create_folder(folder)

                print(result)


            # ==================================
            # COPY
            # ==================================

            elif user_input.lower().startswith("copy "):

                command = user_input[5:]

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


            # ==================================
            # MOVE
            # ==================================

            elif user_input.lower().startswith("move "):

                command = user_input[5:]

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


            # ==================================
            # SEARCH
            # ==================================

            elif user_input.lower().startswith("search "):

                command = user_input[7:]

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


            # ==================================
            # FILE INFO
            # ==================================

            elif user_input.lower().startswith("info "):

                file_path = user_input[5:].strip()

                result = get_file_info(file_path)

                print(result)


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


            # ==================================
            # RENAME
            # ==================================

            elif user_input.lower().startswith("rename "):

                command = user_input[7:]

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


            # ==================================
            # SHUTDOWN MAC
            # ==================================

            elif user_input.lower() == "shutdown":

                result = execute_command("shutdown")

                if result["success"]:
                    print("\n🔌 Mac is shutting down.")
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