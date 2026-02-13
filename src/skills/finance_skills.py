"""Finance skills: transaction categorization, invoicing, reconciliation, anomaly detection."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.skill_registry import SkillRegistry


CATEGORY_KEYWORDS = {
    "Software & SaaS": ["aws", "azure", "google cloud", "github", "slack", "notion", "adobe", "microsoft"],
    "Office & Admin": ["office", "supplies", "printing", "postage", "courier"],
    "Travel & Transport": ["airline", "hotel", "uber", "taxi", "fuel", "parking"],
    "Marketing": ["ads", "advertising", "facebook ads", "google ads", "linkedin", "marketing"],
    "Professional Services": ["consulting", "legal", "accounting", "audit", "lawyer"],
    "Utilities": ["electricity", "water", "internet", "phone", "mobile"],
    "Payroll": ["salary", "wages", "payroll", "bonus", "commission"],
    "Revenue": ["payment received", "invoice paid", "client payment", "revenue"],
}


def categorize_transaction(
    description: str = "",
    amount: float = 0.0,
    vendor: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Categorize a financial transaction.

    Returns dict with: category, confidence, is_expense, suggested_account.
    """
    text = f"{description} {vendor}".lower()
    is_expense = amount < 0 or not any(w in text for w in ["received", "income", "revenue", "payment received"])

    category = "Uncategorized"
    confidence = 0.5
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            category = cat
            confidence = 0.8
            break

    return {
        "category": category,
        "confidence": confidence,
        "is_expense": is_expense,
        "suggested_account": "6100 - Operating Expenses" if is_expense else "4000 - Revenue",
        "reasoning": f"Matched keywords for {category}" if confidence > 0.5 else "No keyword match",
    }


def generate_invoice(
    client_name: str = "",
    items: list[dict[str, Any]] | None = None,
    currency: str = "ZAR",
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate an invoice data structure.

    Returns dict with: invoice_number, client, items, total, currency.
    """
    if items is None:
        items = []
    total = sum(item.get("amount", 0) * item.get("quantity", 1) for item in items)
    from datetime import datetime, timezone
    inv_num = f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    return {
        "invoice_number": inv_num,
        "client": client_name,
        "items": items,
        "subtotal": total,
        "tax": round(total * 0.15, 2),  # 15% VAT
        "total": round(total * 1.15, 2),
        "currency": currency,
    }


def reconcile_accounts(
    bank_transactions: list[dict[str, Any]] | None = None,
    book_entries: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Reconcile bank transactions against book entries.

    Returns dict with: matched, unmatched_bank, unmatched_book, discrepancy.
    """
    if bank_transactions is None:
        bank_transactions = []
    if book_entries is None:
        book_entries = []

    matched = []
    unmatched_bank = list(bank_transactions)
    unmatched_book = list(book_entries)

    # Simple amount-based matching
    for bt in bank_transactions[:]:
        for be in book_entries[:]:
            if abs(bt.get("amount", 0) - be.get("amount", 0)) < 0.01:
                matched.append({"bank": bt, "book": be})
                if bt in unmatched_bank:
                    unmatched_bank.remove(bt)
                if be in unmatched_book:
                    unmatched_book.remove(be)
                break

    bank_total = sum(t.get("amount", 0) for t in bank_transactions)
    book_total = sum(e.get("amount", 0) for e in book_entries)

    return {
        "matched_count": len(matched),
        "unmatched_bank_count": len(unmatched_bank),
        "unmatched_book_count": len(unmatched_book),
        "bank_total": bank_total,
        "book_total": book_total,
        "discrepancy": round(bank_total - book_total, 2),
    }


def detect_anomaly(
    transaction: dict[str, Any] | None = None,
    historical_avg: float = 0.0,
    threshold_multiplier: float = 3.0,
    **kwargs: Any,
) -> dict[str, Any]:
    """Detect anomalous transactions based on historical patterns.

    Returns dict with: is_anomaly, reason, severity, amount, average.
    """
    if transaction is None:
        transaction = {}
    amount = abs(transaction.get("amount", 0))
    threshold = abs(historical_avg) * threshold_multiplier

    is_anomaly = amount > threshold if threshold > 0 else False
    severity = "low"
    if is_anomaly:
        ratio = amount / abs(historical_avg) if historical_avg else 0
        severity = "critical" if ratio > 10 else "high" if ratio > 5 else "medium"

    return {
        "is_anomaly": is_anomaly,
        "reason": f"Amount {amount} exceeds {threshold_multiplier}x average ({historical_avg})" if is_anomaly else "Within normal range",
        "severity": severity,
        "amount": amount,
        "average": historical_avg,
    }


def register_skills(registry: SkillRegistry) -> None:
    registry.register("categorize_transaction", categorize_transaction)
    registry.register("generate_invoice", generate_invoice)
    registry.register("reconcile_accounts", reconcile_accounts)
    registry.register("detect_anomaly", detect_anomaly)
