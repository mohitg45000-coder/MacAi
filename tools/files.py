from pathlib import Path
import shutil

from security.permissions import authorize_operation


# ==========================================
# 1. LIST FILES
# ==========================================

def list_files(folder_path: str):

    path = Path(folder_path).expanduser()

    if not path.exists():
        return {
            "success": False,
            "message": "Folder does not exist."
        }

    if not path.is_dir():
        return {
            "success": False,
            "message": "Path is not a folder."
        }

    try:

        items = []

        for item in path.iterdir():

            items.append({
                "name": item.name,
                "type": "folder" if item.is_dir() else "file",
                "path": str(item)
            })

        return {
            "success": True,
            "path": str(path),
            "items": items
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# 2. CREATE FOLDER
# ==========================================

def create_folder(folder_path: str):

    path = Path(folder_path).expanduser()

    # Security check

    if not authorize_operation(
        "create_folder",
        str(path)
    ):
        return {
            "success": False,
            "message": "Folder creation is not allowed for this path."
        }

    try:

        path.mkdir(
            parents=True,
            exist_ok=True
        )

        return {
            "success": True,
            "message": f"Folder created successfully: {path}"
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# 3. COPY FILE
# ==========================================

def copy_file(
    source: str,
    destination: str
):

    source_path = Path(source).expanduser()
    destination_path = Path(destination).expanduser()

    # Source validation

    if not source_path.exists():

        return {
            "success": False,
            "message": "Source file does not exist."
        }

    if not source_path.is_file():

        return {
            "success": False,
            "message": "Source is not a file."
        }

    # Security check for source

    if not authorize_operation(
        "copy",
        str(source_path)
    ):

        return {
            "success": False,
            "message": "Copy operation is not allowed for this path."
        }

    # Security check for destination

    if not authorize_operation(
        "copy",
        str(destination_path)
    ):

        return {
            "success": False,
            "message": "Destination path is not allowed."
        }

    try:

        shutil.copy2(
            source_path,
            destination_path
        )

        return {
            "success": True,
            "message": f"File copied to: {destination_path}"
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# 4. MOVE FILE
# ==========================================

def move_file(
    source: str,
    destination: str
):

    source_path = Path(source).expanduser()
    destination_path = Path(destination).expanduser()

    # Source validation

    if not source_path.exists():

        return {
            "success": False,
            "message": "Source file does not exist."
        }

    if not source_path.is_file():

        return {
            "success": False,
            "message": "Source is not a file."
        }

    # Security check - SOURCE

    if not authorize_operation(
        "move",
        str(source_path)
    ):

        return {
            "success": False,
            "message": "Move operation is not allowed for the source path."
        }

    # Security check - DESTINATION

    if not authorize_operation(
        "move",
        str(destination_path)
    ):

        return {
            "success": False,
            "message": "Move operation is not allowed for the destination path."
        }

    try:

        shutil.move(
            str(source_path),
            str(destination_path)
        )

        return {
            "success": True,
            "message": f"File moved to: {destination_path}"
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# 5. SEARCH FILES
# ==========================================

def search_files(
    folder_path: str,
    keyword: str
):

    path = Path(folder_path).expanduser()

    if not path.exists():

        return {
            "success": False,
            "message": "Folder does not exist."
        }

    if not path.is_dir():

        return {
            "success": False,
            "message": "Path is not a folder."
        }

    if not keyword.strip():

        return {
            "success": False,
            "message": "Search keyword cannot be empty."
        }

    # Security check

    if not authorize_operation(
        "search",
        str(path)
    ):

        return {
            "success": False,
            "message": "Search operation is not allowed for this path."
        }

    results = []

    try:

        for item in path.rglob("*"):

            if keyword.lower() in item.name.lower():

                results.append({
                    "name": item.name,
                    "path": str(item),
                    "type": (
                        "folder"
                        if item.is_dir()
                        else "file"
                    )
                })

        return {
            "success": True,
            "keyword": keyword,
            "results": results
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied while searching."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# 6. GET FILE INFORMATION
# ==========================================

def get_file_info(file_path: str):

    path = Path(file_path).expanduser()

    if not path.exists():

        return {
            "success": False,
            "message": "File or folder does not exist."
        }

    # Security check

    if not authorize_operation(
        "info",
        str(path)
    ):

        return {
            "success": False,
            "message": "Access to this path is not allowed."
        }

    try:

        stats = path.stat()

        file_type = (
            "folder"
            if path.is_dir()
            else "file"
        )

        return {
            "success": True,
            "name": path.name,
            "path": str(path),
            "type": file_type,
            "size_bytes": stats.st_size,
            "created": stats.st_birthtime,
            "modified": stats.st_mtime
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# 7. READ TEXT FILE
# ==========================================

def read_text_file(file_path: str):

    path = Path(file_path).expanduser()

    if not path.exists():

        return {
            "success": False,
            "message": "File does not exist."
        }

    if not path.is_file():

        return {
            "success": False,
            "message": "Path is not a file."
        }

    # Security check

    if not authorize_operation(
        "read",
        str(path)
    ):

        return {
            "success": False,
            "message": "Reading this file is not allowed."
        }

    try:

        content = path.read_text(
            encoding="utf-8"
        )

        return {
            "success": True,
            "path": str(path),
            "content": content
        }

    except UnicodeDecodeError:

        return {
            "success": False,
            "message": "This file is not a UTF-8 text file."
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }


# ==========================================
# 8. RENAME FILE / FOLDER
# ==========================================

def rename_file(
    file_path: str,
    new_name: str
):

    path = Path(file_path).expanduser()

    if not path.exists():

        return {
            "success": False,
            "message": "File or folder does not exist."
        }

    if not new_name.strip():

        return {
            "success": False,
            "message": "New name cannot be empty."
        }

    # Prevent path traversal / subdirectories
    # from being passed as a new name.

    if Path(new_name).name != new_name:

        return {
            "success": False,
            "message": "New name must contain only a file or folder name."
        }

    new_path = path.parent / new_name

    if new_path.exists():

        return {
            "success": False,
            "message": "A file or folder with that name already exists."
        }

    # Security check

    if not authorize_operation(
        "rename",
        str(path)
    ):

        return {
            "success": False,
            "message": "Rename operation is not allowed for this path."
        }

    try:

        path.rename(new_path)

        return {
            "success": True,
            "old_path": str(path),
            "new_path": str(new_path),
            "message": f"Renamed successfully to: {new_name}"
        }

    except PermissionError:

        return {
            "success": False,
            "message": "Permission denied."
        }

    except Exception as e:

        return {
            "success": False,
            "message": str(e)
        }




    