import subprocess


def open_app(app_name: str):
    try:
        subprocess.run(
            ["open", "-a", app_name],
            check=True
        )

        return {
            "success": True,
            "message": f"{app_name} opened successfully."
        }

    except subprocess.CalledProcessError:
        return {
            "success": False,
            "message": f"Could not open {app_name}."
        }


def close_app(app_name: str):
    try:
        subprocess.run(
            ["osascript", "-e", f'quit app "{app_name}"'],
            check=True
        )

        return {
            "success": True,
            "message": f"{app_name} closed successfully."
        }

    except subprocess.CalledProcessError:
        return {
            "success": False,
            "message": f"Could not close {app_name}."
        }