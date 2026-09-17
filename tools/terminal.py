import shlex
import subprocess
from pathlib import Path
from typing import Optional

from security.permissions import request_confirmation


# =========================================================
# DANGEROUS COMMANDS
# =========================================================

DANGEROUS_COMMANDS = {
    "rm",
    "rmdir",
    "sudo",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "kill",
    "pkill",
    "killall",
    "chmod",
    "chown",
    "diskutil",
    "dd",
    "mkfs",
    "format",
}


# =========================================================
# HIGH-RISK INTERPRETERS
# =========================================================

HIGH_RISK_COMMANDS = {
    "python",
    "python3",
    "ruby",
    "perl",
    "php",
    "osascript",
}


# =========================================================
# SHELL OPERATORS
# =========================================================

SHELL_OPERATORS = {
    "|",
    "||",
    "&&",
    ";",
    ">",
    ">>",
    "<",
    "<<",
}


# =========================================================
# APPLICATIONS WE SHOULD NOT QUIT
# =========================================================

PROTECTED_APPS = {
    "Finder",
    "System Events",
}


# =========================================================
# GET EXECUTABLE NAME
# =========================================================

def get_executable_name(command: str) -> str:

    try:

        parts = shlex.split(command)

        if not parts:
            return ""

        return Path(parts[0]).name.lower()

    except ValueError:

        return ""


# =========================================================
# CHECK SHELL OPERATORS
# =========================================================

def contains_shell_operator(command: str) -> bool:

    try:

        parts = shlex.split(command)

    except ValueError:

        return True

    for part in parts:

        if part in SHELL_OPERATORS:
            return True

    return False


# =========================================================
# CHECK DANGEROUS COMMAND
# =========================================================

def is_dangerous_command(command: str) -> bool:

    try:

        parts = shlex.split(command)

        if not parts:
            return False

        executable = Path(parts[0]).name.lower()

        # Direct dangerous command
        if executable in DANGEROUS_COMMANDS:
            return True

        # High-risk interpreters
        if executable in HIGH_RISK_COMMANDS:

            if "-c" in parts:
                return True

            if "--command" in parts:
                return True

        return False

    except ValueError:

        return True


# =========================================================
# CONFIRM DANGEROUS COMMAND
# =========================================================

def confirm_dangerous_command(command: str) -> bool:

    print("\n⚠️ Dangerous Command Detected")
    print("--------------------------------")
    print(f"Command: {command}")
    print("--------------------------------")

    return request_confirmation(
        "execute_command",
        command
    )


# =========================================================
# VALIDATE TIMEOUT
# =========================================================

def validate_timeout(timeout: int) -> int:

    try:

        timeout = int(timeout)

    except (TypeError, ValueError):

        return 30

    if timeout <= 0:
        return 30

    if timeout > 300:
        return 300

    return timeout


# =========================================================
# DISABLE MACOS SESSION RESTORE
# =========================================================

def disable_session_restore():

    try:

        result = subprocess.run(
            [
                "defaults",
                "write",
                "com.apple.loginwindow",
                "TALLogoutSavesState",
                "-bool",
                "false"
            ],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "message": "Session restore command timed out."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }
# ==========================================
# GET RUNNING APPLICATIONS
# ==========================================

def get_running_apps():

    script = '''
    tell application "System Events"

        set appList to {}

        repeat with appProcess in application processes

            try

                if background only of appProcess is false then

                    set appName to name of appProcess

                    if appName is not "Finder" then
                        set end of appList to appName
                    end if

                end if

            end try

        end repeat

        return appList

    end tell
    '''

    try:

        result = subprocess.run(
            [
                "osascript",
                "-e",
                script
            ],
            capture_output=True,
            text=True,
            timeout=20,
            shell=False
        )

        if result.returncode != 0:

            return {
                "success": False,
                "apps": [],
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }

        output = result.stdout.strip()

        if not output:

            return {
                "success": True,
                "apps": []
            }

        apps = [
            app.strip()
            for app in output.split(",")
            if app.strip()
        ]

        return {
            "success": True,
            "apps": apps
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "apps": [],
            "message": (
                "Getting running applications timed out."
            )
        }

    except Exception as e:

        return {
            "success": False,
            "apps": [],
            "message": str(e)
        }

