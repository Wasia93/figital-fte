"""Shared test fixtures."""
import pytest
from pathlib import Path
from src.core.vault_manager import VaultManager
from src.core.skill_registry import build_default_registry
from src.core.approval_manager import ApprovalManager


VAULT_DIRS = [
    "Inbox/Email", "Inbox/WhatsApp", "Inbox/Banking", "Inbox/Filesystem",
    "Needs_Action/Email", "Needs_Action/Social", "Needs_Action/Finance", "Needs_Action/General",
    "In_Progress/Email", "In_Progress/Social", "In_Progress/Finance", "In_Progress/General",
    "Needs_Approval", "Approved", "Rejected", "Done", "Logs", "Templates",
]


@pytest.fixture
def vault_path(tmp_path):
    """Create a temp vault with all standard directories."""
    for d in VAULT_DIRS:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture
def vault(vault_path):
    return VaultManager(vault_path)


@pytest.fixture
def skills():
    return build_default_registry()


@pytest.fixture
def approval(vault):
    return ApprovalManager(vault)
