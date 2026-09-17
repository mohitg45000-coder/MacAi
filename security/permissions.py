from pathlib import Path


# ==========================================
# ALLOWED DIRECTORIES
# ==========================================

ALLOWED_DIRECTORIES = [
    Path.home() / "Desktop",
    Path.home() / "Documents",
    Path.home() / "Downloads",
]


# ==========================================
# DANGEROUS OPERATIONS
# ==========================================

DANGEROUS_OPERATIONS = {
    "delete",
    "execute_command",
    "move",
    "rename",
}


# ==========================================
# RESOLVE PATH
# ==========================================

def resolve_path(path: str) -> Path:
    """
    Convert a user path such as ~/Desktop
    into an absolute normalized Path.
    """

    return Path(path).expanduser().resolve()


# ==========================================
# CHECK ALLOWED PATH
# ==========================================

def is_path_allowed(path: str) -> bool:

    target = resolve_path(path)

    for allowed_directory in ALLOWED_DIRECTORIES:

        allowed = allowed_directory.resolve()

        try:

            target.relative_to(allowed)

            return True

        except ValueError:

            continue

    return False


# ==========================================
# CHECK OPERATION
# ==========================================

def is_operation_allowed(
    operation: str,
    path: str
) -> bool:

    operation = operation.lower().strip()

    # Path must always be inside
    # an allowed directory.

    if not is_path_allowed(path):

        return False

    # Dangerous operations require
    # additional confirmation.

    if operation in DANGEROUS_OPERATIONS:

        return False

    return True


# ==========================================
# ASK USER CONFIRMATION
# ==========================================

def request_confirmation(
    operation: str,
    path: str
) -> bool:

    print("\n⚠️ Permission Required")

    print(f"Operation : {operation}")
    print(f"Path      : {path}")

    answer = input(
        "Allow this operation? (yes/no): "
    ).strip().lower()

    return answer in {
        "yes",
        "y"
    }


# ==========================================
# SECURE OPERATION CHECK
# ==========================================

def authorize_operation(
    operation: str,
    path: str
) -> bool:

    # First check path.

    if not is_path_allowed(path):

        print(
            "\n❌ Access denied."
        )

        print(
            "Path is outside the allowed directories."
        )

        return False


    # Safe operations can continue.

    if operation not in DANGEROUS_OPERATIONS:

        return True


    # Dangerous operations require
    # explicit user confirmation.

    return request_confirmation(
        operation,
        path
    )