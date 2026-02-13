"""Initialize the vault directory structure for Digital FTE."""
import os
import sys
from pathlib import Path

VAULT_DIRS = [
    "Agents",
    "Inbox/Email",
    "Inbox/WhatsApp",
    "Inbox/Banking",
    "Inbox/Filesystem",
    "Needs_Action/Email",
    "Needs_Action/Social",
    "Needs_Action/Finance",
    "Needs_Action/General",
    "In_Progress/Email",
    "In_Progress/Social",
    "In_Progress/Finance",
    "In_Progress/General",
    "Needs_Approval",
    "Approved",
    "Rejected",
    "Done",
    "Logs",
    "Templates",
]


def setup_vault(vault_path: str | None = None) -> Path:
    """Create the full vault directory tree. Returns the vault root."""
    if vault_path is None:
        vault_path = os.environ.get("VAULT_PATH", str(Path(__file__).resolve().parent.parent / "vault"))
    root = Path(vault_path)
    for d in VAULT_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    # Create .gitkeep in leaf dirs so git tracks them
    for d in VAULT_DIRS:
        gitkeep = root / d / ".gitkeep"
        if not any((root / d).iterdir()):
            gitkeep.touch()
    print(f"Vault initialized at {root}")
    return root


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    setup_vault(path)
