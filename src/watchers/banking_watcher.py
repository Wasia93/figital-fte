"""Banking/Odoo transaction watcher - polls for new transactions."""
from __future__ import annotations

import os
import xmlrpc.client
from typing import Any

from src.core.task_item import TaskItem, Priority
from src.core.vault_manager import VaultManager
from src.watchers.base_watcher import BaseWatcher


class BankingWatcher(BaseWatcher):
    """Watches Odoo ERP for new bank transactions."""

    name = "banking_watcher"
    poll_interval = 300  # 5 minutes

    def __init__(self, vault: VaultManager, config: dict[str, Any] | None = None):
        super().__init__(vault, config)
        self.odoo_url = os.environ.get("ODOO_URL", "http://localhost:8069")
        self.odoo_db = os.environ.get("ODOO_DB", "")
        self.odoo_user = os.environ.get("ODOO_USER", "")
        self.odoo_password = os.environ.get("ODOO_PASSWORD", "")
        self._uid: int | None = None

    def _authenticate(self) -> int:
        """Authenticate with Odoo and return user ID."""
        if self._uid is not None:
            return self._uid
        common = xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/common")
        self._uid = common.authenticate(self.odoo_db, self.odoo_user, self.odoo_password, {})
        if not self._uid:
            raise ConnectionError("Failed to authenticate with Odoo")
        return self._uid

    def _get_models(self) -> xmlrpc.client.ServerProxy:
        return xmlrpc.client.ServerProxy(f"{self.odoo_url}/xmlrpc/2/object")

    async def poll(self) -> list[TaskItem]:
        """Poll Odoo for new bank statement lines."""
        if not self.odoo_db or not self.odoo_user:
            self.log.warning("Odoo credentials not configured")
            return []

        try:
            uid = self._authenticate()
            models = self._get_models()

            # Search for unreconciled bank statement lines
            lines = models.execute_kw(
                self.odoo_db, uid, self.odoo_password,
                "account.bank.statement.line", "search_read",
                [[["is_reconciled", "=", False]]],
                {"fields": ["id", "date", "payment_ref", "amount", "partner_name", "narration"],
                 "limit": 50, "order": "date desc"},
            )
        except Exception as e:
            self.log.error(f"Odoo polling error: {e}")
            return []

        items = []
        for line in lines:
            source_id = f"odoo_bsl_{line['id']}"
            if self.is_duplicate(source_id):
                continue

            amount = line.get("amount", 0)
            ref = line.get("payment_ref", "Transaction")
            partner = line.get("partner_name", "Unknown")
            date = line.get("date", "")

            priority = Priority.HIGH if abs(amount) > 10000 else Priority.MEDIUM

            task = TaskItem(
                title=f"Transaction: {ref} ({amount:,.2f})",
                source="Banking",
                source_id=source_id,
                category="Finance",
                priority=priority,
                tags=["transaction", f"partner:{partner}"],
                source_data={
                    "odoo_id": line["id"],
                    "amount": amount,
                    "partner": partner,
                    "date": date,
                    "reference": ref,
                },
                body=(
                    f"**Transaction:** {ref}\n"
                    f"**Amount:** {amount:,.2f}\n"
                    f"**Partner:** {partner}\n"
                    f"**Date:** {date}\n"
                ),
            )
            items.append(task)

        return items

    def get_target_inbox(self) -> str:
        return self.config.get("target_inbox", "Inbox/Banking")
