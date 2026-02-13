"""Odoo ERP MCP Server - invoices, payments, accounts via FastMCP + stdio."""
from __future__ import annotations

import os
import xmlrpc.client
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("odoo")


def _connect() -> tuple[int, xmlrpc.client.ServerProxy, str, str]:
    """Authenticate and return (uid, models_proxy, db, password)."""
    url = os.environ.get("ODOO_URL", "http://localhost:8069")
    db = os.environ.get("ODOO_DB", "")
    user = os.environ.get("ODOO_USER", "")
    password = os.environ.get("ODOO_PASSWORD", "")

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, user, password, {})
    if not uid:
        raise ConnectionError("Odoo authentication failed")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    return uid, models, db, password


@mcp.tool()
def search_invoices(
    state: str = "draft",
    partner: str = "",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search invoices in Odoo.

    Args:
        state: Invoice state filter (draft, posted, cancel)
        partner: Partner name filter (partial match)
        limit: Max results
    """
    uid, models, db, pwd = _connect()
    domain = [["move_type", "in", ["out_invoice", "in_invoice"]]]
    if state:
        domain.append(["state", "=", state])
    if partner:
        domain.append(["partner_id.name", "ilike", partner])

    invoices = models.execute_kw(
        db, uid, pwd, "account.move", "search_read",
        [domain],
        {"fields": ["id", "name", "partner_id", "amount_total", "state", "invoice_date", "invoice_date_due"],
         "limit": limit, "order": "invoice_date desc"},
    )
    return [
        {
            "id": inv["id"],
            "number": inv.get("name", ""),
            "partner": inv.get("partner_id", [None, ""])[1] if isinstance(inv.get("partner_id"), list) else "",
            "amount": inv.get("amount_total", 0),
            "state": inv.get("state", ""),
            "date": inv.get("invoice_date", ""),
            "due_date": inv.get("invoice_date_due", ""),
        }
        for inv in invoices
    ]


@mcp.tool()
def create_invoice(
    partner_name: str,
    lines: list[dict[str, Any]],
    invoice_type: str = "out_invoice",
) -> dict[str, Any]:
    """Create an invoice in Odoo.

    Args:
        partner_name: Customer/vendor name
        lines: Invoice line items, each with 'name', 'quantity', 'price_unit'
        invoice_type: 'out_invoice' (customer) or 'in_invoice' (vendor)
    """
    uid, models, db, pwd = _connect()

    # Find or create partner
    partner_ids = models.execute_kw(db, uid, pwd, "res.partner", "search", [[["name", "ilike", partner_name]]])
    if not partner_ids:
        partner_id = models.execute_kw(db, uid, pwd, "res.partner", "create", [{"name": partner_name}])
    else:
        partner_id = partner_ids[0]

    invoice_lines = []
    for line in lines:
        invoice_lines.append((0, 0, {
            "name": line.get("name", "Item"),
            "quantity": line.get("quantity", 1),
            "price_unit": line.get("price_unit", 0),
        }))

    inv_id = models.execute_kw(db, uid, pwd, "account.move", "create", [{
        "move_type": invoice_type,
        "partner_id": partner_id,
        "invoice_line_ids": invoice_lines,
    }])

    return {"status": "created", "invoice_id": inv_id}


@mcp.tool()
def get_account_balance(account_code: str = "") -> dict[str, Any]:
    """Get account balance from Odoo.

    Args:
        account_code: Account code (e.g., '1100' for bank). Empty for all accounts.
    """
    uid, models, db, pwd = _connect()
    domain = []
    if account_code:
        domain.append(["code", "=like", f"{account_code}%"])

    accounts = models.execute_kw(
        db, uid, pwd, "account.account", "search_read",
        [domain],
        {"fields": ["id", "code", "name"], "limit": 20},
    )
    return {"accounts": [{"code": a["code"], "name": a["name"], "id": a["id"]} for a in accounts]}


@mcp.tool()
def record_payment(
    invoice_id: int,
    amount: float,
    payment_method: str = "manual",
) -> dict[str, Any]:
    """Record a payment against an invoice.

    Args:
        invoice_id: Odoo invoice ID
        amount: Payment amount
        payment_method: Payment method identifier
    """
    uid, models, db, pwd = _connect()

    payment_id = models.execute_kw(db, uid, pwd, "account.payment", "create", [{
        "payment_type": "inbound",
        "amount": amount,
        "partner_type": "customer",
    }])

    return {"status": "recorded", "payment_id": payment_id}


@mcp.tool()
def get_transactions(
    date_from: str = "",
    date_to: str = "",
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Get bank transactions from Odoo.

    Args:
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
        limit: Max results
    """
    uid, models, db, pwd = _connect()
    domain: list[Any] = [["is_reconciled", "=", False]]
    if date_from:
        domain.append(["date", ">=", date_from])
    if date_to:
        domain.append(["date", "<=", date_to])

    lines = models.execute_kw(
        db, uid, pwd, "account.bank.statement.line", "search_read",
        [domain],
        {"fields": ["id", "date", "payment_ref", "amount", "partner_name"],
         "limit": limit, "order": "date desc"},
    )
    return [
        {
            "id": l["id"],
            "date": l.get("date", ""),
            "reference": l.get("payment_ref", ""),
            "amount": l.get("amount", 0),
            "partner": l.get("partner_name", ""),
        }
        for l in lines
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")