# =========================================================
# CLOSE RUNNING APPLICATIONS
# =========================================================

def close_running_apps():

    print("\n🔄 Checking running applications...")

    running_result = get_running_apps()

    if not running_result["success"]:

        print("\n❌ Could not inspect running applications.")

        if running_result.get("stderr"):
            print("Error:")
            print(running_result["stderr"])

        if running_result.get("message"):
            print(running_result["message"])

        return {
            "success": False,
            "closed_apps": [],
            "failed_apps": [],
            "message": (
                "Unable to inspect running applications."
            )
        }

    running_apps = running_result.get("apps", [])

    if not running_apps:

        print("✅ No normal GUI applications are running.")

        return {
            "success": True,
            "closed_apps": [],
            "failed_apps": []
        }

    print("\nRunning applications:")

    for app in running_apps:

        print(f"  • {app}")

    apps_to_close = []

    for app in running_apps:

        if app in PROTECTED_APPS:
            continue

        apps_to_close.append(app)

    if not apps_to_close:

        print("\n✅ No applications need to be closed.")

        return {
            "success": True,
            "closed_apps": [],
            "failed_apps": []
        }

    print("\n🔄 Asking applications to quit...")

    closed_apps = []
    failed_apps = []

    for app_name in apps_to_close:

        print(f"\n→ Closing: {app_name}")

        script = f'''
        tell application {shlex.quote(app_name)}
            quit
        end tell
        '''

        try:

            result = subprocess.run(
                [
                    "osascript",
                    "-e",
                    script
                ],
                capture_output=True,
                text=True,
                timeout=15,
                shell=False
            )

            if result.returncode == 0:

                print(f"  ✅ Quit request sent: {app_name}")

                closed_apps.append(app_name)

            else:

                error = result.stderr.strip()

                print(f"  ❌ Could not quit: {app_name}")

                if error:
                    print(f"     Error: {error}")

                failed_apps.append({
                    "app": app_name,
                    "error": error
                })

        except subprocess.TimeoutExpired:

            print(f"  ❌ Timeout while closing: {app_name}")

            failed_apps.append({
                "app": app_name,
                "error": "Quit request timed out."
            })

        except Exception as e:

            print(f"  ❌ Error while closing: {app_name}")
            print(f"     {e}")

            failed_apps.append({
                "app": app_name,
                "error": str(e)
            })

    # -----------------------------------------------------
    # Give apps some time to finish quitting
    # -----------------------------------------------------

    print("\n⏳ Waiting for applications to finish quitting...")

    try:

        subprocess.run(
            [
                "sleep",
                "2"
            ],
            timeout=5,
            shell=False
        )

    except Exception:
        pass

    # -----------------------------------------------------
    # Check again
    # -----------------------------------------------------

    final_result = get_running_apps()

    still_running = []

    if final_result["success"]:

        final_apps = final_result.get("apps", [])

        for app in final_apps:

            if app not in PROTECTED_APPS:
                still_running.append(app)

    # -----------------------------------------------------
    # Show result
    # -----------------------------------------------------

    print("\n================================")
    print("Application Closing Result")
    print("================================")

    if closed_apps:

        print("\nClosed / quit requested:")

        for app in closed_apps:

            print(f"  ✅ {app}")

    if failed_apps:

        print("\nFailed to quit:")

        for item in failed_apps:

            print(f"  ❌ {item['app']}")

            if item.get("error"):
                print(f"     {item['error']}")

    if still_running:

        print("\nStill running:")

        for app in still_running:

            print(f"  ⚠️ {app}")

    print("================================")

    # -----------------------------------------------------
    # Important:
    # Do NOT automatically force kill applications.
    # Unsaved data could be lost.
    # -----------------------------------------------------

    return {
        "success": True,
        "closed_apps": closed_apps,
        "failed_apps": failed_apps,
        "still_running": still_running
    }


# =========================================================
# SPECIAL MACOS SHUTDOWN
# =========================================================

def shutdown_mac(timeout: int = 30):

    print("\n⚠️ Mac Shutdown Requested")
    print("================================")
    print("The following actions will be performed:")
    print()
    print("1. Disable normal session restoration")
    print("2. Ask running applications to quit")
    print("3. Shut down macOS")
    print()
    print("Unsaved application data may still require")
    print("the application to respond before quitting.")
    print("================================")

    confirmed = request_confirmation(
        "shutdown",
        "macOS"
    )

    if not confirmed:

        return {
            "success": False,
            "message": "Shutdown cancelled by user."
        }

    # =====================================================
    # STEP 1
    # =====================================================

    print("\n🔧 Disabling session restoration...")

    restore_result = disable_session_restore()

    if restore_result["success"]:

        print("✅ Session restoration setting updated.")

    else:

        print("⚠️ Could not update session restoration setting.")

        if restore_result.get("stderr"):
            print("Error:")
            print(restore_result["stderr"])

        if restore_result.get("message"):
            print(restore_result["message"])

    # =====================================================
    # STEP 2
    # =====================================================

    close_result = close_running_apps()

    if not close_result["success"]:

        print("\n⚠️ Application closing encountered an error.")

        print("\nShutdown can still be requested.")

        continue_shutdown = request_confirmation(
            "continue_shutdown",
            "macOS despite application closing error"
        )

        if not continue_shutdown:

            return {
                "success": False,
                "message": (
                    "Shutdown cancelled because "
                    "applications could not be inspected."
                ),
                "details": close_result
            }

    # =====================================================
    # SHOW APPS STILL RUNNING
    # =====================================================

    still_running = close_result.get(
        "still_running",
        []
    )

    if still_running:

        print("\n⚠️ Some applications are still running:")

        for app in still_running:

            print(f"  • {app}")

        print(
            "\nMac shutdown may ask those applications "
            "to quit as part of the shutdown process."
        )

        continue_shutdown = request_confirmation(
            "continue_shutdown",
            "macOS with applications still running"
        )

        if not continue_shutdown:

            return {
                "success": False,
                "message": (
                    "Shutdown cancelled because "
                    "some applications are still running."
                ),
                "still_running": still_running
            }

    # =====================================================
    # STEP 3
    # ACTUAL SHUTDOWN
    # =====================================================

    print("\n🔌 Starting macOS shutdown...")

    try:

        result = subprocess.run(
            [
                "sudo",
                "shutdown",
                "-h",
                "now"
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "command": "sudo shutdown -h now",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "closed_apps": close_result.get(
                "closed_apps",
                []
            ),
            "failed_apps": close_result.get(
                "failed_apps",
                []
            )
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "message": "Shutdown command timed out."
        }

    except FileNotFoundError:

        return {
            "success": False,
            "message": (
                "sudo or shutdown command "
                "was not found."
            )
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# =========================================================
# SPECIAL MACOS RESTART
# =========================================================

def restart_mac(timeout: int = 30):

    print("\n⚠️ Mac Restart Requested")
    print("================================")
    print("The following actions will be performed:")
    print()
    print("1. Disable normal session restoration")
    print("2. Ask running applications to quit")
    print("3. Restart macOS")
    print("================================")

    confirmed = request_confirmation(
        "reboot",
        "macOS"
    )

    if not confirmed:

        return {
            "success": False,
            "message": "Restart cancelled by user."
        }

    # =====================================================
    # STEP 1
    # =====================================================

    print("\n🔧 Disabling session restoration...")

    restore_result = disable_session_restore()

    if restore_result["success"]:

        print("✅ Session restoration setting updated.")

    else:

        print("⚠️ Could not update session restoration setting.")

        if restore_result.get("stderr"):
            print(restore_result["stderr"])

    # =====================================================
    # STEP 2
    # =====================================================

    close_result = close_running_apps()

    if not close_result["success"]:

        print("\n⚠️ Could not inspect applications.")

        continue_restart = request_confirmation(
            "continue_restart",
            "macOS despite application closing error"
        )

        if not continue_restart:

            return {
                "success": False,
                "message": "Restart cancelled by user.",
                "details": close_result
            }

    # =====================================================
    # STILL RUNNING
    # =====================================================

    still_running = close_result.get(
        "still_running",
        []
    )

    if still_running:

        print("\n⚠️ Some applications are still running:")

        for app in still_running:

            print(f"  • {app}")

        continue_restart = request_confirmation(
            "continue_restart",
            "macOS with applications still running"
        )

        if not continue_restart:

            return {
                "success": False,
                "message": (
                    "Restart cancelled because "
                    "some applications are still running."
                ),
                "still_running": still_running
            }

    # =====================================================
    # STEP 3
    # ACTUAL RESTART
    # =====================================================

    print("\n🔄 Starting macOS restart...")

    try:

        result = subprocess.run(
            [
                "sudo",
                "shutdown",
                "-r",
                "now"
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "command": "sudo shutdown -r now",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "closed_apps": close_result.get(
                "closed_apps",
                []
            ),
            "failed_apps": close_result.get(
                "failed_apps",
                []
            )
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "message": "Restart command timed out."
        }

    except FileNotFoundError:

        return {
            "success": False,
            "message": (
                "sudo or shutdown command "
                "was not found."
            )
        }
    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# EXECUTE TERMINAL COMMAND
# ==========================================

def execute_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout: int = 30
):

    # ======================================
    # VALIDATE COMMAND
    # ======================================

    if not command or not command.strip():

        return {
            "success": False,
            "message": "Command cannot be empty."
        }

    command = command.strip()

    # ======================================
    # VALIDATE TIMEOUT
    # ======================================

    timeout = validate_timeout(
        timeout
    )

    # ======================================
    # PARSE COMMAND
    # ======================================

    try:

        parts = shlex.split(
            command
        )

    except ValueError as e:

        return {
            "success": False,
            "message": (
                f"Invalid command syntax: {e}"
            )
        }

    if not parts:

        return {
            "success": False,
            "message": "Command cannot be empty."
        }

    # ======================================
    # GET EXECUTABLE
    # ======================================

    executable = parts[0]

    executable_name = Path(
        executable
    ).name.lower()

    # ======================================
    # SPECIAL SHUTDOWN
    # ======================================

    if executable_name == "shutdown":

        return shutdown_mac(
            timeout
        )

    # ======================================
    # SPECIAL RESTART
    # ======================================

    if executable_name in {
        "reboot",
        "poweroff",
        "halt"
    }:

        return restart_mac(
            timeout
        )

    # ======================================
    # SHELL OPERATORS
    # ======================================

    if contains_shell_operator(
        command
    ):

        return {
            "success": False,
            "message": (
                "Shell operators such as "
                "|, &&, ;, > and < "
                "are not supported in this version."
            )
        }

    # ======================================
    # DANGEROUS COMMAND CONFIRMATION
    # ======================================

    if is_dangerous_command(
        command
    ):

        confirmed = confirm_dangerous_command(
            command
        )

        if not confirmed:

            return {
                "success": False,
                "message": (
                    "Dangerous command was "
                    "cancelled by the user."
                )
            }

    # ======================================
    # WORKING DIRECTORY
    # ======================================

    cwd = None

    if working_directory:

        cwd_path = Path(
            working_directory
        ).expanduser()

        try:

            cwd_path = cwd_path.resolve()

        except Exception as e:

            return {
                "success": False,
                "message": (
                    f"Invalid working directory: {e}"
                )
            }

        if not cwd_path.exists():

            return {
                "success": False,
                "message": (
                    "Working directory "
                    "does not exist."
                )
            }

        if not cwd_path.is_dir():

            return {
                "success": False,
                "message": (
                    "Working directory "
                    "is not a folder."
                )
            }

        cwd = str(
            cwd_path
        )

    # ======================================
    # EXECUTE COMMAND
    # ======================================

    try:

        result = subprocess.run(
            parts,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )

        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "command": command,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }

    # ======================================
    # COMMAND NOT FOUND
    # ======================================

    except FileNotFoundError:

        return {
            "success": False,
            "return_code": 127,
            "command": command,
            "stdout": "",
            "stderr": (
                f"Command not found: "
                f"{executable_name}"
            )
        }

    # ======================================
    # TIMEOUT
    # ======================================

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "command": command,
            "message": (
                f"Command timed out after "
                f"{timeout} seconds."
            )
        }

    # ======================================
    # PERMISSION ERROR
    # ======================================

    except PermissionError:

        return {
            "success": False,
            "command": command,
            "message": "Permission denied."
        }

    # ======================================
    # UNEXPECTED ERROR
    # ======================================

    except Exception as e:

        return {
            "success": False,
            "command": command,
            "message": str(e)
        }